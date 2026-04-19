import re

from config import DEFAULT_EMBEDDING_MODE, DEFAULT_SENTENCE_TRANSFORMER_MODEL


def normalize_text(text):
    """
    对输入文本做最基础的规范化处理。

    这里不追求复杂的 NLP 预处理，只做两件简单但很实用的事：
    1. 统一转成小写，减少大小写带来的无意义差异
    2. 去掉空白和常见标点，让 embedding 更关注真正的内容字符

    这一步很适合教学，因为它能帮助你观察：
    “文本表示”不只是切 bigram，还包括切之前如何清洗文本。
    """
    lowered_text = text.lower()
    return re.sub(r"[\s\W_]+", "", lowered_text)


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
    cleaned_text = normalize_text(text)

    if len(cleaned_text) < 2:
        return set(cleaned_text)

    bigrams = set()
    for index in range(len(cleaned_text) - 1):
        bigrams.add(cleaned_text[index:index + 2])

    return bigrams


_SENTENCE_TRANSFORMER_MODEL = None


def get_sentence_transformer_model(model_name=DEFAULT_SENTENCE_TRANSFORMER_MODEL):
    """
    懒加载 sentence-transformers 模型。

    为什么这里要“懒加载”：
    1. 当前项目默认还是 bigram 模式，不应该一启动就强行加载大模型依赖
    2. 只有真正切换到 sentence_transformer 模式时，才需要导入并初始化模型
    3. 这样能让 Day 7 的升级更平滑，不会破坏你现在已有的运行方式
    """
    global _SENTENCE_TRANSFORMER_MODEL

    if _SENTENCE_TRANSFORMER_MODEL is not None:
        return _SENTENCE_TRANSFORMER_MODEL

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "当前 embedding 模式是 sentence_transformer，但尚未安装 sentence-transformers。"
        ) from exc

    try:
        # SentenceTransformer 既支持 Hugging Face 仓库名，也支持本地目录路径。
        # 当前 Day 7 默认优先走本地模型目录，避免运行时再次联网拉取文件。
        _SENTENCE_TRANSFORMER_MODEL = SentenceTransformer(str(model_name))
    except Exception as exc:
        raise RuntimeError(
            "sentence-transformers 模型暂时无法完成加载。"
            "这通常表示本地模型目录不完整，或者模型文件路径配置不正确。"
            "请检查 models/paraphrase-multilingual-MiniLM-L12-v2 目录中的文件是否齐全。"
        ) from exc

    return _SENTENCE_TRANSFORMER_MODEL


def text_to_sentence_embedding(text, model_name=DEFAULT_SENTENCE_TRANSFORMER_MODEL):
    """
    将文本编码成真正的稠密向量。

    返回值会是一个数字向量，而不是像 bigram 模式那样的字符串集合。
    这也是后面做“向量相似度检索”的基础。
    """
    model = get_sentence_transformer_model(model_name=model_name)
    # convert_to_numpy=True 可以让后续余弦相似度计算更直接。
    return model.encode(text, convert_to_numpy=True)


def embed_text(text, mode=DEFAULT_EMBEDDING_MODE):
    """
    返回当前项目使用的文本表示。

    mode 可以理解成“我们想用哪一种方式表示文本”：
    1. bigram：返回 set[str]
    2. sentence_transformer：返回向量

    这一步很重要，因为它把“表示层”单独抽了出来。
    后面无论你换什么检索方法，第一步都还是先决定：
    “文本要先被表示成什么？”
    """
    if mode == "bigram":
        return text_to_bigrams(text)

    if mode == "sentence_transformer":
        return text_to_sentence_embedding(text)

    raise ValueError("不支持的 embedding 模式: {0}".format(mode))
