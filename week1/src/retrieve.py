# 导入 json，用来读取前面保存好的 chunks 文件
import json


def load_chunks(json_path: str):
    """
    从本地 json 文件中读取 chunks

    :param json_path: chunks.json 的路径
    :return: chunk 列表
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def text_to_bigrams(text: str):
    """
    把文本转换成 2 字符片段集合（bigram）
    这样做是为了在中文场景下，简单模拟“相似度”

    例如：
    'RAG是什么'
    -> {'RA', 'AG', 'G是', '是什', '什么'}

    :param text: 输入文本
    :return: bigram 集合
    """
    # 去掉首尾空白
    text = text.strip()

    # 如果文本长度小于 2，就直接返回单字符集合
    if len(text) < 2:
        return set(text)

    # 构造连续的 2 字符片段
    bigrams = set()
    for i in range(len(text) - 1):
        bigrams.add(text[i:i + 2])

    return bigrams


def score_chunk(query: str, chunk_text: str):
    """
    计算 query 和某个 chunk 的简单相关性分数

    这里使用：
    1. query 的 bigram 集合
    2. chunk 的 bigram 集合
    3. 取交集大小作为分数

    :param query: 用户问题
    :param chunk_text: 某个 chunk 的文本
    :return: 分数，分数越大表示越相关
    """
    query_bigrams = text_to_bigrams(query)
    chunk_bigrams = text_to_bigrams(chunk_text)

    # 交集越大，说明两者共享的字符片段越多
    overlap = query_bigrams & chunk_bigrams

    return len(overlap)


def retrieve_top_k(query: str, chunks, k: int = 3):
    """
    从所有 chunks 中找出与 query 最相关的 top-k 个

    :param query: 用户输入的问题
    :param chunks: chunk 列表
    :param k: 返回前 k 个结果
    :return: 按分数从高到低排序后的结果
    """
    scored_results = []

    for item in chunks:
        score = score_chunk(query, item["text"])

        scored_results.append({
            "chunk_id": item["chunk_id"],
            "text": item["text"],
            "score": score
        })

    # 按 score 从高到低排序
    scored_results.sort(key=lambda x: x["score"], reverse=True)

    # 返回前 k 个结果
    return scored_results[:k]


if __name__ == "__main__":
    # 读取保存好的 chunks
    chunks = load_chunks("data/processed/chunks.json")

    # 让用户输入问题
    query = input("请输入你的问题：").strip()

    # 检索最相关的 3 个 chunk
    top_results = retrieve_top_k(query, chunks, k=3)

    print("\n最相关的 chunks 如下：\n")

    for item in top_results:
        print(f"===== chunk {item['chunk_id']} | score = {item['score']} =====")
        print(item["text"])
        print()