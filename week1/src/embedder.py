def text_to_bigrams(text):
    """
    将文本转换为二元字符片段集合。

    当前项目没有接入真正的向量模型，因此用 bigram 集合作为
    一个便于理解的“简化 embedding 表示”。

    参数:
        text: 输入文本。

    返回:
        set[str]: 文本对应的 bigram 集合。
    """
    cleaned_text = text.strip()

    if len(cleaned_text) < 2:
        return set(cleaned_text)

    bigrams = set()
    for index in range(len(cleaned_text) - 1):
        bigrams.add(cleaned_text[index:index + 2])

    return bigrams


def embed_text(text):
    """
    返回当前项目使用的文本表示。

    这里保留 bigram 方案不变，方便你继续观察“检索”这一步是如何工作的。
    """
    return text_to_bigrams(text)
