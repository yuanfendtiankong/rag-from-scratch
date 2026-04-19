from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
WEEK1_DIR = SRC_DIR.parent
DATA_DIR = WEEK1_DIR / "data"
MODELS_DIR = WEEK1_DIR / "models"

RAW_KNOWLEDGE_PATH = DATA_DIR / "raw" / "knowledge.txt"
PROCESSED_CHUNKS_PATH = DATA_DIR / "processed" / "chunks.json"
PROCESSED_EMBEDDINGS_PATH = DATA_DIR / "processed" / "chunk_embeddings.json"

DEFAULT_CHUNK_SIZE = 100
DEFAULT_CHUNK_OVERLAP = 20
DEFAULT_RETRIEVE_TOP_K = 3
DEFAULT_NEWAPI_TOP_K = 5
DEFAULT_MIN_CHUNK_NORMALIZED_LENGTH = 5

# 当前项目支持两种 embedding 模式：
# 1. bigram：教学版、零依赖、便于观察检索过程
# 2. sentence_transformer：真实向量 embedding，后续 Day 7 会继续接入
#
# 当前 Day 7 已经把 sentence-transformers 模型手动下载到本地，
# 因此这里切换成真实 embedding 作为默认模式。
DEFAULT_EMBEDDING_MODE = "sentence_transformer"
DEFAULT_SENTENCE_TRANSFORMER_MODEL = MODELS_DIR / "paraphrase-multilingual-MiniLM-L12-v2"
