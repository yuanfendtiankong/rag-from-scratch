# rag-from-scratch-week1

这是一个用于学习最小 RAG 流程的练手项目。我按照“先跑通最小闭环，再逐步优化”的思路，从文本切分开始，逐步完成了检索、规则式回答、拒答机制、接入大模型生成回答，以及对检索策略和项目结构的进一步整理。

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
9. 当 New API 调用失败时，自动回退到本地规则版回答

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
│  ├─ day6_notes.md
│  └─ day7_notes.md
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
│  ├─ retrieve_demo.py
│  ├─ retriever.py
│  └─ vector_store.py
├─ app.py
├─ .env.example
└─ README.md
```

## 核心模块说明

- `loader.py`：读取本地文本文件
- `chunker.py`：按固定窗口切分文本，并支持 chunk overlap
- `embedder.py`：负责文本表示，当前支持简化的 bigram 表示和本地 sentence-transformers 向量表示
- `retriever.py`：计算问题与 chunk 的相关性分数，并返回 top-k 结果
- `generator.py`：根据检索结果生成规则式回答，或调用 New API 生成回答
- `vector_store.py`：负责将 chunks 和 chunk 向量缓存保存到本地 JSON，并再次加载
- `config.py`：统一管理路径和默认参数
- `pipeline.py`：封装构建 chunks、检索、问答等公共流程
- `app.py`：项目统一入口，可选择规则版或 New API 版运行模式

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

### 5. 可解释性

RAG 的一个重要价值，不只是“能回答”，还包括“能说明依据来自哪里”。

本项目当前的规则式回答已经支持：

- 在依据中标注 `[chunk x]`
- 在总结中说明主要参考了哪些 chunks

### 6. 表示层与相似度层

检索并不只是“套一个 embedding 模型”这么简单，还包括两层设计：

1. 文本如何表示
2. 两个表示如何比较

当前项目目前包含两条检索思路：

- `normalize_text()`
- bigram 字符片段集合 + `query coverage + Jaccard`
- 本地 sentence-transformers 向量 + 余弦相似度
- 在真实 embedding 检索上额外加入 lexical baseline，形成轻量 hybrid retrieval
- 对 chunks 的向量做预计算和本地缓存

这样做的目的是让“短 query 对长 chunk”的问答检索更稳定，同时逐步把项目从教学版检索升级到真实向量检索。

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

### Day 7

- 增加项目统一入口 `app.py`
- 让规则式回答带上更明确的来源引用
- 将检索从“简单字符重合”升级为更合理的混合相似度
- 增加文本规范化处理
- 接入本地真实 embedding / 向量检索
- 增加短 chunk 过滤、hybrid retrieval、更稳的主回答选择逻辑
- 增加 chunk 向量预计算与本地缓存

## 运行方式

### 1. 生成 chunks

在 `week1` 目录下运行：

```bash
python3 src/build_chunks.py
```

作用：

- 读取 `data/raw/knowledge.txt`
- 执行文本切分
- 生成 `data/processed/chunks.json`

### 2. 预览切分效果

```bash
python3 src/load_and_split.py
```

作用：

- 直接打印 chunks
- 方便观察切分是否合理

### 3. 测试检索结果

```bash
python3 src/retrieve_demo.py
```

作用：

- 输入问题
- 查看最相关的 top-k chunks
- 观察当前检索效果
- 便于对比不同检索策略的排序效果

### 4. 运行规则式 RAG Demo

```bash
python3 src/rag_demo.py
```

作用：

- 执行完整检索流程
- 输出“回答 + 依据 + 总结”
- 不依赖外部大模型接口

### 5. 运行接入 New API 的版本

```bash
python3 src/rag_with_newapi.py
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
- 当 API 请求失败时，自动回退到本地规则版回答

### 6. 使用统一入口运行

```bash
python3 app.py
```

这个入口会：

- 让你选择规则版或 New API 版
- 接收用户问题
- 统一展示最终回答与参考 chunks
- 更适合日常演示和测试

## 当前默认检索方式

当前项目默认已经切换到：

- 本地 `sentence-transformers` 模型
- 余弦相似度
- lexical baseline 辅助打分
- `data/processed/chunk_embeddings.json` 向量缓存

也就是说，现在默认不是最初的纯 bigram 检索，而是一个更接近真实 RAG 系统的本地向量检索版本。

## 当前项目的特点

- 实现路径清晰，适合入门理解 RAG
- 保留了最小可运行闭环，便于观察每一步在做什么
- 同时包含“规则式回答”和“模型生成回答”两种版本
- 已经支持基本的拒答机制
- 已经支持统一入口和更清晰的输出结构
- 规则版回答具备更明确的引用来源
- 已经支持从本地模型目录加载真实 embedding 模型
- 已经接入本地真实 embedding / 向量检索
- 已经加入短 chunk 过滤和 hybrid retrieval
- 已经支持 chunk 向量预计算与缓存
- 项目结构较轻量，适合继续迭代

## 当前局限

- 当前 chunk 切分仍然比较粗糙，容易产生句子截断和残片
- 虽然已经有 chunk 向量缓存，但每个新进程首次运行时仍然要重新加载本地模型
- top-k 变大后仍可能带入噪声
- 拒答机制目前只是基于分数阈值，仍然比较简单
- 大模型输出格式有时仍可能带有 Markdown 风格
- 知识库规模还比较小，更适合作为学习型项目
- 本地模型和 Python 依赖已经成为新的工程复杂度来源

## 在实现过程中遇到的典型问题

这个项目在推进过程中，不只是遇到了“模型和检索”的问题，也遇到了一些很真实的工程问题：

- Windows 风格虚拟环境和 WSL / Linux 终端的路径不匹配
- New API 运行时缺少 `python-dotenv` 依赖
- 自动回退逻辑只处理接口请求失败，不处理依赖缺失
- 纯 Jaccard 在“短 query + 长 chunk”场景下效果不理想
- 本地真实 embedding 的依赖安装比预想中更复杂，尤其是 `torch` 和 CPU / CUDA 路线选择
- 即使真实 embedding 接通之后，仍然需要过滤短 chunk、加入 hybrid retrieval，并继续调整回答生成逻辑
- 当向量缓存写入 JSON 后，读取时还需要把 list 重新转回数值数组

这些问题让我更清楚地看到，一个 RAG 项目除了算法本身，还会涉及：

- Python 环境管理
- 依赖安装
- 检索实验
- 结构演进

如果你想看更详细的过程记录，可以直接阅读：

- `learn_md/day7_notes.md`

## 下一步可以继续优化的方向

- 对比 bigram baseline 和真实 embedding 检索的效果差异
- 继续优化 chunk 向量缓存策略，例如增加模型版本和缓存失效机制
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

这个项目记录了我从“理解 RAG 是什么”，到“自己实现一个最小 RAG 闭环”，再到“接入大模型完成生成式回答”，并逐步整理项目结构、增强可解释性、优化检索策略、接入本地真实 embedding 检索的学习过程。

它目前还不是一个成熟的生产系统，但已经能比较清楚地展示 RAG 的基本思想：回答质量不仅取决于模型本身，也取决于知识库内容、检索质量、上下文组织方式、引用可解释性，以及是否具备合理的拒答策略。
