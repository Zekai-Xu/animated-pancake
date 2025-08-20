# 故障排除指南

> **AI学术论文监控系统常见问题解决方案**

## 🚨 当前遇到的问题：爬取结果为0篇论文

### 问题现象
```
INFO:main:论文爬取完成，共获得 0 篇论文
```

### 🔍 原因分析

#### 1. **ICLR 2025 数据未发布**
**最主要原因**: 2025年的学术会议论文通常还未正式发布

- **ICLR 2025**: 论文通常在2025年4-5月发布
- **CVPR 2025**: 论文通常在2025年3-4月发布  
- **NeurIPS 2025**: 论文通常在2025年9-10月发布

**当前状态**: 2025年8月，ICLR 2025可能还在审核阶段或刚开始发布

#### 2. **网站结构变化**
OpenReview等网站可能更新了页面结构，导致爬虫无法正确解析

#### 3. **反爬虫机制**
学术网站可能实施了更严格的反爬虫措施

#### 4. **网络连接问题**
代理设置或网络连接不稳定

## ✅ 解决方案

### 方案1: 使用已发布的数据（推荐）

```bash
# 使用Web界面
streamlit run gui.py

# 在界面中选择：
# 会议: ICLR
# 年份: 2024（而不是2025）
# 关键词: transformer, diffusion model
```

### 方案2: 命令行测试

```bash
# 测试ICLR 2024
python main.py --conferences ICLR --years 2024 --keywords "transformer" --verbose

# 测试多会议2023年数据
python main.py --conferences ICLR CVPR --years 2023 --keywords "deep learning" --verbose
```

### 方案3: 安装和环境检查

```bash
# 1. 检查Python环境
python3 --version  # 需要3.8+

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 运行系统测试
python3 quick_test.py

# 4. 使用启动脚本
chmod +x run.sh
./run.sh install  # 一键安装
./run.sh gui      # 启动界面
```

## 📋 推荐的测试配置

### 配置1: 稳定测试（最推荐）
- **会议**: ICLR
- **年份**: 2024
- **关键词**: transformer
- **原因**: ICLR 2024数据完整，transformer是热门关键词

### 配置2: 多会议测试
- **会议**: ICLR, CVPR
- **年份**: 2023
- **关键词**: deep learning
- **原因**: 2023年数据稳定，涵盖面广

### 配置3: 计算机视觉专题
- **会议**: CVPR
- **年份**: 2024
- **关键词**: object detection
- **原因**: CVPR是CV顶会，检测是热门方向

## 🛠️ 高级故障排除

### 检查Chrome驱动
```bash
# 检查Chrome版本
google-chrome --version

# 或者
chromium-browser --version

# 如果没有Chrome，安装：
# Ubuntu/Debian:
sudo apt update
sudo apt install google-chrome-stable

# CentOS/RHEL:
sudo yum install google-chrome-stable
```

### 检查网络连接
```bash
# 测试网络连接
curl -I https://openreview.net
curl -I https://openaccess.thecvf.com

# 如果需要代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

### 调试爬虫
```bash
# 运行调试脚本
python3 debug_iclr_2025.py

# 运行修复测试
python3 fix_crawler.py
```

## 📊 期望结果

### 正常运行时应该看到：
```
INFO:main:开始爬取论文数据
INFO:main:爬取 ICLR 2024
INFO:src.crawlers.openreview_crawler:开始爬取 ICLR 2024 论文
INFO:src.crawlers.openreview_crawler:找到 3 个论文分类: ['accepted-papers', 'poster-presentations', 'oral-presentations']
INFO:main:ICLR 2024 爬取完成: 150 篇论文  # 具体数量取决于关键词
INFO:main:论文爬取完成，共获得 150 篇论文
```

### 成功的Excel报告应包含：
- **论文概览**: 基本信息和评分
- **投资机会分析**: 高价值论文详情
- **技术趋势分析**: 领域分布和趋势
- **汇总统计**: 整体数据概览

## 🆘 仍然无法解决？

### 联系支持
1. **查看日志**: `tail -f logs/paper_monitor.log`
2. **提交Issue**: 包含错误日志和系统信息
3. **使用备用方案**: 手动下载论文数据

### 备用方案
如果爬虫持续失败，可以：
1. 直接访问会议网站手动收集数据
2. 使用学术搜索引擎（Google Scholar等）
3. 关注会议官方发布的论文列表

## 🔄 定期维护

### 月度检查
- 更新Chrome驱动
- 检查网站结构变化
- 更新配置文件

### 季度检查  
- 添加新会议支持
- 更新评分模型
- 优化爬虫性能

---

## 💡 快速修复命令

```bash
# 一键修复常见问题
./run.sh clean    # 清理缓存
./run.sh update   # 更新系统
./run.sh test     # 运行测试

# 重置环境
rm -rf venv/
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**记住**: 2025年的论文数据可能确实还未发布，这是正常现象。建议使用2023-2024年的数据进行测试和分析！