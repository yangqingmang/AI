# 反 AI 依赖：如何通过“指挥 AI”实现技术飞跃

**核心原则**: AI 是你的实习生，不是你的架构师。你必须具备 Review 它的能力，这才是 P7 的能力。

---

## 一、 架构层面的深度干预 (Architectural Intervention)

**不要让 AI 决定你的文件结构和技术选型。**

*   **错误做法**: "Hey AI, 帮我写一个 RAG 系统。" (然后全盘接受它生成的 app.py)。
*   **升级做法**:
    1.  **你画图**: 先在纸上或 Excalidraw 画出数据流图。
        *   用户 Query -> Query Rewrite (你设计的) -> Vector DB -> Re-rank (你要求的) -> LLM -> Answer。
    2.  **你指令**: "我要实现上面的架构。请帮我写 Vector DB 的连接模块，但我要求使用 `pgvector` 而不是 `chromadb`，因为我们需要和现有 PostgreSQL 业务数据做 Join。"
    3.  **你审查**: AI 可能会忘记加索引，或者忘记做连接池复用。**你必须指出来**。如果你看不出这些问题，这就是你现在的**技能缺口**，去补这块知识，而不是让 AI 重生一次。

## 二、 逻辑层面的“白盒化” (Logic White-boxing)

**不要只看结果，要看中间过程。**

*   **场景**: AI 帮你写了一个 `ingest.py` 来切分 PDF 文档。
*   **升级做法**:
    1.  **质疑默认值**: AI 通常会默认 `chunk_size=1000`。
    2.  **深度思考**: "对于我们公司的合同文档，1000 字符会不会把‘甲方权利’和‘乙方义务’切断了？"
    3.  **手动调试**: 打印出前 5 个 Chunk 看看。发现果然切坏了。
    4.  **修正**: 要求 AI 改用 `RecursiveCharacterTextSplitter`，并强制在“第几条”这样的正则处切分。
    *   **收获**: 你学会了**Chunking Strategy**，这是 RAG 核心技术点。

## 三、 评测驱动开发 (Evaluation Driven Development)

**AI 可以帮你写功能，但不能帮你定义“好”。**

*   **场景**: 项目跑起来了，能回答问题。
*   **升级做法**:
    1.  **构建 Bad Case**: 找 5 个 AI 回答得一塌糊涂的问题。
    2.  **归因分析 (Root Cause Analysis)**:
        *   是召回没召回对？(看 Log 里的 `retrieved_docs`)
        *   还是召回对了但 LLM 没读懂？(看 Prompt)
    3.  **优化循环**:
        *   如果是召回问题，尝试让 AI 引入 `Hybrid Search` (关键词+向量)。
        *   如果是 LLM 问题，尝试优化 Prompt 的 `Chain-of-Thought`。
    *   **收获**: 这就是张和说的“自动驾驶数据闭环”在 LLM 里的体现。

## 四、 性能与成本的极限压榨 (Performance & Cost)

**AI 写出的代码通常是“能跑就行”，也是性能最差的。**

*   **场景**: 处理 100 个文件很慢。
*   **升级做法**:
    1.  **Profiler**: 不要猜。运行 `cProfile` 或看日志时间戳。
    2.  **发现瓶颈**: 发现 AI 用了单线程 `for` 循环去请求 OpenAI API。
    3.  **重构**: 要求 AI 改写成 `asyncio` 并发，或者使用 `ThreadPoolExecutor`。
    4.  **计算 ROI**: "并发改写后，速度提升了 10 倍，但 Token 消耗速率变快了，触发了 API Rate Limit。如何加 Backoff 重试机制？"

---

## 总结：你的新工作流

1.  **Think First**: 动手前，先写文档/画图。想清楚这里面的难点在哪。
2.  **AI Coding**: 用 Cursor 生成代码块。
3.  **Code Review**: 像审查实习生代码一样审查 AI 的代码。
    *   "这里为什么没做异常处理？"
    *   "这里是不是会有 SQL 注入风险？"
    *   "这个变量命名不符合 PEP8。"
4.  **Debug & Optimize**: 遇到 Bug 时，不要盲目 Regenerate。**读报错栈 (Stack Trace)**，理解为什么错，再告诉 AI 怎么改。

**每一次你指出 AI 的不足并纠正它的过程，就是你在升级的过程。**
