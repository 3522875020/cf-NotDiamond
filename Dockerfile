FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 首先复制必要的文件
COPY requirements.txt setup.py ./
COPY notdiamond notdiamond/

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 安装本地包
RUN pip install -e .

# 复制其余应用代码
COPY main.py .env ./

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV NOTDIAMOND_API_KEY=""
ENV OPENAI_API_KEY=""

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 