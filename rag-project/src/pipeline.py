from chunker import simple_split_text
from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_MODE,
    DEFAULT_NEWAPI_TOP_K,
    DEFAULT_RETRIEVE_TOP_K,
    PROCESSED_EMBEDDINGS_PATH,
    PROCESSED_CHUNKS_PATH,
    RAW_KNOWLEDGE_PATH,
)
from embedder import embed_text
from generator import generate_answer, generate_answer_with_newapi
from loader import load_text
from retriever import retrieve_top_k
from vector_store import (
    load_chunk_embeddings,
    load_chunks,
    save_chunk_embeddings_to_json,
    save_chunks_to_json,
)


def build_and_save_chunks(
    source_path=RAW_KNOWLEDGE_PATH,
    output_path=PROCESSED_CHUNKS_PATH,
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """
    从原始知识库文本构建文本块，并保存到本地 JSON 文件。

    返回:
        list[dict]: 保存后的文本块列表。
    """
    text = load_text(source_path)
    chunks = simple_split_text(
        text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    save_chunks_to_json(chunks, output_path)
    return load_chunks(output_path)


def preview_chunks(
    source_path=RAW_KNOWLEDGE_PATH,
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """
    仅构建文本块并返回结果，不写入文件，适合调试切分效果。
    """
    text = load_text(source_path)
    return simple_split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def load_saved_chunks(chunks_path=PROCESSED_CHUNKS_PATH):
    """
    加载已经落盘保存的文本块数据。
    """
    return load_chunks(chunks_path)


def build_and_save_chunk_embeddings(
    chunks_path=PROCESSED_CHUNKS_PATH,
    output_path=PROCESSED_EMBEDDINGS_PATH,
    embedding_mode=DEFAULT_EMBEDDING_MODE,
):
    """
    为已经保存好的 chunks 预计算向量，并缓存到本地 JSON。

    当前这个函数主要服务于 sentence_transformer 模式。
    这样后续检索时就不需要对每个 chunk 反复重复编码。
    """
    chunks = load_saved_chunks(chunks_path=chunks_path)
    embedding_records = []

    for item in chunks:
        chunk_id = item["chunk_id"]
        text = item["text"]
        embedding = embed_text(text, mode=embedding_mode)

        embedding_records.append({
            "chunk_id": chunk_id,
            "embedding": embedding.tolist(),
        })

    save_chunk_embeddings_to_json(embedding_records, output_path)
    return load_chunk_embeddings(output_path)


def load_saved_chunk_embeddings(embeddings_path=PROCESSED_EMBEDDINGS_PATH):
    """
    加载已经保存好的 chunk 向量缓存。
    """
    return load_chunk_embeddings(embeddings_path)


def search_chunks(
    query,
    k=DEFAULT_RETRIEVE_TOP_K,
    chunks_path=PROCESSED_CHUNKS_PATH,
    embeddings_path=PROCESSED_EMBEDDINGS_PATH,
    embedding_mode=DEFAULT_EMBEDDING_MODE,
):
    """
    执行一次完整的检索流程。
    """
    chunks = load_saved_chunks(chunks_path)
    chunk_embeddings = None

    if embedding_mode == "sentence_transformer":
        try:
            chunk_embeddings = load_saved_chunk_embeddings(embeddings_path=embeddings_path)
        except FileNotFoundError:
            # 第一次运行时如果还没有缓存，就自动构建一份。
            chunk_embeddings = build_and_save_chunk_embeddings(
                chunks_path=chunks_path,
                output_path=embeddings_path,
                embedding_mode=embedding_mode,
            )

    return retrieve_top_k(
        query,
        chunks,
        k=k,
        embedding_mode=embedding_mode,
        chunk_embeddings=chunk_embeddings,
    )


def answer_query(query, k=DEFAULT_RETRIEVE_TOP_K, chunks_path=PROCESSED_CHUNKS_PATH):
    """
    使用规则式生成器回答问题。

    返回:
        tuple[str, list[dict]]: 最终回答与检索结果。
    """
    top_results = search_chunks(query, k=k, chunks_path=chunks_path)
    answer = generate_answer(query, top_results)
    return answer, top_results


def answer_query_with_newapi(
    query,
    k=DEFAULT_NEWAPI_TOP_K,
    chunks_path=PROCESSED_CHUNKS_PATH,
):
    """
    使用 New API 版本的生成器回答问题。

    返回:
        tuple[str, list[dict]]: 最终回答与检索结果。
    """
    top_results = search_chunks(query, k=k, chunks_path=chunks_path)
    answer = generate_answer_with_newapi(query, top_results)
    return answer, top_results
