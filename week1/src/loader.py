from pathlib import Path


def load_text(file_path: str) -> str:
    """
    读取本地文本文件，返回完整字符串
    :param file_path: 文件路径
    :return: 文件内容
    """
    return Path(file_path).read_text(encoding="utf-8")
