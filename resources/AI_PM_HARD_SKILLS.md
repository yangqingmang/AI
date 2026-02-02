# AI PM 硬核技术胜任力模型 (The Hardcore AI PM Competencies)

> "Traditional PMs write specs for code. AI PMs curate datasets for models."

本文档定义了 BAT P7+ 级别 AI 产品经理必须掌握的 **差异化硬技能**。

---

## 一、 核心思维差异：从“确定性”到“概率性”

| 维度 | 普通 PM (Web/Mobile) | **AI PM (Native)** |
| :--- | :--- | :--- |
| **产品定义** | 逻辑流 (If A then B) | **概率流** (当置信度 > 0.8 时出结果，否则怎么办？) |
| **核心资产** | 代码逻辑、用户关系链 | **高质量数据 (Golden Data)**、Prompt 资产、模型权重 |
| **验收标准** | Bug Free (功能完好) | **Bad Case 率** (幻觉率 < 5%, 拒答率 < 2%) |
| **性能关注** | 页面加载速度 (ms) | **首字延迟 (TTFT)**, **Token 生成速度 (TPS)** |
| **迭代方式** | 发版 (Release) | **微调 (Fine-tuning)** 或 **Prompt 优化** |

---

## 二、 五大硬核技术模块 (The Tech Stack for PMs)

### 1. 模型选型与成本建模 (Model Strategy & Unit Economics)
*AI PM 必须是半个架构师，能算清每一分钱的账。*

*   **能力要求**:
    *   **模型阶梯**: 秒懂 GPT-4o, Claude 3.5 Sonnet, Llama-3-70B, Qwen-7B 的区别。知道谁擅长逻辑，谁擅长写作，谁最便宜。
    *   **量化感知**: 知道 **FP16** vs **INT4** 量化对产品体验和成本的巨大影响（精度损失 vs 显存减半）。
    *   **成本计算**: 能熟练建立 Excel 模型：`DAU * Avg_Turns * Avg_Tokens * Price_Per_Token = Daily_Cost`。
*   **面试考题**:
    > "如果你要做一个免费的 C 端情感聊天助手，日活 100 万，你会选什么模型？如何保证不亏本？"
    > *(参考答案：必须用开源小模型 (7B/8B) 自行部署 + INT4 量化，利用闲时算力或端侧算力，绝不能直接调 GPT-4 API)*

### 2. 数据飞轮设计 (Data Flywheel Design)
*这是 AI 产品的护城河。AI PM 不写代码，但要设计“让用户不知不觉帮你标注数据”的机制。*

*   **能力要求**:
    *   **Implicit Feedback (隐式反馈)**: 不仅仅是“点赞/点踩”。如果用户复制了 AI 的回答，说明质量高；如果用户刷新了重试，说明质量差。你必须设计这种埋点。
    *   **SFT 数据构造**: 知道如何从 Log 中清洗出用于 Supervised Fine-Tuning 的数据对。
*   **面试考题**:
    > "我们的 RAG 搜索效果不好，作为 PM 你打算怎么做？"
    > *(错误答案：换个更强的模型。正确答案：建立 Bad Case 归因流程，让运营/专家标注正确答案，加入到 Golden Set，用于优化召回策略或微调。)*

### 3. 评估工程 (Evaluation Engineering)
*AI 是不可预测的“黑盒”，PM 必须构建“仪表盘”来监控它。*

*   **能力要求**:
    *   **Golden Dataset (金标集)**: 亲手维护 100-500 个覆盖各种 Corner Case 的测试用例。每次模型升级，必须先跑通这组数据。
    *   **Model-based Eval**: 知道怎么用 GPT-4 当裁判给你的小模型打分。
    *   **指标体系**: 区分 **Faithfulness** (是否忠实于原文) 和 **Relevance** (是否回答了问题)。

### 4. 提示词与上下文管理 (Prompting & Context)
*Prompt 是写给 AI 的产品文档。*

*   **能力要求**:
    *   **System Prompt 设计**: 能写出结构化、防御性强的 System Prompt（防止 Prompt Injection 攻击）。
    *   **Context Window 管理**: 知道当对话太长超过 128k 时，是切断最早的？还是通过 Summary 压缩中间的？这对用户体验意味着什么？

### 5. 伦理与安全 (Safety & Alignment)
*AI 可能会说脏话、会骗人，PM 是最后一道防线。*

*   **能力要求**:
    *   **敏感词过滤**: 知道如何在模型输出前加一层 Shield。
    *   **拒答策略**: 当用户问“怎么制造炸弹”时，如何优雅地拒绝而不是生硬地报错。

---

## 三、 基于 `enterprise-brain` 的 AI PM 实战任务

为了证明你是 AI PM，请不要画原型图，而是产出以下文档：

### 任务 1: 定义评估标准 (Evaluation Criteria)
*   **目标**: 为你的企业知识库定义“什么是好的回答”。
*   **动作**: 创建一个 Excel/Markdown 表格，列出 5 个典型的用户 Query，并分别写出：
    1.  **理想回答 (Ideal Answer)**。
    2.  **可接受的底线 (Acceptable Baseline)**。
    3.  **绝对错误的回答 (Failure Mode)** (比如：幻觉、泄露隐私)。

### 任务 2: 成本 vs 体验的 Trade-off 分析
*   **目标**: 决定是否开启“流式输出 (Streaming)”。
*   **分析**:
    *   流式输出优点：TTFT (首字延迟) 极低，用户感觉快。
    *   流式输出缺点：无法进行后置的内容审核（一旦输出脏话就来不及撤回了）。
    *   **决策**: 对于企业内部使用的 `enterprise-brain`，你选哪种？为什么？

### 任务 3: 数据回流机制
*   **目标**: 设计一个机制，当员工发现 AI 回答错误时，能一键修正。
*   **设计**: 在 UI 上加一个“编辑并提交”按钮。PM 需要定义：提交后的数据去哪里？是直接进向量库？还是进入人工审核列表？

---

## 推荐阅读 (AI PM 必读)

1.  **Shreyas Doshi 的产品思维** (关于 metrics definition).
2.  **OpenAI Cookbook** (特别是关于 Evaluation 和 Fine-tuning 的章节).
3.  **Leah's Guide to AI Product Management** (国外很火的 AI PM 专栏).
