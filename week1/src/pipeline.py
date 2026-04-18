from chunker import simple_split_text
from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_NEWAPI_TOP_K,
    DEFAULT_RETRIEVE_TOP_K,
    PROCESSED_CHUNKS_PATH,
    RAW_KNOWLEDGE_PATH,
)
from generator import generate_answer, generate_answer_with_newapi
from loader import load_text
from retriever import retrieve_top_k
from vector_store import load_chunks, save_chunks_to_json


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


def search_chunks(query, k=DEFAULT_RETRIEVE_TOP_K, chunks_path=PROCESSED_CHUNKS_PATH):
    """
    执行一次完整的检索流程。
    """
    chunks = load_saved_chunks(chunks_path)
    return retrieve_top_k(query, chunks, k=k)


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
