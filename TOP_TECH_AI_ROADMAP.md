# BAT (字节/阿里/腾讯) P7+ AI 专家级成长路线图

**目标**: 具备独立负责 AI 核心子系统（如推理引擎、训练平台、垂直领域大模型）的能力。
**核心素质**: 算法原理深度 + 系统工程能力 + 业务架构视野。
**总周期**: 9-12 个月 (假设每天投入 2-3 小时高效学习/实战)

---

## 阶段一：内功重塑 —— 系统与底层 (1.5 - 2 个月)
**痛点**: 大厂面试中最容易挂的地方，不是不懂 Transformer，而是不懂计算机体系结构。
**目标**: 能从硬件视角理解模型运行。

### 1. 高性能编程 (C++/CUDA)
*   **核心任务**:
    *   精通 **Modern C++ (14/17/20)**: 智能指针、移动语义、多线程并发 (std::thread, future)。*AI 基础设施底层全是 C++。*
    *   入门 **CUDA 编程**: 理解 GPU 架构 (SM, Warp, Shared Memory, HBM)。
    *   **实战**: 使用 `Triton` (OpenAI 的 GPU 语言) 或原生 CUDA 写一个简单的 **Matrix Multiplication (矩阵乘法)** 算子，并尝试优化到接近 cuBLAS 的性能。
*   **检验标准**: 能解释清楚“为什么 Batch Size 增大能提高 GPU 利用率？”（从内存带宽和计算密度角度回答）。

### 2. 计算机系统基础
*   **核心任务**:
    *   **OS**: 进程/线程调度、虚拟内存、Page Fault。
    *   **Network**: RDMA (InfiniBand) vs TCP/IP，NCCL 通信原语 (AllReduce, AllGather) 的原理。
*   **推荐资源**: 《Computer Systems: A Programmer's Perspective (CSAPP)》

---

## 阶段二：算法内核 —— 手撕大模型 (2.5 - 3 个月)
**痛点**: 只会 `from transformers import AutoModel` 是 P5/P6 水平。
**目标**: 具备从零构建并训练一个 mini-LLM 的能力。

### 1. Transformer 深度解剖
*   **核心任务**:
    *   **手写代码**: 不依赖 PyTorch 的 `nn.Transformer`，仅用 Tensor 操作手写 Self-Attention, Multi-Head Attention, LayerNorm, FeedForward。
    *   **位置编码**: 彻底搞懂并手推 **RoPE (旋转位置编码)** 和 **ALiBi** 的数学推导。
    *   **KV Cache**: 亲手实现 KV Cache 推理逻辑，理解显存占用公式。

### 2. 预训练 (Pre-training) 全流程
*   **核心任务**:
    *   **数据**: 编写高效的 DataLoader，处理 Tokenization、数据混合 (Data Mixing)、去重。
    *   **架构**: 复现 LLaMA 结构 (RMSNorm, SwiGLU)。
    *   **实战**: 在单机多卡或云端小集群上，训练一个 **NanoGPT** (比如 100M 参数)，跑通 Loss 下降曲线。

### 3. 微调与强化学习 (SFT & RLHF)
*   **核心任务**:
    *   **SFT**: 理解指令微调的数据格式。
    *   **RLHF**: 搞懂 PPO (Proximal Policy Optimization) 的四个模型交互流程 (Actor, Critic, Ref, Reward)。
    *   **DPO**: 理解 DPO 如何移除 Reward Model 简化流程，并在数学上等价于 RLHF。

---

## 阶段三：AI Infra —— 分布式与极致优化 (3 个月)
**这是目前最稀缺、薪资最高的领域。**
**目标**: 解决“模型太大装不下”和“速度太慢不够用”的问题。

### 1. 分布式训练 (Training System)
*   **核心任务**:
    *   **并行策略**: 彻底精通 **Data Parallel (DP/DDP/FSDP)**, **Tensor Parallel (TP)**, **Pipeline Parallel (PP)**。
    *   **框架源码**: 阅读 **DeepSpeed** 或 **Megatron-LM** 源码，理解 ZeRO-1/2/3 到底切分了什么。
    *   **显存优化**: Activation Checkpointing (梯度检查点), CPU Offload。

### 2. 推理加速 (Inference System)
*   **核心任务**:
    *   **框架**: 精通 **vLLM** (PagedAttention 原理), **TensorRT-LLM**。
    *   **技术点**: Continuous Batching (动态批处理), Speculative Decoding (投机采样), FlashAttention-2 (IO 感知优化)。
    *   **量化**: 各种量化方法的原理 (GPTQ, AWQ, FP8) 及其精度损失分析。

---

## 阶段四：业务架构与搜推结合 (1.5 - 2 个月)
**目标**: 将 AI 能力转化为业务价值，具备字节/阿里风格的架构视野。

### 1. 搜推 (Search & Rec) + LLM
*   **趋势**: RAG 正在向 Search 演进，推荐系统正在向 LLM 演进。
*   **核心任务**:
    *   **召回 (Retrieval)**: 向量索引 (HNSW, IVFPQ) 原理与调优。
    *   **精排 (Ranking)**: Cross-Encoder 架构，Learning to Rank (LTR) 思想。
    *   **实战**: 设计一个支持“千万级文档库 + 毫秒级响应”的 RAG 系统架构图，包含缓存层、召回层、重排层、生成层。

### 2. Agent 与评估体系
*   **核心任务**:
    *   **Agent**: 理解 ReAct, Tool Use, Planning 的局限性。
    *   **Eval**: 搭建自动化评估流水线 (RAGAS, TruLens)，不要只看 BLEU/ROUGE，要看业务指标。

---

## 阶段五：实战作品集 (Portfolio) —— 敲门砖 (持续进行)

**不要只做“玩具项目”，要做“工业级验证”。**

1.  **Project A: "Mini-DeepSpeed"**
    *   不调用库，手动用 PyTorch Distributed 实现一个简单的 Data Parallel + Gradient Accumulation 训练脚本。
    *   *简历亮点*: "深入理解分布式训练原理，手写实现了数据并行核心逻辑。"

2.  **Project B: "Custom Kernel Operator"**
    *   使用 Triton 或 CUDA 编写一个自定义的 FlashAttention 简化版算子，并与 PyTorch 原生 Attention 进行 benchmark 对比。
    *   *简历亮点*: "具备高性能算子开发能力，实测自定义算子比原生快 x%."

3.  **Project C: "Vertical Domain LLM End-to-End"**
    *   找一个特定领域（如法律、医疗代码），从数据清洗 -> Tokenizer 训练 -> 预训练/增量预训练 -> SFT -> 量化部署，跑通全链路。
    *   *简历亮点*: "具备大模型全生命周期落地经验。"

---

## 推荐书单与课程

1.  **AI 系统**: *Deep Learning Systems (CMU 10-414)* - 陈天奇大神亲授。
2.  **CUDA**: *Programming Massively Parallel Processors* (PMPP 书籍)。
3.  **LLM 理论**: *Stanford CS224N* (NLP) / *CS324* (Large Language Models)。
4.  **论文跟进**: 定期阅读 NeurIPS, ICLR, ICML 顶会关于 System 和 LLM 的最佳论文。
