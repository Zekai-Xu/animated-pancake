# AI学术论文监控系统

> **专为AI投资人设计的学术论文监控和分析平台**  
> *Academic Paper Monitoring Platform for AI Investors*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

## 🎯 项目简介

AI学术论文监控系统是一个专门为AI领域投资人设计的智能化论文分析工具。系统能够实时爬取主流AI学术会议的论文数据，通过多维度量化评分模型对论文进行投资价值分析，并生成专业的Excel报告，帮助投资人快速识别具有商业化潜力的前沿技术。

### 🔥 核心功能

- **🕷️ 智能爬虫**: 支持ICLR、CVPR、ICCV、NeurIPS等主流AI会议
- **📊 投资评分**: 基于引用数、技术深度、商业潜力等多维度智能评分
- **💼 投资分析**: 专业的投资价值分析和建议
- **📈 趋势洞察**: 技术趋势分析和市场前景评估
- **📋 Excel报告**: 生成专业的分析报告，包含详细数据和图表
- **🖥️ 友好界面**: 基于Streamlit的直观Web界面
- **⚙️ 灵活配置**: 支持自定义关键词、日期范围等过滤条件

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Chrome浏览器 (用于网页爬取)
- 8GB+ 内存推荐

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/ai-paper-monitor.git
cd ai-paper-monitor
```

2. **创建虚拟环境**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **创建必要目录**
```bash
mkdir -p logs data output
```

### 🖥️ 使用Web界面 (推荐)

启动Web界面：
```bash
streamlit run gui.py
```

然后在浏览器中打开 `http://localhost:8501`

#### Web界面功能

- **📋 配置面板**: 选择会议、年份、关键词等
- **📊 实时监控**: 查看爬取进度和实时统计
- **📈 可视化分析**: 投资评分分布、技术趋势图表
- **⭐ 论文推荐**: 高价值论文详情展示
- **📥 报告下载**: 一键生成和下载Excel报告

### 💻 使用命令行界面

#### 基础用法

```bash
# 爬取所有支持会议的最近3年论文
python main.py

# 指定会议和年份
python main.py --conferences ICLR CVPR --years 2023 2024

# 使用关键词过滤
python main.py --keywords "transformer" "diffusion model" "large language model"

# 指定输出文件
python main.py --output reports/ai_papers_2024.xlsx
```

#### 高级用法

```bash
# 指定日期范围
python main.py --date-from 2024-01-01 --date-to 2024-12-31

# 详细输出模式
python main.py --verbose

# 使用自定义配置文件
python main.py --config custom_config.yaml

# 综合示例
python main.py \
    --conferences ICLR CVPR NeurIPS \
    --years 2023 2024 \
    --keywords "transformer" "diffusion" "multimodal" \
    --output analysis_2024.xlsx \
    --verbose
```

## 📊 系统架构

```
ai-paper-monitor/
├── src/                          # 源代码目录
│   ├── core/                     # 核心模块
│   │   └── database.py          # 数据库管理
│   ├── crawlers/                # 爬虫模块
│   │   ├── base_crawler.py      # 基础爬虫类
│   │   ├── openreview_crawler.py # OpenReview爬虫
│   │   └── cvf_crawler.py       # CVF网站爬虫
│   ├── scoring/                 # 评分模块
│   │   └── investment_scorer.py # 投资评分器
│   └── export/                  # 导出模块
│       └── excel_exporter.py    # Excel导出器
├── config/                      # 配置文件
│   └── config.yaml             # 主配置文件
├── data/                       # 数据存储
├── logs/                       # 日志文件
├── output/                     # 输出报告
├── main.py                     # 命令行主程序
├── gui.py                      # Web界面程序
└── README.md                   # 说明文档
```

## 🎯 评分体系

### 投资评分模型 (1-10分)

系统采用多维度加权评分模型：

| 维度 | 权重 | 说明 |
|------|------|------|
| **引用次数** | 25% | 论文的学术影响力 |
| **引用增长率** | 20% | 近期关注度趋势 |
| **作者H指数** | 15% | 作者学术声誉 |
| **会议影响因子** | 15% | 发表平台权威性 |
| **新颖性评分** | 10% | 技术创新程度 |
| **技术深度** | 10% | 技术复杂度和实现难度 |
| **商业潜力** | 5% | 市场应用前景 |

### 投资建议分级

- **🔥 强烈推荐 (8.0+)**: 具有极高投资价值的突破性技术
- **⭐ 推荐关注 (6.5-8.0)**: 具有良好投资潜力的优质论文
- **👀 一般关注 (5.0-6.5)**: 有一定价值但需观察的技术
- **📝 暂不关注 (<5.0)**: 投资价值有限的研究

