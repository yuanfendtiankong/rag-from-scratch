def simple_split_text(text, chunk_size=100, chunk_overlap=20):
    """
    按固定窗口切分长文本，并保留相邻块之间的重叠内容。

    这是一个适合入门阶段理解 RAG 思路的简化版切分函数。

    参数:
        text: 待切分的原始文本。
        chunk_size: 每个文本块的最大长度。
        chunk_overlap: 相邻文本块之间保留的重叠长度。

    返回:
        list[str]: 切分后的文本块列表。
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0。")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap 不能为负数。")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size，否则切分窗口无法向前推进。")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - chunk_overlap

    return chunks
