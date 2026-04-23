import numpy as np

from config import DEFAULT_EMBEDDING_MODE, DEFAULT_MIN_CHUNK_NORMALIZED_LENGTH
from embedder import embed_text, normalize_text


def jaccard_similarity(left_embedding, right_embedding):
    """
    计算两个 embedding 集合的 Jaccard 相似度。

    公式:
        交集大小 / 并集大小

    为什么比“只看交集个数”更合理：
    1. 分数会被归一化到 0 到 1 之间
    2. 不会因为某个 chunk 更长、包含更多字符片段，就天然更占优势
    3. 更适合比较不同长度文本之间的相似程度
    """
    union = left_embedding | right_embedding
    if not union:
        return 0.0

    overlap = left_embedding & right_embedding
    return len(overlap) / len(union)


def query_coverage(query_embedding, chunk_embedding):
    """
    计算“query 被 chunk 覆盖了多少”。

    公式:
        交集大小 / query embedding 大小

    这个指标特别适合当前项目这种场景：
    用户问题通常很短，而 chunk 往往更长。
    如果只用 Jaccard，长 chunk 容易因为并集过大而被压分；
    加入 query coverage 之后，我们能更关注：
    “问题里的关键信息，有多少真的在这个 chunk 里出现了？”
    """
    if not query_embedding:
        return 0.0

    overlap = query_embedding & chunk_embedding
    return len(overlap) / len(query_embedding)


def cosine_similarity(left_embedding, right_embedding):
    """
    计算两个向量之间的余弦相似度。

    这是做向量检索时最常见的相似度之一。
    你可以把它简单理解成：
    “两个向量在方向上有多接近”。

    分数越接近 1，说明越相似；
    越接近 0，说明越不相似。
    """
    left_norm = (left_embedding ** 2).sum() ** 0.5
    right_norm = (right_embedding ** 2).sum() ** 0.5

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return float((left_embedding @ right_embedding) / (left_norm * right_norm))


def is_meaningful_chunk(chunk_text, min_normalized_length=DEFAULT_MIN_CHUNK_NORMALIZED_LENGTH):
    """
    判断一个 chunk 是否值得进入检索候选。

    这里主要是过滤掉像“。”、“，”这类几乎没有信息量的极短残片。
    对真实 embedding 检索来说，这类残片有时会因为向量异常而被排到前面，
    反而破坏最终结果。
    """
    normalized_text = normalize_text(chunk_text)
    return len(normalized_text) >= min_normalized_length


def score_bigram_embeddings(query_embedding, chunk_embedding):
    """
    计算当前项目中 lexical baseline 的分数。

    这个函数本质上就是原来 bigram 检索的核心打分方式。
    单独拆出来之后，我们就可以在真实 embedding 检索时复用它，
    做一个简单的 hybrid retrieval。
    """
    coverage_score = query_coverage(query_embedding, chunk_embedding)
    jaccard_score = jaccard_similarity(query_embedding, chunk_embedding)
    return 0.7 * coverage_score + 0.3 * jaccard_score


def score_embeddings(query_embedding, chunk_embedding, embedding_mode=DEFAULT_EMBEDDING_MODE):
    """
    直接比较已经计算好的 query / chunk 表示。

    把“文本编码”和“相似度计算”拆开后，一个检索请求里就可以只编码一次 query，
    避免在遍历所有 chunks 时反复重复做同样的工作。
    """
    if embedding_mode == "bigram":
        return score_bigram_embeddings(query_embedding, chunk_embedding)

    if embedding_mode == "sentence_transformer":
        return cosine_similarity(query_embedding, chunk_embedding)

    raise ValueError("不支持的 embedding 模式: {0}".format(embedding_mode))


def score_chunk(query, chunk_text, embedding_mode=DEFAULT_EMBEDDING_MODE):
    """
    计算查询文本与单个文本块之间的相关分数。

    当前支持两套打分方式：
    1. bigram 模式：
       - 使用 query coverage + Jaccard 的混合分数
       - 适合教学和观察
    2. sentence_transformer 模式：
       - 使用真实向量的余弦相似度
       - 更接近正式的向量检索

    参数:
        query: 用户问题。
        chunk_text: 单个文本块内容。

    返回:
        float: 分数范围在 0 到 1 之间，越高说明相关性越强。
    """
    query_embedding = embed_text(query, mode=embedding_mode)
    chunk_embedding = embed_text(chunk_text, mode=embedding_mode)
    return score_embeddings(query_embedding, chunk_embedding, embedding_mode=embedding_mode)


def retrieve_top_k(
    query,
    chunks,
    k=3,
    embedding_mode=DEFAULT_EMBEDDING_MODE,
    chunk_embeddings=None,
):
    """
    从全部文本块中选出与问题最相关的前 k 个结果。

    参数:
        query: 用户问题。
        chunks: 文本块列表。
        k: 返回结果数量。
        chunk_embeddings: 预计算好的 chunk 向量缓存。

    返回:
        list[dict]: 按分数从高到低排序后的检索结果。
    """
    scored_results = []
    query_embedding = embed_text(query, mode=embedding_mode)
    query_bigram_embedding = None
    chunk_embedding_map = None

    # 当上层已经准备好了 chunk 向量缓存时，这里会优先直接使用缓存，
    # 避免对每个 chunk 再重复编码一次 sentence-transformer 向量。
    if isinstance(chunk_embeddings, list):
        chunk_embedding_map = {
            item["chunk_id"]: np.array(item["embedding"], dtype=float)
            for item in chunk_embeddings
        }

    if embedding_mode == "sentence_transformer":
        # 真实 embedding 负责语义相似，
        # 但对短 query 来说，适当保留一点 lexical 信号会更稳。
        query_bigram_embedding = embed_text(query, mode="bigram")

    for item in chunks:
        chunk_text = item["text"]

        if not is_meaningful_chunk(chunk_text):
            continue

        if chunk_embedding_map is not None and item["chunk_id"] in chunk_embedding_map:
            chunk_embedding = chunk_embedding_map[item["chunk_id"]]
        else:
            chunk_embedding = embed_text(chunk_text, mode=embedding_mode)

        score = score_embeddings(query_embedding, chunk_embedding, embedding_mode=embedding_mode)

        if embedding_mode == "sentence_transformer":
            chunk_bigram_embedding = embed_text(chunk_text, mode="bigram")
            lexical_score = score_bigram_embeddings(query_bigram_embedding, chunk_bigram_embedding)

            # 这里采用轻量 hybrid retrieval：
            # dense score 负责语义相似，
            # lexical score 负责关键词对齐。
            # 对像“RAG是什么？”这样短而明确的问题，这种组合通常比只用 dense 更稳。
            score = 0.8 * score + 0.2 * lexical_score

        scored_results.append({
            "chunk_id": item["chunk_id"],
            "text": chunk_text,
            "score": score
        })

    scored_results.sort(key=lambda item: item["score"], reverse=True)

    filtered_results = []
    for item in scored_results:
        if item["score"] > 0:
            filtered_results.append(item)

    return filtered_results[:k]
