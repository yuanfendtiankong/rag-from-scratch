import os
import re

from retriever import score_chunk


NO_ANSWER_TEXT = "我无法从当前资料中找到足够相关的内容来回答这个问题。"


def split_into_sentences(text):
    """
    按中文常见标点将文本粗略切分为句子列表。

    参数:
        text: 原始文本。

    返回:
        list[str]: 去除空白后的句子列表。
    """
    sentences = re.split(r"[。！？；\n]", text)

    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            cleaned_sentences.append(sentence)

    return cleaned_sentences


def select_best_sentences(query, top_chunks, max_sentences=3):
    """
    在已检索到的文本块中挑选最相关的句子，作为最终回答依据。

    参数:
        query: 用户问题。
        top_chunks: 检索得到的文本块列表。
        max_sentences: 最多返回多少个候选句子。

    返回:
        list[dict]: 包含 chunk_id、sentence、score 的候选句子列表。
    """
    candidate_sentences = []

    for item in top_chunks:
        chunk_id = item["chunk_id"]
        chunk_text = item["text"]
        chunk_score = item["score"]
        sentences = split_into_sentences(chunk_text)

        for sentence in sentences:
            sentence_score = score_chunk(query, sentence)

            # 在真实 embedding 检索下，句子级语义分数有时会把一些泛化句顶上来。
            # 这里把“句子本身的相关性”和“所属 chunk 的整体相关性”结合起来，
            # 让最终回答更稳定地贴近 top retrieval 结果。
            score = 0.7 * sentence_score + 0.3 * chunk_score
            candidate_sentences.append({
                "chunk_id": chunk_id,
                "sentence": sentence,
                "score": score
            })

    candidate_sentences.sort(key=lambda item: item["score"], reverse=True)
    return candidate_sentences[:max_sentences]


def generate_answer(query, top_chunks):
    """
    根据检索结果生成一个结构清晰的规则式回答。

    参数:
        query: 用户问题。
        top_chunks: 检索阶段返回的相关文本块。

    返回:
        str: 包含回答、依据和总结的最终字符串。
    """
    best_sentences = select_best_sentences(query, top_chunks, max_sentences=3)

    if not best_sentences or best_sentences[0]["score"] == 0:
        return "回答：\n{0}".format(NO_ANSWER_TEXT)

    # 主回答优先从 top1 chunk 中挑选。
    # 这样可以让最终答案更贴近检索阶段的主结果，避免被后续 chunk 中的泛化句抢走。
    top1_chunk_sentences = select_best_sentences(query, top_chunks[:1], max_sentences=1)

    answer_sentences = []
    used_sentences = set()

    if top1_chunk_sentences:
        top1_sentence = top1_chunk_sentences[0]["sentence"]
        used_sentences.add(top1_sentence)
        answer_sentences.append({
            "chunk_id": top1_chunk_sentences[0]["chunk_id"],
            "sentence": top1_sentence,
        })

    for item in best_sentences:
        sentence = item["sentence"]
        if sentence not in used_sentences:
            used_sentences.add(sentence)
            # 这里不仅保留句子内容，也保留它来自哪个 chunk。
            # 这样后面生成“依据”时就能直接标注来源，让回答更像一个可解释的 RAG 结果。
            answer_sentences.append({
                "chunk_id": item["chunk_id"],
                "sentence": sentence,
            })

    if not answer_sentences:
        return "回答：\n{0}".format(NO_ANSWER_TEXT)

    main_answer = answer_sentences[0]["sentence"]
    evidence_lines = []
    cited_chunk_ids = []

    for index, item in enumerate(answer_sentences, start=1):
        chunk_id = item["chunk_id"]
        sentence = item["sentence"]
        evidence_lines.append(
            "{0}. [chunk {1}] {2}".format(index, chunk_id, sentence)
        )
        if chunk_id not in cited_chunk_ids:
            cited_chunk_ids.append(chunk_id)

    evidence_text = "\n".join(evidence_lines)
    cited_chunks_text = "、".join("chunk {0}".format(chunk_id) for chunk_id in cited_chunk_ids)
    summary = "以上回答基于当前知识库中的相关文本片段整理得到，主要参考了 {0}。".format(
        cited_chunks_text
    )

    final_answer = (
        "回答：\n{0}\n\n"
        "依据：\n{1}\n\n"
        "总结：\n{2}"
    ).format(main_answer, evidence_text, summary)
    return final_answer


def build_context(top_chunks):
    """
    将检索结果拼接为上下文文本，供大模型参考。

    参数:
        top_chunks: 检索到的文本块列表。

    返回:
        str: 拼接后的上下文内容。
    """
    context_parts = []

    for item in top_chunks:
        chunk_id = item["chunk_id"]
        chunk_text = item["text"]
        context_parts.append("[chunk {0}]\n{1}".format(chunk_id, chunk_text))

    return "\n\n".join(context_parts)


def should_refuse(top_chunks, min_top1_score=0.05, min_total_score=0.12):
    """
    根据检索分数判断当前资料是否足以支撑回答。

    参数:
        top_chunks: 检索到的文本块列表。
        min_top1_score: top1 结果允许回答的最低分。
        min_total_score: 全部结果允许回答的最低总分。

    返回:
        bool: True 表示应该拒答，False 表示可以继续生成回答。
    """
    if not top_chunks:
        return True

    top1_score = top_chunks[0]["score"]
    total_score = 0
    for item in top_chunks:
        total_score += item["score"]

    if top1_score < min_top1_score:
        return True

    if total_score < min_total_score:
        return True

    return False


def generate_answer_with_newapi(query, top_chunks):
    """
    使用兼容 OpenAI 接口的 New API 生成最终回答。

    参数:
        query: 用户问题。
        top_chunks: 检索到的相关文本块。

    返回:
        str: 模型生成的回答文本。
    """
    # 这里的阈值要和 retriever 中新的相似度分数体系保持一致。
    # 现在 score 是 0 到 1 之间的小数，而不是之前的整数交集计数。
    if should_refuse(top_chunks, min_top1_score=0.05, min_total_score=0.12):
        return NO_ANSWER_TEXT

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()

    context = build_context(top_chunks)
    prompt = """
你是一个问答助手。请严格根据下面提供的资料回答问题。
请使用纯文本回答，不要使用 Markdown 格式，不要使用加粗符号。
如果资料中没有足够信息，请明确回答：
“我无法从当前资料中确定答案。”

资料：
{context}

问题：
{query}

请给出：
1. 简洁回答
2. 如果可以，补一句依据说明
""".strip().format(context=context, query=query)

    client = OpenAI(
        api_key=os.getenv("NEWAPI_API_KEY"),
        base_url=os.getenv("NEWAPI_BASE_URL")
    )

    model_name = os.getenv("NEWAPI_MODEL", "gpt-5.2")

    try:
        # 这里只包住真正的接口调用阶段。
        # 这样依赖缺失或前置配置问题仍会直接暴露出来，便于学习和排查。
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格基于给定资料回答问题的助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as exc:
        fallback_answer = generate_answer(query, top_chunks)
        fallback_notice = (
            "提示：New API 调用失败，本次已回退到本地规则版回答。\n"
            "失败原因：{0}\n\n"
        ).format(exc)
        return fallback_notice + fallback_answer
