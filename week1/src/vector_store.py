import json


def save_chunks_to_json(chunks, output_path: str):
    """
    把切分后的 chunks 保存到本地 json 文件中

    :param chunks: 文本块列表
    :param output_path: 输出文件路径
    """
    data = []

    for i, chunk in enumerate(chunks):
        data.append({
            "chunk_id": i + 1,
            "text": chunk
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_chunks(json_path: str):
    """
    从本地 json 文件中读取 chunks

    :param json_path: chunks.json 的路径
    :return: chunk 列表
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
