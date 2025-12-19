# --- 第一阶段：选择地基 ---
FROM python:3.10-slim

# --- 第二阶段：安装工具 (uv) ---
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# --- 第三阶段：设置工作空间 ---
WORKDIR /app

# --- 第四阶段：安装依赖（核心技巧：分层） ---
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# --- 第五阶段：拷贝业务代码 ---
COPY . .

# --- 第六阶段：暴露端口 ---
EXPOSE 8080

# --- 第七阶段：启动程序 ---
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]