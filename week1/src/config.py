from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
WEEK1_DIR = SRC_DIR.parent
DATA_DIR = WEEK1_DIR / "data"

RAW_KNOWLEDGE_PATH = DATA_DIR / "raw" / "knowledge.txt"
PROCESSED_CHUNKS_PATH = DATA_DIR / "processed" / "chunks.json"

DEFAULT_CHUNK_SIZE = 100
DEFAULT_CHUNK_OVERLAP = 20
DEFAULT_RETRIEVE_TOP_K = 3
DEFAULT_NEWAPI_TOP_K = 5
