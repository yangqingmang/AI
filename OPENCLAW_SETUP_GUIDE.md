# OpenClaw 完整搭建指南

> 最后更新：2026-02-09  
> 目标：让新手也能成功搭建并稳定运行 OpenClaw

---

## 目录

- [一、环境要求](#一环境要求)
- [二、方式一：Docker 部署（推荐）](#二方式一docker-部署推荐)
- [三、方式二：本地安装（Node.js）](#三方式二本地安装nodejs)
- [四、配置企业微信渠道](#四配置企业微信渠道)
- [五、配置模型 API](#五配置模型-api)
- [六、Web 控制台访问](#六web-控制台访问)
- [七、配置反向代理（Nginx）](#七配置反向代理nginx)
- [八、配置后台自动启动](#八配置后台自动启动)
- [九、常用命令速查](#九常用命令速查)
- [十、故障排查](#十故障排查)
- [十一、备份与迁移](#十一备份与迁移)
- [十二、推荐模型配置](#十二推荐模型配置)

---

## 一、环境要求

| 项目 | 要求 | 说明 |
|------|------|------|
| Node.js | >= 22 | 必须 |
| 内存 | 建议 4GB+ | 2GB 也能跑，但会卡 |
| 磁盘 | 10GB+ | 主要是日志和媒体文件 |
| 系统 | Ubuntu 22.04 LTS | Debian/macOS/Windows 也支持 |

**检查当前环境：**

```bash
# 检查 Node.js 版本
node --version

# 如果低于 v22，需要升级
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt-get install -y nodejs
```

---

## 二、方式一：Docker 部署（推荐）

> 适合服务器部署，隔离性好，迁移方便

### 2.1 安装 Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sudo sh

# 添加当前用户到 docker 组（免 sudo 运行）
sudo usermod -aG docker $USER

# 验证安装
docker --version          # 应显示 Docker version 24+
docker compose version    # 应显示 Docker Compose version v2+
```

**macOS/Windows**：安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 2.2 创建目录结构

```bash
# 创建配置目录
mkdir -p ~/.openclaw
cd ~/.openclaw

# 创建数据目录（可选，用于持久化）
mkdir -p data logs
```

### 2.3 创建配置文件

**方式 A：从源码构建（推荐）**

```bash
# 克隆仓库
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 构建镜像
docker build -t openclaw:local .

# 返回配置目录
cd ~/.openclaw
```

**方式 B：使用预构建镜像**

```yaml
# 创建 docker-compose.yml
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  openclaw-gateway:
    image: openclaw:local
    container_name: openclaw-gateway
    ports:
      - "18789:18789"
    volumes:
      - ~/.openclaw:/app/.openclaw
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "require('http').get('http://127.0.0.1:18789/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
```

### 2.4 启动服务

```bash
# 启动（后台运行）
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

### 2.5 验证启动成功

```bash
# 健康检查
curl http://127.0.0.1:18789/health

# 应该返回：{"status":"ok"}
```

---

## 三、方式二：本地安装（Node.js）

> 适合本地开发或不想用 Docker 的场景

### 3.1 安装 Node.js 22+

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt-get install -y nodejs

# macOS
brew install node@22

# 验证
node --version  # 应显示 v22.x
```

### 3.2 安装 OpenClaw

```bash
# 全局安装 CLI
npm install -g @openclaw/openclaw

# 或使用 pnpm（推荐，速度更快）
npm install -g pnpm
pnpm add -g @openclaw/openclaw
```

### 3.3 初始化配置

```bash
# 运行设置向导
openclaw setup
```

这会引导你完成：
- 创建配置文件 `~/.openclaw/openclaw.json`
- 配置默认模型
- 配置渠道（企业微信/Telegram等）

### 3.4 启动 Gateway

**前台运行（开发调试）：**

```bash
openclaw gateway --verbose
```

**后台运行：**

```bash
# Linux/macOS
openclaw gateway start

# 查看状态
openclaw status

# 停止
openclaw gateway stop
```

---

## 四、配置企业微信渠道

> 如果你已经在用，可以跳过此节

### 4.1 创建企业微信应用

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin)
2. 进入「应用管理」→「自建应用」
3. 点击「创建应用」
4. 填写信息：
   - 应用名称：`OpenClaw` 或任意名字
   - 应用logo：上传一张图
   - 应用描述：`AI 助手`
5. 创建成功后，记录以下信息：
   - AgentId（应用ID）
   - Secret（应用密钥）
   - CorpID（企业ID，在「我的企业」页查看）

### 4.2 配置 API 权限

在应用详情页，点击「API 权限」，确保勾选：
- [x] 接收消息
- [x] 发送消息
- [x] 通讯录读写（可选）

### 4.3 配置接收消息服务器

1. 在应用页点击「接收消息」→「设置API接收」
2. 点击「设置」，填写：
   - URL：`https://你的域名/wecom`（后面配好域名再改）
   - Token：随机字符串，保存好
   - EncodingAESKey：随机43位字符，点击「随机生成」

### 4.4 在 OpenClaw 中配置

```bash
# 编辑配置文件
openclaw config edit
```

添加或修改：

```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "corpId": "YOUR_CORP_ID",
      "agentId": "YOUR_AGENT_ID",
      "secret": "YOUR_SECRET",
      "token": "YOUR_TOKEN",
      "aesKey": "YOUR_AES_KEY"
    }
  }
}
```

### 4.5 验证企业微信连通

```bash
# 重启 Gateway
docker compose restart openclaw-gateway

# 或本地
openclaw gateway restart

# 查看日志
docker compose logs -f openclaw-gateway
```

在企业微信里给你的应用发条消息，看是否有响应。

---

## 五、配置模型 API

### 5.1 Anthropic（Claude，推荐）

1. 访问 https://console.anthropic.com/
2. 登录后点击「API Keys」→「Create Key」
3. 复制 Key，保存好（只会显示一次）

**在配置文件中设置：**

```json
{
  "agents": {
    "default": {
      "model": "claude-sonnet-4-20250514",
      "apiKey": "sk-ant-api03-YOUR_KEY_HERE"
    }
  }
}
```

**或使用环境变量：**

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
```

### 5.2 OpenAI（GPT-4）

1. 访问 https://platform.openai.com/api-keys
2. 创建 Key

**在配置文件中设置：**

```json
{
  "agents": {
    "default": {
      "model": "gpt-4o",
      "apiKey": "sk-YOUR_KEY_HERE"
    }
  }
}
```

### 5.3 配置默认模型

```json
{
  "agents": {
    "default": {
      "model": "claude-sonnet-4-20250514",
      "temperature": 0.7,
      "maxTokens": 4096
    }
  }
}
```

---

## 六、Web 控制台访问

### 6.1 本地访问

打开浏览器访问：

```
http://127.0.0.1:18789/
```

### 6.2 远程访问

需要先获取 Token：

```bash
# Docker 环境下
docker compose exec openclaw-cli openclaw dashboard --no-open

# 本地环境
openclaw dashboard
```

复制 Token，粘贴到控制台登录页。

### 6.3 配置允许列表（安全）

在配置文件中限制谁可以访问：

```json
{
  "gateway": {
    "mode": "local"
  },
  "security": {
    "allowFrom": ["127.0.0.1", "YOUR_IP"]
  }
}
```

---

## 七、配置反向代理（Nginx）

> 生产环境推荐使用，安全性更高

### 7.1 安装 Nginx

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl enable nginx
```

### 7.2 配置 SSL 证书（Let's Encrypt 免费）

```bash
# 安装 certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书（会自动配置 Nginx）
sudo certbot --nginx -d your-domain.com
```

### 7.3 Nginx 配置

```nginx
# /etc/nginx/sites-available/openclaw
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_read_timeout 86400;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7.4 更新企业微信回调地址

将企业微信的回调 URL 改为：

```
https://your-domain.com/wecom
```

---

## 八、配置后台自动启动

### 8.1 Systemd 服务（Linux 服务器）

创建服务文件：

```bash
sudo nano /etc/systemd/system/openclaw.service
```

内容：

```ini
[Unit]
Description=OpenClaw Gateway
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/$USER/.openclaw
ExecStart=/usr/local/bin/docker compose up -d
ExecStop=/usr/local/bin/docker compose down
User=$USER

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw.service
sudo systemctl start openclaw.service

# 查看状态
sudo systemctl status openclaw.service
```

### 8.2 Crontab 监控（备选方案）

```bash
# 编辑 crontab
crontab -e

# 添加（每分钟检查一次，未运行则启动）
* * * * * /usr/bin/docker ps --filter name=openclaw-gateway --format "{{.Names}}" | grep -q openclaw-gateway || cd /home/$USER/.openclaw && /usr/local/bin/docker compose up -d
```

---

## 九、常用命令速查

| 命令 | 说明 |
|------|------|
| `docker compose up -d` | 启动服务（后台） |
| `docker compose down` | 停止服务 |
| `docker compose restart` | 重启服务 |
| `docker compose logs -f` | 查看日志 |
| `docker compose logs -f --tail=100` | 查看最近100行日志 |
| `openclaw status` | 查看状态 |
| `openclaw config edit` | 编辑配置 |
| `openclaw config get` | 查看当前配置 |
| `openclaw health` | 健康检查 |
| `openclaw channels list` | 查看已配置渠道 |
| `openclaw update.run` | 更新版本 |

---

## 十、故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 端口被占用 | 18789 端口已用 | `openclaw gateway --port 18889` |
| 无法访问 | 防火墙阻止 | `sudo ufw allow 18789` |
| 企业微信无响应 | Token/AESKey 错误 | 检查配置，重新填写 |
| Token 无效 | Token 过期 | `openclaw dashboard` 重新获取 |
| 内存不足 | 进程崩溃 | `docker stats` 查看内存使用 |
| 镜像构建失败 | Docker 问题 | `docker system prune -a` 清理 |

### 查看完整日志

```bash
# Docker 环境
docker compose logs -f openclaw-gateway

# 本地环境
tail -f ~/.openclaw/logs/*.log
```

### 重置所有配置

```bash
# 危险！会删除所有配置
rm -rf ~/.openclaw
openclaw setup
```

---

## 十一、备份与迁移

### 11.1 备份

```bash
# 打包配置目录
cd /home/$USER
tar -czvf openclaw_backup_$(date +%Y%m%d).tar.gz .openclaw/

# 或使用 rsync 增量备份
rsync -av ~/.openclaw/ /backup/path/
```

### 11.2 迁移到新服务器

```bash
# 1. 在旧服务器打包
tar -czvf openclaw_backup.tar.gz .openclaw/

# 2. 传输到新服务器
scp openclaw_backup.tar.gz user@new-server:~/

# 3. 在新服务器恢复
mkdir -p ~/.openclaw
tar -xzvf openclaw_backup.tar.gz -C ~/

# 4. 重启服务
docker compose restart
```

---

## 十二、推荐模型配置

根据社区经验，推荐模型组合：

| 场景 | 模型 | 特点 |
|------|------|------|
| **日常对话** | Claude Sonnet 4 | 性价比高，响应快 |
| **复杂任务** | Claude Opus 4 | 能力最强，适合长程任务 |
| **代码任务** | GPT-5.2-Codex | 代码专项优化 |
| **快速草稿** | Claude Haiku 3 | 最快最便宜 |

### 多模型切换配置

```json
{
  "agents": {
    "default": {
      "model": "claude-sonnet-4-20250514",
      "temperature": 0.7
    },
    "coder": {
      "model": "gpt-5.2-codex-20250514",
      "temperature": 0.2
    }
  }
}
```

---

## 十三、参考链接

| 资源 | 链接 |
|------|------|
| 官方文档 | https://docs.openclaw.ai |
| GitHub | https://github.com/openclaw/openclaw |
| 社区 Discord | https://discord.com/invite/clawd |
| 刘小排文章 | 搜索公众号「一人公司」 |

---

## 十四、快速上手清单

完成搭建后，按这个清单检查：

- [ ] Docker/Node.js 安装成功
- [ ] Gateway 启动成功 (`docker ps` 或 `openclaw status`)
- [ ] Web 控制台能访问
- [ ] 企业微信能发消息收到响应
- [ ] API Key 配置正确
- [ ] 配置文件已保存
- [ ] 后台自启动已配置
- [ ] SSL 证书已配置（如有域名）

---

**祝你搭建顺利！** 🚀
