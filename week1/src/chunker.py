def simple_split_text(text: str, chunk_size: int = 100, chunk_overlap: int = 20):
    """
    一个简化版的文本切分函数。
    按固定长度切分长文本，并保留相邻块之间的重叠部分。

    :param text: 原始长文本
    :param chunk_size: 每个 chunk 的最大长度
    :param chunk_overlap: 相邻 chunk 之间重复保留的长度
    :return: 切分后的字符串列表
    """
    chunks = []
    start = 0
    text_length = len(text)

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size，否则会进入死循环。")

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - chunk_overlap

    return chunks
