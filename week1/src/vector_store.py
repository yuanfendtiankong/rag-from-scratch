import json
from pathlib import Path


def save_chunks_to_json(chunks, output_path):
    """
    将文本块保存为 JSON 文件，便于后续检索阶段直接加载。

    参数:
        chunks: 文本块列表。
        output_path: 输出文件路径。
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = []
    for index, chunk in enumerate(chunks, start=1):
        data.append({
            "chunk_id": index,
            "text": chunk
        })

    output_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_chunks(json_path):
    """
    从本地 JSON 文件读取文本块数据。

    参数:
        json_path: 文本块 JSON 文件路径。

    返回:
        list[dict]: 每一项至少包含 chunk_id 和 text 字段。
    """
    return json.loads(Path(json_path).read_text(encoding="utf-8"))
