from config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, RAW_KNOWLEDGE_PATH
from pipeline import preview_chunks


if __name__ == "__main__":
    chunks = preview_chunks(
        source_path=RAW_KNOWLEDGE_PATH,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )

    print("一共切分出 {0} 个 chunks\n".format(len(chunks)))

    for index, chunk in enumerate(chunks, start=1):
        print("===== chunk {0} =====".format(index))
        print(chunk)
        print()
