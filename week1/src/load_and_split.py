"""

RAG 流水线中的「加载」步骤：从磁盘读取 UTF-8 文本。

"""



from pathlib import Path





def load_text(file_path: str) -> str:

    """

    读取整个文本文件为字符串。



    使用 pathlib.Path 而不是 open()，便于跨平台路径处理，且 API 简洁。

    encoding="utf-8" 显式指定编码，避免在 Windows 上默认编码导致中文乱码。

    """

    return Path(file_path).read_text(encoding="utf-8")





if __name__ == "__main__":

    # 从项目根目录运行时，相对路径 data/raw/... 才正确（当前工作目录需为仓库根）

    text = load_text("week1/data/raw/knowledge.txt")

    print(text)

