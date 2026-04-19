# rag-from-scratch-week1

这是一个用于学习最小 RAG 流程的练手项目。我按照“先跑通最小闭环，再逐步优化”的思路，从文本切分开始，逐步完成了检索、规则式回答、拒答机制，以及接入大模型生成回答的版本。

这个项目的重点不是直接追求复杂工程，而是通过一个可运行、可观察、可修改的小项目，理解 RAG 的核心流程到底在做什么。

## 项目目标

- 理解 RAG 的基本组成：加载资料、切分文本、检索相关内容、生成回答
- 从零实现一个最小可运行的 RAG 原型
- 通过逐日迭代，观察不同模块对最终回答质量的影响
- 在规则式回答的基础上，进一步接入大模型完成生成式回答

## 什么是 RAG

RAG 是 Retrieval-Augmented Generation 的缩写，中文通常叫“检索增强生成”。

它的核心思想不是只依赖模型参数中的知识，而是：

1. 先从外部知识库中检索相关资料
2. 再把检索结果和用户问题一起交给生成模块
3. 最后基于这些资料生成更有依据的回答

这也是为什么 RAG 往往比“直接问模型”更适合做知识问答系统，因为它更容易补充外部知识，也更容易解释回答依据。

## 当前实现的最小 RAG 流程

本项目目前已经实现了下面这条完整链路：

1. 读取本地知识库文本 `data/raw/knowledge.txt`
2. 将长文本切分为多个 chunks
3. 将 chunks 保存到 `data/processed/chunks.json`
4. 用户输入问题后，对所有 chunks 进行相关性打分
5. 返回最相关的 top-k chunks
6. 基于检索结果生成回答
7. 当资料不足时，触发简单拒答机制
8. 可选地接入 New API 上的大模型生成最终回答

## 项目结构

```text
week1/
├─ data/
│  ├─ raw/
│  │  └─ knowledge.txt
│  └─ processed/
│     └─ chunks.json
├─ learn_md/
│  ├─ day1_notes.md
│  ├─ day2_notes.md
│  ├─ day3_notes.md
│  ├─ day4_notes.md
│  ├─ day5_notes.md
│  └─ day6_notes.md
├─ src/
│  ├─ build_chunks.py
│  ├─ chunker.py
│  ├─ config.py
│  ├─ embedder.py
│  ├─ generator.py
│  ├─ load_and_split.py
│  ├─ loader.py
│  ├─ pipeline.py
│  ├─ rag_demo.py
│  ├─ rag_with_newapi.py
│  ├─ retrieve.py
│  ├─ retriever.py
│  └─ vector_store.py
├─ .env.example
└─ README.md
```

## 核心模块说明

- `loader.py`：读取本地文本文件
- `chunker.py`：按固定窗口切分文本，并支持 chunk overlap
- `embedder.py`：使用简化的 bigram 方式表示文本
- `retriever.py`：计算问题与 chunk 的相关性分数，并返回 top-k 结果
- `generator.py`：根据检索结果生成规则式回答，或调用 New API 生成回答
- `vector_store.py`：负责将 chunks 保存到本地 JSON，并再次加载
- `config.py`：统一管理路径和默认参数
- `pipeline.py`：封装构建 chunks、检索、问答等公共流程

## 我学到的关键概念

### 1. chunk_size

`chunk_size` 表示每个文本块的长度。

- 值越大：每个 chunk 包含的信息越多，chunk 数量越少
- 值越小：每个 chunk 更细，但 chunk 数量会变多

### 2. chunk_overlap

`chunk_overlap` 表示相邻 chunks 之间保留的重叠内容。

它的作用是减少上下文被硬切断的问题，避免重要信息刚好落在两个 chunk 的边界上。

### 3. top-k 检索

top-k 表示从所有 chunks 中选出分数最高的前 k 个结果。

- top-k 太小，可能漏掉有用上下文
- top-k 太大，可能带入更多噪声

所以 top-k 不是越大越好，而是需要结合知识库内容和检索质量来调节。

### 4. 拒答机制

当知识库里没有足够相关的信息时，一个好的 RAG 系统不应该硬编答案，而应该明确说“无法根据当前资料回答”。

