# 导入 os，用来读取环境变量
import os

# 导入 dotenv，用来加载 .env 文件
from dotenv import load_dotenv

# 导入 OpenAI 官方 Python SDK
# 这里虽然名字叫 OpenAI，但也可以连接 OpenAI 兼容接口
from openai import OpenAI

# 复用你已经写好的检索逻辑
from retrieve import load_chunks, retrieve_top_k


# 加载项目根目录中的 .env
load_dotenv()


def build_context(top_chunks):
    """
    把检索到的 top-k chunks 拼接成上下文，供模型使用

    :param top_chunks: 检索结果列表
    :return: 拼接后的上下文字符串
    """
    context_parts = []

    for item in top_chunks:
        chunk_id = item["chunk_id"]
        chunk_text = item["text"]

        # 给每个 chunk 加编号，方便模型理解来源
        context_parts.append(f"[chunk {chunk_id}]\n{chunk_text}")

    return "\n\n".join(context_parts)

def should_refuse(top_chunks, min_top1_score: int = 2, min_total_score: int = 4):
    """
    根据检索结果判断是否应该拒答

    :param top_chunks: 检索到的 chunks
    :param min_top1_score: top1 的最低分阈值
    :param min_total_score: top-k 总分的最低阈值
    :return: True 表示应该拒答，False 表示可以继续生成
    """
    # 如果一个结果都没有，直接拒答
    if not top_chunks:
        return True

    # 取最高分
    top1_score = top_chunks[0]["score"]

    # 计算 top-k 的总分
    total_score = 0
    for item in top_chunks:
        total_score += item["score"]

    # 如果最高分过低，说明最相关的 chunk 都不够相关
    if top1_score < min_top1_score:
        return True

    # 如果总分过低，说明整体检索结果都比较弱
    if total_score < min_total_score:
        return True

    # 否则认为可以继续生成
    return False

def generate_answer_with_newapi(query: str, top_chunks):
    """
    使用 New API 的 OpenAI 兼容接口生成回答

    :param query: 用户问题
    :param top_chunks: 检索到的相关 chunks
    :return: 模型生成的回答
    """
    # 如果没有检索到任何相关内容，或者检索结果整体太弱，就直接拒答
    if should_refuse(top_chunks, min_top1_score=2, min_total_score=4):
        return "我无法从当前资料中找到足够相关的内容来回答这个问题。"

    # 拼接上下文
    context = build_context(top_chunks)

    # 构造提示词
    prompt = f"""
你是一个问答助手。
请严格根据下面提供的资料回答问题。
请使用纯文本回答，不要使用 Markdown 格式，不要使用 ** 加粗符号。
如果资料中没有足够信息，请明确回答：
“我无法从当前资料中确定答案。”

资料：
{context}

问题：
{query}

请给出：
1. 简洁回答
2. 如果可以，补一句依据说明
""".strip()

    # 创建客户端
    # 关键点：
    # 1. api_key 用 New API 平台给你的 token
    # 2. base_url 用你的站点地址 + /v1
    client = OpenAI(
        api_key=os.getenv("NEWAPI_API_KEY"),
        base_url=os.getenv("NEWAPI_BASE_URL")
    )

    # 读取模型名
    model_name = os.getenv("NEWAPI_MODEL", "gpt-5.2")

    # 调用 chat completions 接口
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "你是一个严格基于给定资料回答问题的助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        stream=False
    )

    # 返回模型输出内容
    return response.choices[0].message.content


if __name__ == "__main__":
    # 读取已经保存好的 chunks
    chunks = load_chunks("data/processed/chunks.json")

    # 获取用户输入的问题
    query = input("请输入你的问题：").strip()

    # 先做检索
    top_results = retrieve_top_k(query, chunks, k=5)

    # 再交给模型生成回答
    answer = generate_answer_with_newapi(query, top_results)

    # 打印最终回答
    print("\n===== 最终回答（New API 生成）=====\n")
    print(answer)

    # 打印参考 chunks，方便你核对
    print("\n===== 参考 chunks =====\n")
    if not top_results:
        print("没有检索到相关 chunks。")
    else:
        for item in top_results:
            print(f"chunk_id = {item['chunk_id']} | score = {item['score']}")
            print(item["text"])
            print()