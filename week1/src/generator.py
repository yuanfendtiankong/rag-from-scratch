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
        sentences = split_into_sentences(chunk_text)

        for sentence in sentences:
            score = score_chunk(query, sentence)
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

    answer_sentences = []
    used_sentences = set()

    for item in best_sentences:
        sentence = item["sentence"]
        if sentence not in used_sentences:
            used_sentences.add(sentence)
            answer_sentences.append(sentence)

    if not answer_sentences:
        return "回答：\n{0}".format(NO_ANSWER_TEXT)

    main_answer = answer_sentences[0]
    evidence_lines = []

    for index, sentence in enumerate(answer_sentences, start=1):
        evidence_lines.append("{0}. {1}".format(index, sentence))

    evidence_text = "\n".join(evidence_lines)
    summary = "以上回答基于当前知识库中的相关文本片段整理得到。"

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


def should_refuse(top_chunks, min_top1_score=2, min_total_score=4):
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
    if should_refuse(top_chunks, min_top1_score=2, min_total_score=4):
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
