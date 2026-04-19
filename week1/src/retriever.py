from embedder import embed_text


def score_chunk(query, chunk_text):
    """
    计算查询文本与单个文本块之间的相关分数。

    当前分数定义为 query bigram 集合与 chunk bigram 集合的交集大小。

    参数:
        query: 用户问题。
        chunk_text: 单个文本块内容。

    返回:
        int: 分数越高，说明相关性越强。
    """
    query_embedding = embed_text(query)
    chunk_embedding = embed_text(chunk_text)
    overlap = query_embedding & chunk_embedding
    return len(overlap)


def retrieve_top_k(query, chunks, k=3):
    """
    从全部文本块中选出与问题最相关的前 k 个结果。

    参数:
        query: 用户问题。
        chunks: 文本块列表。
        k: 返回结果数量。

    返回:
        list[dict]: 按分数从高到低排序后的检索结果。
    """
    scored_results = []

    for item in chunks:
        score = score_chunk(query, item["text"])
        scored_results.append({
            "chunk_id": item["chunk_id"],
            "text": item["text"],
            "score": score
        })

    scored_results.sort(key=lambda item: item["score"], reverse=True)

    filtered_results = []
    for item in scored_results:
        if item["score"] > 0:
            filtered_results.append(item)

    return filtered_results[:k]
