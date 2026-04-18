from generator import generate_answer_with_newapi
from retriever import retrieve_top_k
from vector_store import load_chunks


if __name__ == "__main__":
    chunks = load_chunks("data/processed/chunks.json")
    query = input("请输入你的问题：").strip()
    top_results = retrieve_top_k(query, chunks, k=5)
    answer = generate_answer_with_newapi(query, top_results)

    print("\n===== 最终回答（New API 生成）====\n")
    print(answer)

    print("\n===== 参考 chunks =====\n")
    if not top_results:
        print("没有检索到相关 chunks。")
    else:
        for item in top_results:
            print(f"chunk_id = {item['chunk_id']} | score = {item['score']}")
            print(item["text"])
            print()
