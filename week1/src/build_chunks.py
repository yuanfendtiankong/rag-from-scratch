from loader import load_text
from chunker import simple_split_text
from vector_store import save_chunks_to_json


if __name__ == "__main__":
    text = load_text("data/raw/knowledge.txt")
    chunks = simple_split_text(text, chunk_size=100, chunk_overlap=20)
    save_chunks_to_json(chunks, "data/processed/chunks.json")

    print(f"成功保存 {len(chunks)} 个 chunks 到 data/processed/chunks.json")
