from config import DEFAULT_RETRIEVE_TOP_K
from pipeline import search_chunks


if __name__ == "__main__":
    query = input("请输入你的问题：").strip()
    top_results = search_chunks(query, k=DEFAULT_RETRIEVE_TOP_K)

    print("\n最相关的 chunks 如下：\n")

    for item in top_results:
        print("===== chunk {0} | score = {1} =====".format(item["chunk_id"], item["score"]))
        print(item["text"])
        print()
