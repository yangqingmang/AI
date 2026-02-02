# Enterprise Brain Pro (RAGFlow Edition) 部署指南

本指南适用于 **高性能生产环境** (CPU >= 8核, RAM >= 32GB)，将部署完整的 RAGFlow 引擎作为底层知识库，替代本地轻量级方案。

## 1. 硬件要求

| 组件 | 最低配置 | 推荐配置 |
| :--- | :--- | :--- |
| **CPU** | 4 Cores | 8 Cores+ |
| **RAM** | 16 GB | **32 GB+** (关键) |
| **Disk** | 50 GB SSD | 500 GB NVMe SSD |
| **OS** | Ubuntu 22.04 / CentOS 7+ | Ubuntu 22.04 LTS |

> **注意**: 必须安装 Docker 和 Docker Compose (v2.x)。
> `vm.max_map_count` 必须设置为 >= 262144 (Elasticsearch 要求)。
> `sysctl -w vm.max_map_count=262144`

## 2. 部署架构

部署将启动以下容器群：

*   **应用层**:
    *   `enterprise-brain-frontend`: 用户界面 (Streamlit)
    *   `enterprise-brain-backend`: 业务逻辑 (FastAPI)
*   **RAGFlow 核心层**:
    *   `ragflow-server`: RAG 核心引擎
    *   `ragflow-minio`: 文件存储
    *   `ragflow-es`: 向量与全文索引 (Elasticsearch)
    *   `ragflow-mysql`: 元数据存储
    *   `ragflow-redis`: 缓存与任务队列

## 3. 一键部署 (Linux/Mac)

```bash
# 1. 下载部署包 (假设已解压到 /opt/enterprise-brain)
cd /opt/enterprise-brain

# 2. 设置系统参数 (ES 需要)
sudo sysctl -w vm.max_map_count=262144

# 3. 启动 RAGFlow 版
./deploy_pro.sh
```

## 4. 验证部署

1.  **Enterprise Brain (前端)**: `http://<SERVER_IP>:8501`
2.  **RAGFlow Console (管理后台)**: `http://<SERVER_IP>:9380`
    *   默认账号: `admin` / `admin` (请登录后立即修改)

## 5. 配置对接

脚本会自动生成 `.env` 文件。如果需要手动修改，请确保 `enterprise-brain/.env` 中包含：

```ini
RAG_ENGINE=ragflow
RAGFLOW_BASE_URL=http://ragflow-server:9380
RAGFLOW_API_KEY=<你的_RAGFLOW_API_KEY> 
# 注意: 初次部署可能需要去 RAGFlow 后台生成一个 API Key 并填入此处
```

## 6. 故障排查

*   **内存不足**: 如果 ES 启动失败，检查 `docker logs ragflow-es`，通常是因为内存不足被 OOM Kill。
*   **连接失败**: 确保 backend 容器和 ragflow 容器在同一个 docker network 中 (脚本已处理)。