## 📋 支持的会议

### 计算机视觉 (Computer Vision)
- **CVPR** - IEEE Conference on Computer Vision and Pattern Recognition
- **ICCV** - IEEE International Conference on Computer Vision  
- **ECCV** - European Conference on Computer Vision
- **WACV** - Winter Conference on Applications of Computer Vision

### 机器学习 (Machine Learning)
- **ICLR** - International Conference on Learning Representations
- **ICML** - International Conference on Machine Learning
- **NeurIPS** - Conference on Neural Information Processing Systems

### 人工智能 (Artificial Intelligence)
- **AAAI** - AAAI Conference on Artificial Intelligence
- **IJCAI** - International Joint Conference on Artificial Intelligence

## 📈 输出报告

系统生成的Excel报告包含以下工作表：

### 1. 论文概览
- 论文基本信息 (标题、作者、会议、年份)
- 投资评分和建议
- 引用数据和增长趋势
- 技术指标 (深度、新颖性、商业潜力)

### 2. 投资机会分析  
- 高价值论文详细分析
- 作者和机构信息
- 联系方式和合作机会
- 投资建议和风险评估

### 3. 技术趋势分析
- 技术领域分布统计
- 发展趋势和增长预测
- 市场前景和竞争分析
- 投资热度排名

### 4. 汇总统计
- 整体数据概览
- 会议对比分析
- 关键指标统计

## ⚙️ 配置说明

### 主配置文件 (config/config.yaml)

```yaml
# 数据库配置
database:
  type: "sqlite"
  path: "data/papers.db"

# 爬虫配置  
crawler:
  proxy:
    enabled: false
    http: "http://127.0.0.1:7890"
  request:
    timeout: 30
    max_retries: 5

# 评分权重配置
scoring:
  weights:
    citation_count: 0.25
    citation_growth: 0.20
    author_h_index: 0.15
    # ... 更多配置

# 投资关键词
investment_keywords:
  hot_topics:
    - "Large Language Model"
    - "Diffusion Model"
    - "Multimodal"
    # ... 更多关键词
```

### 环境变量配置

创建 `.env` 文件：
```bash
# 代理设置 (可选)
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# 数据库路径
DATABASE_PATH=data/papers.db

# 日志级别
LOG_LEVEL=INFO
```

## 🛠️ 高级功能

### 1. 自定义评分权重

```python
# 修改 config/config.yaml 中的权重配置
scoring:
  weights:
    citation_count: 0.30      # 增加引用权重
    commercial_potential: 0.15 # 增加商业权重
```

### 2. 添加新的会议支持

```python
# 在 src/crawlers/ 目录下创建新的爬虫类
class NewConferenceCrawler(BaseCrawler):
    def crawl_papers(self, conference, year, keywords=None):
        # 实现具体的爬取逻辑
        pass
```

### 3. 自定义投资指标

```python
# 在 InvestmentScorer 类中添加新的评分方法
def calculate_custom_score(self, paper_data):
    # 实现自定义评分逻辑
    return score
```

## 🔧 故障排除

### 常见问题

1. **Chrome驱动问题**
   ```bash
   # 系统会自动下载Chrome驱动，如遇问题请手动安装
   pip install webdriver-manager
   ```

2. **网络连接问题**
   ```bash
   # 配置代理 (如需要)
   export HTTP_PROXY=http://127.0.0.1:7890
   export HTTPS_PROXY=http://127.0.0.1:7890
   ```

3. **内存不足**
   ```bash
   # 减少并发数或分批处理
   python main.py --conferences ICLR --years 2024
   ```

4. **权限问题**
   ```bash
   # 确保有写入权限
   chmod -R 755 data/ logs/ output/
   ```

### 日志分析

查看详细日志：
```bash
tail -f logs/paper_monitor.log
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black src/
flake8 src/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenReview](https://openreview.net/) - 提供ICLR、ICML等会议数据
- [CVF Open Access](https://openaccess.thecvf.com/) - 提供CVPR、ICCV等会议数据  
- [Scholarly](https://github.com/scholarly-python-package/scholarly) - 学术数据获取
- [Streamlit](https://streamlit.io/) - Web界面框架

## 📞 联系方式

- 项目主页: https://github.com/your-username/ai-paper-monitor
- 问题反馈: https://github.com/your-username/ai-paper-monitor/issues
- 邮箱: your-email@example.com

---

<div align="center">

**🌟 如果这个项目对您有帮助，请给它一个星标！**

*让AI投资决策更加智能化* ✨

</div>