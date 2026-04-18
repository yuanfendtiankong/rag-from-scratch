import os
import re

from retriever import score_chunk


def split_into_sentences(text: str):
    """
    把一段文本粗略切成句子

    :param text: 输入文本
    :return: 句子列表
    """
    sentences = re.split(r"[。！？；\n]", text)

    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            cleaned_sentences.append(sentence)

    return cleaned_sentences


def select_best_sentences(query: str, top_chunks, max_sentences: int = 3):
    """
    从检索到的 top chunks 中，进一步挑选最相关的句子

    :param query: 用户问题
    :param top_chunks: 已检索出的 top-k chunks
    :param max_sentences: 最多保留多少句
    :return: 最相关句子的列表
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

    candidate_sentences.sort(key=lambda x: x["score"], reverse=True)
    return candidate_sentences[:max_sentences]


def generate_answer(query: str, top_chunks):
    """
    根据检索到的 top chunks 生成一个格式更清晰的回答

    :param query: 用户问题
    :param top_chunks: 检索出的相关 chunks
    :return: 最终回答字符串
    """
    best_sentences = select_best_sentences(query, top_chunks, max_sentences=3)

    if not best_sentences or best_sentences[0]["score"] == 0:
        return "回答：\n我无法从当前资料中找到足够相关的内容来回答这个问题。"

    answer_sentences = []
    used_sentences = set()

    for item in best_sentences:
        sentence = item["sentence"]
        if sentence not in used_sentences:
            used_sentences.add(sentence)
            answer_sentences.append(sentence)

    if not answer_sentences:
        return "回答：\n我无法从当前资料中找到足够相关的内容来回答这个问题。"

    main_answer = answer_sentences[0]
    evidence_lines = []
    for i, sentence in enumerate(answer_sentences, start=1):
        evidence_lines.append(f"{i}. {sentence}")

    evidence_text = "\n".join(evidence_lines)
    summary = "以上回答基于当前知识库中的相关文本片段整理得到。"

    final_answer = (
        f"回答：\n{main_answer}\n\n"
        f"依据：\n{evidence_text}\n\n"
        f"总结：\n{summary}"
    )
    return final_answer


def build_context(top_chunks):
    """
    把检索到的 top-k chunks 拼接成上下文，供模型使用

    :param top_chunks: 检索结果列表
    :return: 拼接后的上下文字符串
    """
    context_parts = []

    for item in top_chunks:
        chunk_id = item["chunk_id"]
        chunk_text = item["text"]
        context_parts.append(f"[chunk {chunk_id}]\n{chunk_text}")

    return "\n\n".join(context_parts)


def should_refuse(top_chunks, min_top1_score: int = 2, min_total_score: int = 4):
    """
    根据检索结果判断是否应该拒答

    :param top_chunks: 检索到的 chunks
    :param min_top1_score: top1 的最低分阈值
    :param min_total_score: top-k 总分的最低阈值
    :return: True 表示应该拒答，False 表示可以继续生成
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


def generate_answer_with_newapi(query: str, top_chunks):
    """
    使用 New API 的 OpenAI 兼容接口生成回答

    :param query: 用户问题
    :param top_chunks: 检索到的相关 chunks
    :return: 模型生成的回答
    """
    if should_refuse(top_chunks, min_top1_score=2, min_total_score=4):
        return "我无法从当前资料中找到足够相关的内容来回答这个问题。"

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()

    context = build_context(top_chunks)

    prompt = f"""
你是一个问答助手。
请严格根据下面提供的资料回答问题。
请使用纯文本回答，不要使用 Markdown 格式，不要使用 ** 加粗符号。
如果资料中没有足够信息，请明确回答：
“我无法从当前资料中确定答案。”

资料：
{context}

问题：
{query}

请给出：
1. 简洁回答
2. 如果可以，补一句依据说明
""".strip()

    client = OpenAI(
        api_key=os.getenv("NEWAPI_API_KEY"),
        base_url=os.getenv("NEWAPI_BASE_URL")
    )

    model_name = os.getenv("NEWAPI_MODEL", "gpt-5.2")

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
