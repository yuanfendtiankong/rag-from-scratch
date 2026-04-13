# 导入 Path，用来读取本地文件
from pathlib import Path


def load_text(file_path: str) -> str:
    """
    读取本地文本文件，返回完整字符串
    :param file_path: 文件路径
    :return: 文件内容
    """
    return Path(file_path).read_text(encoding="utf-8")


def simple_split_text(text: str, chunk_size: int = 100, chunk_overlap: int = 20):
    """
    一个简化版的文本切分函数。
    按固定长度切分长文本，并保留相邻块之间的重叠部分。

    :param text: 原始长文本
    :param chunk_size: 每个 chunk 的最大长度
    :param chunk_overlap: 相邻 chunk 之间重复保留的长度
    :return: 切分后的字符串列表
    """

    # 用来存放最终切分出的所有 chunk
    chunks = []

    # 当前切分起点
    start = 0

    # 文本总长度
    text_length = len(text)

    # 如果 overlap 不合理，提前报错，避免死循环
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size，否则会进入死循环。")

    # 循环切分，直到 start 超过文本长度
    while start < text_length:
        # 当前 chunk 的结束位置
        end = start + chunk_size

        # 从原文中截取这一段
        chunk = text[start:end]

        # 去掉首尾多余空白，然后加入结果
        chunks.append(chunk.strip())

        # 下一轮的起点：
        # 不直接跳到 end，而是减去 overlap，保留一部分重复内容
        start = end - chunk_overlap

    return chunks


if __name__ == "__main__":
    # 读取测试文本
    text = load_text("data/raw/knowledge.txt")

    # 先用一组默认参数做切分
    chunks = simple_split_text(text, chunk_size=80, chunk_overlap=30)

    # 打印一共切分出了多少块
    print(f"一共切分出 {len(chunks)} 个 chunks\n")

    # 逐个打印每个 chunk
    for i, chunk in enumerate(chunks):
        print(f"===== chunk {i + 1} =====")
        print(chunk)
        print()