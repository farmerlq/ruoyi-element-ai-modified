# 使用官方Python运行时作为父镜像
FROM python:3.12-slim-bookworm

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 到工作目录
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY . .

# 创建非root用户
RUN adduser --uid 1001 --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER 1001

# 创建.env文件（如果不存在）
RUN if [ ! -f .env ]; then touch .env; fi

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]