本项目中通过 `should_refuse()` 做了一个简单阈值判断，用于控制是否拒答。

## 从 Day 1 到 Day 6 的学习演进

### Day 1

- 理解 RAG 的基本流程
- 明白为什么不能直接把整篇长文丢给模型
- 初步理解 `chunk_size` 和 `chunk_overlap`

### Day 2

- 学习文本切分
- 观察不同 `chunk_size` 和 `chunk_overlap` 对 chunk 数量和上下文连续性的影响

### Day 3

- 将 chunks 保存为本地 JSON
- 完成最基础的检索流程
- 用简单的字符片段重合方式计算相关性

### Day 4

- 第一次真正把 Retrieval 和 Generate 串起来
- 从 top-k chunks 中挑选更相关的句子
- 输出一个最小闭环的问答系统

### Day 5

- 过滤掉 score 为 0 的无关 chunks
- 将输出格式优化为“回答 + 依据 + 总结”
- 让结果更清晰，也更像一个问答系统

### Day 6

- 扩充知识库内容
- 增大 top-k 检索数量
- 加入简单拒答机制
- 接入 New API 上的大模型，生成更自然的回答

## 运行方式

### 1. 生成 chunks

在 `week1` 目录下运行：

```bash
python src/build_chunks.py
```

作用：

- 读取 `data/raw/knowledge.txt`
- 执行文本切分
- 生成 `data/processed/chunks.json`

### 2. 预览切分效果

```bash
python src/load_and_split.py
```

作用：

- 直接打印 chunks
- 方便观察切分是否合理

### 3. 测试检索结果

```bash
python src/retrieve.py
```

作用：

- 输入问题
- 查看最相关的 top-k chunks
- 观察当前检索效果

### 4. 运行规则式 RAG Demo

```bash
python src/rag_demo.py
```

作用：

- 执行完整检索流程
- 输出“回答 + 依据 + 总结”
- 不依赖外部大模型接口

### 5. 运行接入 New API 的版本

```bash
python src/rag_with_newapi.py
```

在运行前，需要先配置 `.env` 文件，例如：

```env
NEWAPI_API_KEY=your_api_key
NEWAPI_BASE_URL=your_base_url
NEWAPI_MODEL=gpt-5.2
```

这个版本会：

- 先执行本地检索
- 再把检索到的上下文交给大模型生成回答
- 在资料不足时触发简单拒答

## 当前项目的特点

- 实现路径清晰，适合入门理解 RAG
- 保留了最小可运行闭环，便于观察每一步在做什么
- 同时包含“规则式回答”和“模型生成回答”两种版本
- 已经支持基本的拒答机制
- 项目结构较轻量，适合继续迭代

## 当前局限

- 检索仍然基于简单字符片段重合，不是真正的 embedding 语义检索
- chunk 打分方式还比较粗糙，容易受表面字符重合影响
- top-k 变大后仍可能带入噪声
- 拒答机制目前只是基于分数阈值，仍然比较简单
- 大模型输出格式有时仍可能带有 Markdown 风格
- 知识库规模还比较小，更适合作为学习型项目

## 下一步可以继续优化的方向

- 将检索从字符重合升级为 embedding + 向量检索
- 继续优化 top-k 选择策略
- 改进拒答逻辑，让判断更稳
- 优化 prompt，减少终端中的 Markdown 风格输出
- 在回答中加入更明确的引用信息，例如 `[chunk 5]`
- 对比规则式回答和大模型生成回答的效果差异

## 适合谁看这个项目

这个项目比较适合下面几类人：

- 刚开始学习 RAG，想先从最小原型入手的人
- 想自己把 Retrieval 和 Generate 分开理解的人
- 想从“能跑通”开始，再逐步优化成更完整系统的人

## 总结

这个项目记录了我从“理解 RAG 是什么”，到“自己实现一个最小 RAG 闭环”，再到“接入大模型完成生成式回答”的学习过程。

它目前还不是一个成熟的生产系统，但已经能比较清楚地展示 RAG 的基本思想：回答质量不仅取决于模型本身，也取决于知识库内容、检索质量、上下文组织方式，以及是否具备合理的拒答策略。
