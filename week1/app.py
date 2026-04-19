from pathlib import Path
import sys


# app.py 放在项目根目录，而核心代码都在 src/ 目录下。
# 为了让这个入口文件能直接复用 src 里的现有模块，
# 这里先把 src 路径加入 Python 的导入搜索路径。
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from pipeline import answer_query, answer_query_with_newapi


def choose_mode():
    """
    让用户选择回答模式。

    返回:
        str: "1" 表示规则版回答，"2" 表示 New API 版回答。
    """
    print("请选择运行模式：")
    print("1. 规则版 RAG")
    print("2. New API 版 RAG（失败时会自动回退到规则版）")

    while True:
        choice = input("\n请输入 1 或 2：").strip()
        if choice in {"1", "2"}:
            return choice
        print("输入无效，请重新输入 1 或 2。")


def print_results(answer_title, answer, top_results):
    """
    统一打印最终回答和参考 chunks。

    这样做的好处是：
    1. 规则版和 New API 版可以复用同一套输出格式
    2. app.py 只负责“交互和展示”，不负责核心问答逻辑
    """
    print("\n===== {0} =====\n".format(answer_title))
    print(answer)

    print("\n===== 参考 chunks =====\n")
    if not top_results:
        print("没有检索到相关 chunks。")
        return

    for item in top_results:
        # 现在检索分数是 0 到 1 之间的小数，保留 3 位更容易观察。
        print("chunk_id = {0} | score = {1:.3f}".format(item["chunk_id"], item["score"]))
        print(item["text"])
        print()


def main():
    """
    项目统一入口。

    当前这个函数只做三件事：
    1. 让用户选择运行模式
    2. 接收用户问题
    3. 调用 pipeline 中已经写好的函数并展示结果

    也就是说，app.py 更像“前台”，
    而真正的检索、生成、回退逻辑依然在 src/ 里。
    """
    print("欢迎使用 week1 RAG 学习项目。")
    mode = choose_mode()

    query = input("\n请输入你的问题：").strip()
    if not query:
        print("问题不能为空。")
        return

    if mode == "1":
        answer, top_results = answer_query(query)
        print_results("最终回答（规则版）", answer, top_results)
    else:
        answer, top_results = answer_query_with_newapi(query)
        print_results("最终回答（New API 版）", answer, top_results)


if __name__ == "__main__":
    main()
