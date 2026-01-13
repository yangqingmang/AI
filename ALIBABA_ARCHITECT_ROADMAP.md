# 阿里 AI 解决方案架构师 (AI Solution Architect) 晋升路线图 (V2 - 增强版)

**目标职级**: P7/P8 (技术专家/高级技术专家)
**核心策略**: 覆盖 JD 显性要求 + 攻克“隐性门槛”（高可用、数据闭环、安全、评估体系）。

---

## 核心差距分析与项目映射
我们将利用 `enterprise-brain` 项目作为全栈演练场。

| 阿里 JD 关键词 (含隐含) | 对应实战项目模块 | 架构师级要求 (The "Hidden" Specs) |
| :--- | :--- | :--- |
| **推理/分布式/优化** | `src/core/llm.py` | 不仅会调库，要懂 **FlashAttention2**, **PagedAttention**, **算子融合**，能手写 CUDA 优化是加分项。 |
| **RAG/Agent/LangChain** | `src/core/agent.py` | 解决 LangChain 臃肿问题，实现 **GraphRAG** (知识图谱结合)，实现 **Multi-Agent** 协同。 |
| **样本处理/数据** | `src/ingest.py` | 构建 **ETL Pipeline** (Spark/Ray)，实现数据去重(MinHash)、质量打分、合成数据(Synthetic Data)。 |
| **Infra/K8s/硬件** | `deploy.sh` / Docker | 具备 **GPU 虚拟化**、**Spot 实例调度**、**混合云容灾** 的设计能力。 |

---

## 第一阶段：深度推理与极致性能 (1.5个月)
**目标**: 突破单纯的 API 调用，掌握模型落地的“最后一公里”。

### 1. 生产级推理改造 (覆盖 JD: 推理框架, VLLM)
- **任务**: 在 Docker 中集成 **vLLM** 或 **NVIDIA Triton Inference Server**。
- **差异化竞争点**:
    - **Continuous Batching**: 深入理解并配置动态批处理，压测对比吞吐量提升。
    - **Speculative Decoding (投机采样)**: 实现大小模型配合（如 Qwen-7B 辅助 Qwen-72B），降低延迟。
- **低配环境挑战**: 在 2C2G 节点实现 **Edge AI** 方案，使用 `llama.cpp` + `GGUF` 量化，并编写脚本通过 MQTT 上报推理结果。

### 2. 高并发与高可用 (隐形要求: 稳定性)
- **任务**: 引入 **Redis Semantic Cache** (语义缓存)。
    - *原理*: 同样的问题不经过 LLM，直接通过向量相似度从缓存返回，QPS 提升 100 倍。
- **任务**: 实现 **Rate Limiting** (限流) 和 **Fallback** (降级) 机制。当 GPU 显存满时，自动切回 CPU 或排队，而不是 Crash。

---

## 第二阶段：数据工程与评估体系 (2个月)
**目标**: 解决“模型效果不好怎么办”的问题，建立科学的迭代闭环。

### 1. 构建 DataOps 飞轮 (覆盖 JD: 样本处理)
- **任务**: 升级 `ingest.py` 为分布式数据处理流。
- **架构**: 使用 **Ray Data** 或 **Apache Spark** (单机模拟) 处理非结构化数据。
- **关键动作**:
    - 实现 **PII (敏感信息) 自动过滤**。
    - 实现 **Dedup (去重)** 算法。
    - **合成数据**: 使用大模型生成 Query-Answer 对，用于后续微调。

### 2. 严谨的评估工程 (隐形要求: 效果量化)
- **现状**: 目前大多凭感觉判断好坏。
- **任务**: 引入 **RAGAS** 或 **TruLens** 框架。
- **指标**: 建立 **Faithfulness** (忠实度), **Answer Relevance** (相关性), **Context Recall** (召回率) 的自动化评分报表。
- *面试话术*: "我建立了一套自动化 Eval Pipeline，每次代码提交都会自动跑回归测试，确保模型效果不回退。"

---

## 第三阶段：大模型训练与微调 (2个月)
**目标**: 掌握模型“大脑”的定制能力。

### 1. 全链路微调 (覆盖 JD: 分布式训练, Deepspeed)
- **任务**: 对 Qwen 模型进行 SFT (Supervised Fine-Tuning)。
- **技术**:
    - **LoRA/QLoRA**: 显存优化微调。
    - **Flash Attention**: 训练加速。
    - **Deepspeed Zero-3**: 多卡显存切分原理。
- **差异化**: 尝试 **Long Context (长文本)** 微调，解决 RAG 读不懂长文档的问题。

### 2. 对齐与强化学习 (覆盖 JD: RLHF, Verl)
- **任务**: 部署 **Verl** (Hybrid Flow) 框架。
- **实战**: 训练一个 Reward Model。即使数据量小，也要跑通 **DPO (Direct Preference Optimization)** 流程，证明你懂 RLHF 的工程坑点（如 KL 散度爆炸）。

---

## 第四阶段：架构设计与云原生 Infra (1.5个月)
**目标**: 具备设计百万级用户系统的宏观视野。

### 1. 云原生 AI 平台 (覆盖 JD: K8s, 容器)
- **任务**: 编写 K8s Operator 或 Helm Chart。
- **难点攻克**:
    - **GPU Sharing (MIG)**: 如何在一张 A100 上跑 7 个小模型？
    - **弹性伸缩 (HPA)**: 基于 GPU 利用率或队列深度的自动扩缩容。

### 2. 知识图谱与高级 RAG (隐形要求: 解决幻觉)
- **任务**: 引入 **GraphRAG** (NebulaGraph 或 Neo4j)。
- **场景**: 解决“阿里有哪些P9级员工”这种不仅需要相似度，还需要关系推理的问题。

---

## 第五阶段：阿里面试专项突击 (持续进行)

### 1. 阿里味儿 (Culture)
- **思考方式**: 从“技术思维”转向“业务价值思维”。
    - *Bad*: "我用了 Deepspeed 优化训练。"
    - *Good*: "我通过 Deepspeed ZeRO-3 优化，在保持模型效果不变的情况下，将训练成本降低了 40%，并将上线周期从 3 天缩短到 1 天。"
- **常用词**: 抓手、闭环、沉淀、赋能、打通、复用。（虽然有梗的嫌疑，但面试中要能听懂并适度使用专业术语表达业务价值）。

### 2. 系统设计 (System Design) 模拟题
- 设计一个支持多租户（ToB）、数据隔离、支持私有化部署的 RAG 平台。
- 设计一个超大规模（万卡级别）的训练集群网络拓扑。

### 3. 源码阅读清单 (不仅是会用)
- **Transformer 结构**: 手推 Self-Attention 公式。
- **vLLM**: PagedAttention 显存管理代码。
- **LangChain**: 为什么它被诟病？如何自己实现一个轻量级的？

---

## 执行计划仪表盘 (基于当前进度)

1.  **本周重点**: 环境准备。
    -   安装 WSL2。
    -   Docker 化现有应用。
    -   在代码中集成 Prometheus 埋点 (为 Observability 做准备)。

2.  **下周重点**: 推理优化。
    -   将 `llm.py` 的调用后端替换为 vLLM (API 兼容模式)。
    -   记录 latency 和 throughput 的变化。