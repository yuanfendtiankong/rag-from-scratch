from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    PROCESSED_CHUNKS_PATH,
    RAW_KNOWLEDGE_PATH,
)
from pipeline import build_and_save_chunks


if __name__ == "__main__":
    chunks = build_and_save_chunks(
        source_path=RAW_KNOWLEDGE_PATH,
        output_path=PROCESSED_CHUNKS_PATH,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )

    print("已生成 {0} 个 chunks，并保存到 {1}".format(len(chunks), PROCESSED_CHUNKS_PATH))
