# BAT P7+ AI 专家之路：实操执行手册 (The "How-To" Guide)

这份文档是 `TOP_TECH_AI_ROADMAP.md` 的配套执行指南。它解决了“去哪看、抄哪里、写什么”的问题。

---

## 阶段一：系统与高性能编程 (C++/CUDA)

### 1. 环境准备 (Windows/WSL2)
不要在 Windows CMD 里折腾。
1.  **安装 WSL2 (Ubuntu 22.04)**: `wsl --install`.
2.  **配置 C++ 环境**:
    ```bash
    sudo apt update && sudo apt install build-essential cmake gdb
    ```
3.  **安装 CUDA Toolkit** (前提：你有 NVIDIA 显卡):
    *   去 NVIDIA 官网下载对应 WSL2 的 `.deb` 包安装。
    *   验证: 运行 `nvcc --version` 和 `nvidia-smi`。

### 2. C++ 怎么学 (只学 AI 用的部分)
*   **不要看**: 《C++ Primer》全书（太厚，会劝退）。
*   **要看**:
    *   **资源**: [LearnCpp.com](https://www.learncpp.com/) (查阅式学习) 或 *A Tour of C++* (Bjarne Stroustrup 写给有经验程序员的)。
    *   **重点章节**: Pointers/References (指针/引用), Memory Management (new/delete/smart pointers), Classes, Templates (模版 - AI 框架大量使用)。
*   **任务 1.1**: 手写一个 `MatMul` (矩阵乘法) 类。
    *   用 `std::vector<float>` 存储数据。
    *   实现 `dot_product` 函数。
    *   使用 OpenMP (`#pragma omp parallel for`) 尝试 CPU 多线程加速。

### 3. CUDA 怎么入门
*   **资源**:
    *   **必读**: [NVIDIA CUDA C++ Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/) 的 *Introduction* 和 *Programming Model* 章节。
    *   **Github 参考**: [kwea123/kwea123.github.io](https://github.com/kwea123/kwea123.github.io) (非常好的 CUDA 教程) 或者 [cuda-mode](https://github.com/cuda-mode) 社区资源。
*   **任务 1.2**: 写你的第一个 Kernel。
    *   目标：向量加法 (Vector Add)。
    *   代码结构：
        ```cpp
        __global__ void add(int *a, int *b, int *c) { ... }
        // main: cudaMalloc -> cudaMemcpy (H2D) -> add<<<grid, block>>> -> cudaMemcpy (D2H)
        ```
    *   进阶：使用 Shared Memory 优化矩阵乘法 (Tiling 技术)。

---

## 阶段二：手撕大模型 (Transformer/Training)

### 1. Transformer 怎么写
*   **不要**: 盯着论文里的数学公式发呆。
*   **要做**: **复现 Andrej Karpathy 的代码**。
*   **资源**:
    *   **视频**: YouTube "Let's build GPT: from scratch, in code, spelled out." (Andrej Karpathy).
    *   **Repo**: [karpathy/nanoGPT](https://github.com/karpathy/nanoGPT).
*   **任务 2.1**: "Copy-Paste-Understand"
    *   新建 `model.py`，跟着视频一行行敲出 `CausalSelfAttention` 类。
    *   **修改它**: 原始代码用的是标准 Attention，请你自己修改代码，把 `RoPE` (Rotary Positional Embedding) 加进去。参考 HuggingFace `transformers` 库中 Llama 的源码实现。

### 2. 预训练怎么做
*   **资源**: 依然是 `nanoGPT`，或者 [TinyLlama](https://github.com/jzhang38/TinyLlama)。
*   **任务 2.2**: 跑通训练循环。
    *   下载 `Shakespeare` 数据集 (几 MB)。
    *   运行 `train.py`。
    *   **观察**: 打开 TensorBoard，看 Loss 曲线。
    *   **调试**: 故意把 Learning Rate 调大 10 倍，看 Loss 怎么炸；把 LayerNorm 去掉，看模型还收不收敛。**这种“炸炉”的经验是专家才有的。**

---

## 阶段三：AI Infra (分布式与优化)

### 1. 分布式原理怎么学
*   **资源**: [HuggingFace: Transformers Distributed Training](https://huggingface.co/docs/transformers/perf_train_gpu_many).
*   **任务 3.1**: 模拟多卡训练。
    *   即使你只有一张卡，也可以用 `torchrun` 模拟分布式启动。
    *   使用 `DeepSpeed`：
        ```bash
        pip install deepspeed
        deepspeed train.py --deepspeed_config ds_config.json
        ```
    *   **实验**: 对比 ZeRO-Stage 2 和 Stage 3 的显存占用差异 (使用 `nvidia-smi` 观察)。

### 2. 推理优化怎么做
*   **资源**: [vLLM Blog](https://blog.vllm.ai/) (特别是关于 PagedAttention 的那篇)。
*   **任务 3.2**: 源码阅读与修改。
    *   Clone [vLLM](https://github.com/vllm-project/vllm) 仓库。
    *   找到 `vllm/core/block_manager.py`。
    *   **作业**: 在代码里加 print 或 log，打印出当一个 prompt 进来时，Block 是怎么被分配的。这一步能让你彻底理解“显存分页”。

---

## 阶段四：搜推业务与评估

### 1. 搜推系统怎么搭
*   **资源**: [Faiss Tutorial](https://github.com/facebookresearch/faiss/wiki/Getting-started).
*   **任务 4.1**: 构建 RAG 2.0 (带精排)。
    *   Step 1 (召回): 使用 `faiss.IndexFlatL2` 对 10万条文本向量建立索引。
    *   Step 2 (精排): 引入 `CrossEncoder` (用 `sentence-transformers` 库)。
    *   Step 3 (对比): 
        *   Pipeline A: Top 5 (Vector Search) -> LLM.
        *   Pipeline B: Top 100 (Vector Search) -> Rerank Top 5 -> LLM.
        *   **结论**: 找一个具体的例子（如“那种红色的水果叫什么？”），证明 Pipeline B 为什么更准。

---

## 推荐的每日时间表 (假设在职)

*   **09:00 - 18:00**: 工作 (尽量在工作中寻找 AI 结合点，哪怕是写脚本自动化)。
*   **20:00 - 21:00**: **Deep Work (编码)**。不做业务，只写 C++/CUDA 或 PyTorch 底层代码。不要被打断。
*   **21:00 - 22:00**: **Input (阅读)**。看论文、看源码、看 CSAPP。
*   **周末**: **Project Time**。把平日写的代码串起来，变成一个完整的 Repo (比如 "My-Tiny-Llama")。
