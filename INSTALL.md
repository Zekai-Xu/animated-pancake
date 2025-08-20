# 安装和部署指南

> **AI学术论文监控系统详细安装说明**

## 📋 系统要求

### 硬件要求
- **CPU**: 2核心及以上
- **内存**: 8GB RAM (推荐16GB)
- **存储**: 5GB可用空间
- **网络**: 稳定的互联网连接

### 软件要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **浏览器**: Chrome 90+ (用于网页爬取)

## 🚀 快速安装

### 方法一：使用Git克隆 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/your-username/ai-paper-monitor.git
cd ai-paper-monitor

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac  
source venv/bin/activate

# 4. 升级pip
python -m pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 创建必要目录
mkdir -p logs data output config
```

### 方法二：下载ZIP包

1. 从GitHub下载项目ZIP包
2. 解压到目标目录
3. 按照上述步骤3-6执行

## 🔧 详细配置

### 1. 环境变量配置

创建 `.env` 文件：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

`.env` 文件内容：
```bash
# 数据库配置
DATABASE_PATH=data/papers.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/paper_monitor.log

# 代理配置 (如需要)
HTTP_PROXY=
HTTPS_PROXY=

# Chrome驱动配置
CHROME_HEADLESS=true
CHROME_NO_SANDBOX=true

# API配置 (可选)
SCHOLARLY_ENABLED=false
ARXIV_ENABLED=false
```

### 2. 配置文件设置

编辑 `config/config.yaml`：

```yaml
# 数据库配置
database:
  type: "sqlite"
  path: "data/papers.db"
  backup_enabled: true
  backup_interval_days: 7

# 爬虫配置
crawler:
  # 代理设置
  proxy:
    enabled: false
    http: "http://127.0.0.1:7890"
    https: "http://127.0.0.1:7890"
  
  # 请求设置
  request:
    timeout: 30
    max_retries: 5
    retry_delay: 10
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 更多配置项...
```

### 3. Chrome驱动安装

系统会自动下载Chrome驱动，但如遇问题可手动安装：

```bash
# 安装Chrome驱动管理器
pip install webdriver-manager

# 验证Chrome安装
google-chrome --version  # Linux
# 或
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version  # Windows
```

## 🧪 验证安装

### 1. 基础功能测试

```bash
# 测试Python环境
python --version

# 测试依赖包
python -c "import requests, beautifulsoup4, selenium, pandas, openpyxl; print('All packages imported successfully')"

# 测试数据库连接
python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); print('Database connection successful'); db.close()"
```

### 2. 运行简单测试

```bash
# 运行帮助命令
python main.py --help

# 测试配置加载
python -c "import yaml; config = yaml.safe_load(open('config/config.yaml')); print('Config loaded successfully')"

# 测试Web界面
streamlit run gui.py --server.port 8501 --server.headless true
```

### 3. 完整功能测试

```bash
# 运行小规模测试 (爬取少量数据)
python main.py --conferences ICLR --years 2024 --keywords "transformer" --verbose
```

## 🐳 Docker部署 (可选)

### 1. 使用Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要目录
RUN mkdir -p logs data output

# 设置环境变量
ENV PYTHONPATH=/app
ENV CHROME_HEADLESS=true

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "gui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

构建和运行：

```bash
# 构建镜像
docker build -t ai-paper-monitor .

