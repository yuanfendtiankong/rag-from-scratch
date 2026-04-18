from embedder import embed_text


def score_chunk(query: str, chunk_text: str):
    """
    计算 query 和某个 chunk 的简化相关性分数。

    :param query: 用户问题
    :param chunk_text: 某个 chunk 的文本
    :return: 分数，分数越大表示越相关
    """
    query_embedding = embed_text(query)
    chunk_embedding = embed_text(chunk_text)
    overlap = query_embedding & chunk_embedding
    return len(overlap)


def retrieve_top_k(query: str, chunks, k: int = 3):
    """
    从所有 chunks 中找出与 query 最相关的 top-k 个。

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

    scored_results.sort(key=lambda x: x["score"], reverse=True)

    filtered_results = []
    for item in scored_results:
        if item["score"] > 0:
            filtered_results.append(item)

    return filtered_results[:k]
