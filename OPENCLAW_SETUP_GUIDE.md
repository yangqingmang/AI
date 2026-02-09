# OpenClaw 完整搭建指南

> 最后更新：2026-02-09

## 一、环境要求

| 项目 | 要求 |
|------|------|
| Node.js | >= 22 |
| 内存 | 建议 4GB+ |
| 磁盘 | 10GB+ |
| 系统 | Ubuntu 22.04 / macOS / Windows |

---

## 二、方式一：Docker 部署（推荐）

### 2.1 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh

# 验证
docker --version
docker-compose --version
```

### 2.2 创建目录

```bash
mkdir -p ~/.openclaw
cd ~/.openclaw
```

### 2.3 创建 docker-compose.yml

```bash
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  openclaw-gateway:
    image: openclaw/openclaw:latest
    ports:
      - "18789:18789"
    volumes:
      - ~/.openclaw:/app/.openclaw
    restart: unless-stopped

  openclaw-cli:
    image: openclaw/openclaw:latest
    volumes:
      - ~/.openclaw:/app/.openclaw
    environment:
      - OPENCLAW_GATEWAY_URL=http://openclaw-gateway:18789
EOF
```

### 2.4 启动

```bash
# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 2.5 初始化配置

```bash
# 进入容器
docker-compose exec openclaw-cli bash

# 运行初始化向导
openclaw setup
```

### 2.6 配置模型 API Key

```bash
# 设置 Anthropic API Key（推荐 Claude）
export ANTHROPIC_API_KEY="sk-ant-api03-xxx"

# 或设置 OpenAI
export OPENAI_API_KEY="sk-xxx"
```

---

## 三、方式二：本地安装（Node.js）

### 3.1 安装 Node.js 22+

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

# 验证
node --version  # 应显示 v22.x
```

### 3.2 安装 OpenClaw

```bash
# 全局安装
npm install -g @openclaw/openclaw

# 或用 pnpm
pnpm add -g @openclaw/openclaw
```

### 3.3 初始化

```bash
# 运行设置向导
openclaw setup
```

### 3.4 启动 Gateway

```bash
# 前台运行
openclaw gateway

# 或后台运行
openclaw gateway start

# 查看状态
openclaw status
```

---

## 四、配置渠道

### 4.1 企业微信（已配置）

```bash
# 查看当前配置
openclaw config get
```

### 4.2 Telegram

```bash
# 添加 Telegram Bot
openclaw channels add --channel telegram --token "YOUR_BOT_TOKEN"
```

### 4.3 WhatsApp

```bash
# 扫码登录
openclaw channels login --channel whatsapp
```

### 4.4 Discord

```bash
# 添加 Discord Bot
openclaw channels add --channel discord --token "YOUR_BOT_TOKEN"
```

---

## 五、Web 控制台

### 5.1 访问地址

- 本地：`http://127.0.0.1:18789/`
- 远程：`http://你的服务器IP:18789/`

### 5.2 登录

首次访问需要：
1. 输入 Gateway Token
2. 配对设备（手机/浏览器）

```bash
# 获取 Token
openclaw dashboard
```

---

## 六、配置文件说明

### 6.1 默认位置

```
~/.openclaw/openclaw.json
```

### 6.2 示例配置

```json
{
  "gateway": {
    "port": 18789,
    "mode": "remote"
  },
  "channels": {
    "wecom": {
      "enabled": true
    },
    "telegram": {
      "enabled": false
    },
    "whatsapp": {
      "enabled": false
    }
  },
  "agents": {
    "default": {
      "model": "claude-sonnet-4-20250514"
    }
  }
}
```

---

## 七、常用命令速查

| 命令 | 说明 |
|------|------|
| `openclaw gateway start` | 启动 Gateway |
| `openclaw gateway stop` | 停止 Gateway |
| `openclaw status` | 查看状态 |
| `openclaw config edit` | 编辑配置 |
| `openclaw channels list` | 查看已配置渠道 |
| `openclaw update.run` | 更新版本 |
| `openclaw health` | 健康检查 |

---

## 八、备份与恢复

### 8.1 备份

```bash
# 备份整个配置
cp -r ~/.openclaw ~/openclaw_backup_$(date +%Y%m%d)
```

### 8.2 恢复

```bash
# 迁移到新服务器
scp -r ~/openclaw_backup_* user@new-server:~/
```

---

## 九、故障排查

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | `openclaw gateway --port 18889` 换端口 |
| Token 无效 | `openclaw dashboard` 重新获取 |
| 渠道无法连接 | `openclaw channels login` 重新登录 |
| 内存不足 | 检查 `docker stats` 或 `htop` |

---

## 十、推荐模型配置

根据刘小排的经验，推荐模型：

| 场景 | 模型 | 说明 |
|------|------|------|
| 综合任务 | Claude Opus 4 | 通用能力最强 |
| 编程任务 | GPT-5.2-Codex | 代码专项优化 |
| 日常对话 | Claude Sonnet 4 | 性价比高 |

---

## 十一、一人公司进阶路径

| 阶段 | 目标 | 关键动作 |
|------|------|----------|
| 入门 | 日常任务自动化 | 写好记忆、熟悉工具链 |
| 进阶 | 多渠道接入 | 飞书、Telegram、Discord 都接 |
| 高阶 | 全流程自动化 | 搭 SOP、AI 自己闭环 |
| 顶峰 | 一人公司 | 只做人设判断，剩下 AI 干 |

---

## 参考资料

- 官方文档：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- 社区：https://discord.com/invite/clawd
