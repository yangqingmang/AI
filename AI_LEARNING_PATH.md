# 🧠 大模型开发入门路线图 (LLM Developer Roadmap) - Ultimate Edition

> **目标**：从零基础到能够独立构建**企业级**智能体 (Agent) 的 AI 全栈工程师。
> **核心原则**：自底向上，先懂原理，后用框架，重在评估与工程化。

---

## 🚩 核心实战路径 (The 8 Stages)

### 阶段一：学会与 AI 深度对话 (Prompt Engineering)
*在写代码之前，先学会如何高效地调度 LLM 的能力。*
- [ ] **核心概念**：Context Window（上下文窗口）、Tokens（分词）、System Prompt（角色设定）。
- [ ] **必会技巧**：CoT (Chain of Thought, 思维链)、Few-shot Prompting (少样本提示)。
- [ ] **实践任务**：使用 ChatGPT/DeepSeek 网页版，尝试让它完成一个复杂的任务（如：整理会议纪要并提取待办）。

### 阶段二：Hello AI —— 掌握原生 API 调用
*跳过框架，先学会最原始的通信方式。*
- [ ] **环境准备**：安装 Python 3.10+，获取 API Key。
- [ ] **技术重点**：熟悉 `openai` SDK，掌握 `messages` 数组结构（User/Assistant/System）。
- [ ] **实践任务**：编写一个 20 行的脚本，实现一个在控制台运行的连续对话小助手，并尝试调整 `temperature` 参数。

### 阶段三：赋予 AI 外部知识 (Embeddings & Vector DB)
*让 AI 能够检索它在预训练阶段没见过的数据。*
- [ ] **核心概念**：Embeddings（嵌入/向量化）、Vector Database（向量数据库）。
- [ ] **数学直觉**：Cosine Similarity（余弦相似度）。
- [ ] **实践任务**：手写一个脚本，将 10 个不同的句子转换成向量，并计算出哪两个句子意思最接近。

### 阶段四：手写 RAG (检索增强生成)
*这是目前企业落地最多的场景，不依赖框架手写一遍流程。*
- [ ] **理解全链路**：Load (加载) -> Split (切片) -> Embed (向量化) -> Retrieve (检索) -> Augment (增强) -> Generate (生成)。
- [ ] **实践任务**：实现一个“日记问答助手”：把你的几篇文本日记存入向量库，问 AI “我上周去哪玩了？”，看它能否准确找到原文并回答。

### 阶段五：从“胡言乱语”到“精准控制” (Structured Output) [⭐ 新增]
*企业级开发必须掌握：如何让 AI 稳定输出 JSON。*
- [ ] **痛点解决**：让 AI 像 API 接口一样稳定输出数据。
- [ ] **核心技术**：JSON Mode、Pydantic (数据校验)、Instructor / LangChain Parser。
- [ ] **实践任务**：编写脚本，输入一段乱七八糟的用户收货地址，让 AI 稳定提取出标准 JSON 对象（省、市、电话等）。

### 阶段六：从“对话”到“执行” (Agents & Function Calling)
*让 AI 能够调用函数、操作电脑、搜索网页。*
- [ ] **核心概念**：Function Calling（函数调用）、ReAct 模式（思考-行动循环）。
- [ ] **实践任务**：定义一个模拟查股价的 Python 函数，让 AI 自动识别用户意图并调用该函数回答问题。

### 阶段七：评估与迭代 (Evaluation / Evals) [⭐ 新增]
*区分“玩具”与“产品”的关键：不靠肉眼看，靠数据说话。*
- [ ] **核心概念**：Ground Truth（标准答案）、RAGAS / DeepEval（评估框架）。
- [ ] **关键指标**：Faithfulness（忠实度）、Context Recall（召回率）。
- [ ] **实践任务**：建立一个包含 20 个测试用例的数据集，运行你的 RAG 系统并计算准确率得分。

