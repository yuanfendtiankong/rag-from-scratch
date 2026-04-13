# 导入 json，用来把切分后的 chunks 保存为本地 json 文件
import json

# 从 Day 2 的文件里导入已经写好的两个函数：
# 1. load_text：读取文本
# 2. simple_split_text：切分文本
from load_and_split import load_text, simple_split_text


def save_chunks_to_json(chunks, output_path: str):
    """
    把切分后的 chunks 保存到本地 json 文件中

    :param chunks: 文本块列表
    :param output_path: 输出文件路径
    """
    # 为了后续检索更方便，这里把每个 chunk 包装成一个字典
    data = []

    for i, chunk in enumerate(chunks):
        data.append({
            "chunk_id": i + 1,
            "text": chunk
        })

    # ensure_ascii=False 可以保证中文正常写入
    # indent=2 是为了让 json 文件更容易阅读
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 读取原始知识文本
    text = load_text("data/raw/knowledge.txt")

    # 继续使用你在 Day 2 学到的切分参数
    chunks = simple_split_text(text, chunk_size=100, chunk_overlap=20)

    # 保存到本地 json 文件
    save_chunks_to_json(chunks, "data/processed/chunks.json")

    print(f"成功保存 {len(chunks)} 个 chunks 到 data/processed/chunks.json")