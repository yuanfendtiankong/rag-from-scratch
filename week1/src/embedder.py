def text_to_bigrams(text: str):
    """
    把文本转换成 2 字符片段集合（bigram）。
    这里保留当前项目的简化“嵌入”方式，不改变现有行为。

    :param text: 输入文本
    :return: bigram 集合
    """
    text = text.strip()

    if len(text) < 2:
        return set(text)

    bigrams = set()
    for i in range(len(text) - 1):
        bigrams.add(text[i:i + 2])

    return bigrams


def embed_text(text: str):
    """
    返回当前项目使用的文本表示。
    目前仍然是 bigram 集合，用于保持检索行为不变。
    """
    return text_to_bigrams(text)