### 阶段八：本地模型与微调 (Local LLM & Fine-tuning) [⭐ 新增]
*掌握私有化部署与模型定制能力。*
- [ ] **核心工具**：Ollama（本地运行）、vLLM（推理服务）。
- [ ] **微调技术**：PEFT / LoRA（轻量级微调）。
- [ ] **实践任务**：下载 Ollama 并运行 `qwen:7b`，修改代码将 API 指向本地（localhost），实现完全离线的 RAG。

---

## 📚 殿堂级学习资源 (Must-Watch)

- **吴恩达 (Andrew Ng)**: [Generative AI for Everyone](https://www.deeplearning.ai/courses/generative-ai-for-everyone/) —— *6 小时建立完整的 AI 世界观。*
- **Andrej Karpathy**: [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) —— *技术原理讲得最透彻的视频（必看）。*
- **李沐 (Mu Li)**: [B站：跟李沐学AI](https://space.bilibili.com/1567748478) —— *中文圈最硬核、最良心的深度学习与大模型论文精读。*
- **OpenAI Cookbook**: [官方代码菜谱](https://github.com/openai/openai-cookbook) —— *海量一线实战代码参考。*

---

## 🌐 权威信息源清单 (The Authoritative Info Diet)

### 1. 深度研究与学术前沿 (Deep Research)
- **ArXiv.org (CS.CL)**: 论文原始首发地。
- **Hugging Face Papers**: [Daily Papers](https://huggingface.co/papers) —— *每日最受关注的论文筛选。*
- **Papers with Code**: [Trends](https://paperswithcode.com/) —— *论文 + 源码实现，复现算法的首选。*

### 2. 顶级产业实验室 (Industrial Labs)
- **OpenAI Research**: [Blog](https://openai.com/news/search/?categories=research) —— *GPT 系列的诞生地。*
- **Google DeepMind**: [Blog](https://deepmind.google/discover/) —— *关注 AlphaFold 和 Gemini 动态。*
- **Anthropic News**: [Research](https://www.anthropic.com/news) —— *Claude 系列与 AI 安全研究。*
- **Meta AI (FAIR)**: [News](https://ai.meta.com/blog/) —— *开源大模型之王 Llama 的发布地。*
- **Microsoft Research**: [AI Blog](https://www.microsoft.com/en-us/research/blog/category/artificial-intelligence/) —— *涵盖极广的 AI 前沿探索。*

### 3. 行业领袖与技术社区 (Community & Gurus)
- **Andrej Karpathy**: [X/Twitter](https://x.com/karpathy) —— *AI 领域最具影响力的教育者。*
- **Yann LeCun**: [X/Twitter](https://x.com/ylecun) —— *图灵奖得主，Meta 首席科学家，观点犀利。*
- **Hacker News**: [Show HN](https://news.ycombinator.com/) —— *硅谷技术风向标，第一时间发现顶级开源项目。*
- **Reddit (r/LocalLLaMA)**: [Home](https://www.reddit.com/r/LocalLLaMA/) —— *全球最活跃的本地大模型与显卡玩家社区。*
- **宝玉**: [微博/X](https://baoyu.io/) —— *中文圈最接地气的 AI 工程化落地专家。*

### 4. 商业、创投与深度访谈 (Business & Logic)
- **张小珺 (播客)**: 强烈推荐。能采访到中国 AI 圈最核心操盘手（杨植麟、王小川等）。
- **Lex Fridman Podcast**: [YouTube](https://www.youtube.com/@lexfridman) —— *采访 Sam Altman, Elon Musk 等人的神级深度长访谈。*
- **The Information / SemiAnalysis**: 硅谷最硬核的独家商业爆料与芯片/算力成本深度分析。
- **Latent Space**: 专注于 AI 工程师视角的硬核播客。
- **机器之心 / 量子位**: 国内最专业、最及时的 AI 科技媒体。

---

## 🎯 进阶里程碑
- [ ] 能在不看教程的情况下，手写出一个支持上传 PDF 的问答 API。
- [ ] 能构建一套自动化测试流程，证明你的 RAG 系统准确率超过 90%。
- [ ] **能站在商业视角，清晰阐述一个大模型项目在算力、数据和落地场景上的 ROI。**
