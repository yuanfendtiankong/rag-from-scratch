from retriever import retrieve_top_k, score_chunk
from vector_store import load_chunks


if __name__ == "__main__":
    chunks = load_chunks("data/processed/chunks.json")
    query = input("请输入你的问题：").strip()
    top_results = retrieve_top_k(query, chunks, k=3)

    print("\n最相关的 chunks 如下：\n")

    for item in top_results:
        print(f"===== chunk {item['chunk_id']} | score = {item['score']} =====")
        print(item["text"])
        print()
