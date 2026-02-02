# 使用轻量级 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 防止 Python 生成 pyc 文件，并开启无缓冲输出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY enterprise-brain/requirements.txt .

# 安装依赖 (使用国内源加速)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

# 复制项目代码
COPY enterprise-brain/ .

# 创建必要的目录
RUN mkdir -p data chroma_db

# 暴露端口 (仅作为文档)
EXPOSE 8000 8501
