# 字节跳动 AI 研发/算法专家能力画像 (ByteDance P7/P8 Equivalent)

**核心关键词**: **极致工程化 (Engineering Excellence)**, **数据驱动 (Data Driven)**, **高并发 (High Concurrency)**, **推荐/大模型落地**.

与阿里不同，字节的面试通常**必须手写代码**（算法题），且对**底层原理**（CUDA、操作系统、网络）考察极深。

---

## 一、 通用硬性门槛 (The "ByteStyle" Baseline)

### 1. 极强的代码与算法功底 (Coding Bar)
*   **算法题**: 即使是 P8 级别，面试也大概率会考 1-2 道 LeetCode Medium/Hard 题目。要求 `Bug Free` 且代码风格极其规范。
*   **语言栈**: 
    *   **Python**: 精通，不仅是调用，要懂 GIL、内存管理、多进程优化。
    *   **C++**: **(高加分项)** 很多高性能推理引擎（ByteNN）、搜推引擎底层都是 C++。
    *   **Go**: 字节内部服务治理主力语言，懂 Go 的高并发模型 (GMP 调度) 是加分项。

### 2. 极致的系统工程能力
*   **QPS 敏感**: 习惯处理亿级流量。面试常问：“如何将模型推理延迟从 50ms 优化到 10ms？”
*   **A/B 测试**: 字节是 A/B Test 的信徒。你需要深刻理解 **实验设计**、**置信度**、**流量分层**。不仅仅是把模型练出来，还要能证明它在线上带来了 DAU 或 停留时长的增长。

---

## 二、 细分领域要求 (根据 JD 归纳)

### A. 大模型/生成式 AI 方向 (Doubao/Coooo/豆包)
目前字节最火的赛道。
1.  **训练性能优化 (Training Efficiency)**:
    *   熟悉 **Megatron-LM**, **DeepSpeed** 的源码级原理。
    *   解决过千卡集群的训练稳定性问题 (Loss Spike, 机器故障自动恢复)。
2.  **推理与服务化 (Serving)**:
    *   精通 **TensorRT**, **vLLM**, 或字节自研的 **ByteTransformer**。
    *   **KV Cache 优化**: 极其看重推理成本的降低。
3.  **强化学习与对齐 (RLHF)**:
    *   不仅仅是 PPO，要懂 **Reward Model** 的数据构造（如何防止 Reward Hacking）。
    *   熟悉 **DPO (Direct Preference Optimization)** 及其在生产环境的各种坑。

### B. 推荐系统/广告算法 (The Core Cash Cow)
字节的立身之本（抖音/TikTok 算法）。
1.  **大规模稀疏模型**:
    *   熟悉 **Embedding** 技术，处理百亿级特征 (Sparse Features)。
    *   熟悉 **Parameter Server (PS)** 架构 vs **All-Reduce** 架构的优劣。
2.  **在线学习 (Online Learning)**:
    *   模型如何进行实时更新？(Flink + TensorFlow/PyTorch)。
3.  **召回与精排**:
    *   双塔模型 (Two-Tower)、多目标优化 (MMOE, PLE)。

### C. 多模态与 CV (Video/Image Generation)
剪映、抖音特效、视觉大模型。
1.  **扩散模型 (Diffusion Models)**:
    *   精通 SD (Stable Diffusion), DiT (Diffusion Transformer) 架构。
    *   **Video Generation**: 熟悉视频生成的一致性问题 (Consistency)。
2.  **端侧 AI (On-Device AI)**:
    *   模型压缩、剪枝 (Pruning)、蒸馏 (Distillation)。
    *   如何把模型塞进手机端（NCNN, TNN, CoreML）并实时运行。

---

## 三、 软技能与文化 (ByteStyle)

1.  **Always Day 1**: 即使是老专家，也要有在一线写代码、看数据的冲劲。不要表现出“我只管人，不写代码”的态度。
2.  **数据说话 (ROI)**: 所有的优化都要折算成收益。
    *   *Bad*: "我优化了模型结构，准确率提升了 1%。"
    *   *Good*: "我优化了模型结构，在准确率提升 1% 的同时，推理成本降低了 20%，预计每年节省算力成本 500 万。"
3.  **坦诚清晰**: 沟通直切要害，不要废话和包装。

---

## 四、 针对你的项目的调整建议 (Vs. Alibaba Plan)

如果你的目标转向字节，现有的 `enterprise-brain` 项目需要做以下调整：

1.  **弱化**: 复杂的 SaaS 租户管理、文档编写、流程图。
2.  **强化**:
    *   **Benchmark**: 必须有极其详细的压测数据报告（P99 Latency, Throughput）。
    *   **Custom Kernel**: 尝试写一个自定义的 CUDA 算子，或者给 vLLM 提一个 PR 优化性能。
    *   **End-to-End**: 尝试做一个端侧版本（比如用 WebLLM 在浏览器跑模型），体现对“端侧落地”的理解。
    *   **Ranking**: 在 RAG 检索后，增加一个**精排模型 (Re-ranking Model)**，使用 XGBoost 或 BERT 专门对检索结果排序，体现搜推思维。