# 运行容器
docker run -p 8501:8501 -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output ai-paper-monitor
```

### 2. 使用Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  ai-paper-monitor:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - CHROME_HEADLESS=true
      - LOG_LEVEL=INFO
    restart: unless-stopped

  # 可选：添加数据库服务
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: papers
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

运行：

```bash
docker-compose up -d
```

## 🌐 生产环境部署

### 1. 使用Nginx反向代理

安装Nginx：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

配置Nginx (`/etc/nginx/sites-available/ai-paper-monitor`)：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/ai-paper-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. 使用Systemd服务

创建服务文件 (`/etc/systemd/system/ai-paper-monitor.service`)：

```ini
[Unit]
Description=AI Paper Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai-paper-monitor
Environment=PATH=/path/to/ai-paper-monitor/venv/bin
ExecStart=/path/to/ai-paper-monitor/venv/bin/streamlit run gui.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-paper-monitor
sudo systemctl start ai-paper-monitor
```

### 3. SSL证书配置 (使用Let's Encrypt)

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. Chrome驱动问题

**问题**: ChromeDriver版本不匹配
```bash
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version X
```

**解决方案**:
```bash
# 更新Chrome驱动
pip install --upgrade webdriver-manager

# 或手动指定Chrome路径
export CHROME_BIN=/usr/bin/google-chrome
```

#### 2. 权限问题

**问题**: 无法创建文件或目录
```bash
PermissionError: [Errno 13] Permission denied: 'data/papers.db'
```

**解决方案**:
```bash
# 修改目录权限
sudo chown -R $USER:$USER .
chmod -R 755 data/ logs/ output/

# 或使用sudo运行 (不推荐)
sudo python main.py
```

#### 3. 内存不足

**问题**: 处理大量数据时内存溢出
```bash
MemoryError: Unable to allocate array
```

**解决方案**:
```bash
# 分批处理数据
python main.py --conferences ICLR --years 2024
python main.py --conferences CVPR --years 2024

# 或增加虚拟内存
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 网络连接问题

**问题**: 网络超时或连接被拒绝
```bash
requests.exceptions.ConnectTimeout: HTTPSConnectionPool
```

**解决方案**:
```bash
# 配置代理
export HTTP_PROXY=http://proxy-server:port
export HTTPS_PROXY=http://proxy-server:port

# 或修改超时设置
# 在config.yaml中增加timeout值
```

#### 5. 依赖包冲突

**问题**: 包版本冲突
```bash
pip._internal.exceptions.DistributionNotFound: No matching distribution found
```

**解决方案**:
```bash
# 清理pip缓存
pip cache purge

# 重新创建虚拟环境
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 或使用conda环境
conda create -n ai-paper-monitor python=3.9
conda activate ai-paper-monitor
pip install -r requirements.txt
```

### 性能优化

#### 1. 数据库优化

```sql
-- 为常用查询创建索引
CREATE INDEX idx_papers_conference_year ON papers(conference, year);
CREATE INDEX idx_papers_investment_score ON papers(investment_score);
CREATE INDEX idx_papers_created_at ON papers(created_at);
```

#### 2. 爬虫优化

```python
# 在config.yaml中调整爬虫参数
crawler:
  request:
    timeout: 60  # 增加超时时间
    max_retries: 3  # 减少重试次数
    retry_delay: 5  # 减少重试延迟
  chrome:
    headless: true  # 使用无头模式
    disable_gpu: true  # 禁用GPU
    no_sandbox: true  # 禁用沙箱
```

#### 3. 内存管理

```python
# 分批处理大量数据
def process_papers_in_batches(papers, batch_size=100):
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        # 处理批次
        yield batch
```

## 📞 技术支持

如果遇到安装问题，请：

1. 查看 [FAQ](FAQ.md) 文档
2. 搜索 [GitHub Issues](https://github.com/your-username/ai-paper-monitor/issues)
3. 提交新的Issue，包含：
   - 操作系统信息
   - Python版本
   - 错误日志
   - 复现步骤

## 🔄 更新升级

### 更新到最新版本

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 备份数据库
cp data/papers.db data/papers.db.backup

# 运行数据库迁移 (如有)
python manage.py migrate
```

### 版本回滚

```bash
# 查看版本历史
git log --oneline

# 回滚到指定版本
git checkout <commit-hash>

# 恢复数据库备份
cp data/papers.db.backup data/papers.db
```

---

**安装完成后，请查看 [README.md](README.md) 了解使用方法！** 🎉