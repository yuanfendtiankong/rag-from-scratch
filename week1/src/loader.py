from pathlib import Path


def load_text(file_path):
    """
    读取本地文本文件并返回完整内容。

    参数:
        file_path: 目标文本文件路径，可以是相对路径或绝对路径。

    返回:
        str: 文件中的完整文本内容。
    """
    return Path(file_path).read_text(encoding="utf-8")
