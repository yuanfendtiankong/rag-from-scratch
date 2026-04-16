# 导入 re，用来按句号、问号、感叹号等切分句子
import re

# 从 retrieve.py 中导入已经写好的函数
# 1. load_chunks：读取保存好的 chunks
# 2. retrieve_top_k：检索最相关的 top-k 个 chunk
# 3. score_chunk：计算 query 和文本的相关性分数
from retrieve import load_chunks, retrieve_top_k, score_chunk


def split_into_sentences(text: str):
    """
    把一段文本粗略切分成句子

    :param text: 输入文本
    :return: 句子列表
    """
    # 按中文句号、问号、感叹号、分号、换行进行切分
    sentences = re.split(r"[。！？；\n]", text)

    # 去掉空字符串和首尾空白
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

    # 遍历每个检索到的 chunk
    for item in top_chunks:
        chunk_id = item["chunk_id"]
        chunk_text = item["text"]

        # 先把 chunk 切成句子
        sentences = split_into_sentences(chunk_text)

        # 对每个句子计算和 query 的相关性
        for sentence in sentences:
            score = score_chunk(query, sentence)

            candidate_sentences.append({
                "chunk_id": chunk_id,
                "sentence": sentence,
                "score": score
            })

    # 按分数从高到低排序
    candidate_sentences.sort(key=lambda x: x["score"], reverse=True)

    # 返回前 max_sentences 个句子
    return candidate_sentences[:max_sentences]


def generate_answer(query: str, top_chunks):
    """
    根据检索到的 top chunks 生成一个格式更清晰的回答

    :param query: 用户问题
    :param top_chunks: 检索出的相关 chunks
    :return: 最终回答字符串
    """
    # 从 top chunks 中挑选最相关的句子
    best_sentences = select_best_sentences(query, top_chunks, max_sentences=3)

    # 如果没有找到有效句子，就直接返回提示信息
    if not best_sentences or best_sentences[0]["score"] == 0:
        return "回答：\n我无法从当前资料中找到足够相关的内容来回答这个问题。"

    # 用来保存去重后的句子
    answer_sentences = []
    used_sentences = set()

    for item in best_sentences:
        sentence = item["sentence"]

        # 去重，避免重复句子影响可读性
        if sentence not in used_sentences:
            used_sentences.add(sentence)
            answer_sentences.append(sentence)

    # 如果去重后没有句子，也给出提示
    if not answer_sentences:
        return "回答：\n我无法从当前资料中找到足够相关的内容来回答这个问题。"

    # 第一部分：核心回答
    main_answer = answer_sentences[0]

    # 第二部分：依据说明
    evidence_lines = []
    for i, sentence in enumerate(answer_sentences, start=1):
        evidence_lines.append(f"{i}. {sentence}")

    evidence_text = "\n".join(evidence_lines)

    # 第三部分：总结
    summary = "以上回答基于当前知识库中的相关文本片段整理得到。"

    # 拼成一个更清晰的回答格式
    final_answer = (
        f"回答：\n{main_answer}\n\n"
        f"依据：\n{evidence_text}\n\n"
        f"总结：\n{summary}"
    )

    return final_answer


if __name__ == "__main__":
    # 读取已经保存好的 chunks
    chunks = load_chunks("data/processed/chunks.json")

    # 让用户输入问题
    query = input("请输入你的问题：").strip()

    # 先检索最相关的 3 个 chunks
    top_results = retrieve_top_k(query, chunks, k=3)

    # 再根据 top chunks 生成回答
    answer = generate_answer(query, top_results)

    # 打印格式化后的最终回答
    print("\n===== 最终回答 =====\n")
    print(answer)

    # 打印参考依据，方便理解程序到底参考了哪些 chunk
    print("\n===== 参考 chunks =====\n")
    if not top_results:
        print("没有检索到相关 chunks。")
    else:
        for item in top_results:
            print(f"chunk_id = {item['chunk_id']} | score = {item['score']}")
            print(item["text"])
            print()