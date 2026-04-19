from pipeline import answer_query_with_newapi


if __name__ == "__main__":
    query = input("请输入你的问题：").strip()
    answer, top_results = answer_query_with_newapi(query)

    print("\n===== 最终回答（New API 生成） =====\n")
    print(answer)

    print("\n===== 参考 chunks =====\n")
    if not top_results:
        print("没有检索到相关 chunks。")
    else:
        for item in top_results:
            print("chunk_id = {0} | score = {1:.3f}".format(item["chunk_id"], item["score"]))
            print(item["text"])
            print()
