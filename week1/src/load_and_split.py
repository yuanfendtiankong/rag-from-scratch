from loader import load_text
from chunker import simple_split_text


if __name__ == "__main__":
    text = load_text("data/raw/knowledge.txt")
    chunks = simple_split_text(text, chunk_size=80, chunk_overlap=30)

    print(f"一共切分出 {len(chunks)} 个 chunks\n")

    for i, chunk in enumerate(chunks):
        print(f"===== chunk {i + 1} =====")
        print(chunk)
        print()
