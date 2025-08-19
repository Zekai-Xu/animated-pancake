# API文档

> **AI学术论文监控系统 API 参考文档**

## 📋 概述

本文档描述了AI学术论文监控系统的核心API接口，包括数据库操作、爬虫接口、评分系统和导出功能。

## 🗄️ 数据库API

### DatabaseManager

数据库管理器，负责论文数据的存储和检索。

#### 初始化

```python
from src.core.database import DatabaseManager

db = DatabaseManager(db_path="data/papers.db")
```

#### 方法列表

##### `add_paper(paper_data: Dict) -> int`

添加新论文到数据库。

**参数:**
- `paper_data` (Dict): 论文数据字典

**返回:**
- `int`: 新添加论文的ID

**示例:**
```python
paper_data = {
    'title': 'Attention Is All You Need',
    'authors': '["Ashish Vaswani", "Noam Shazeer"]',
    'conference': 'NeurIPS',
    'year': 2017,
    'abstract': 'The dominant sequence transduction models...',
    'investment_score': 9.5
}

paper_id = db.add_paper(paper_data)
print(f"Added paper with ID: {paper_id}")
```

##### `search_papers(keywords=None, conferences=None, years=None, ...) -> List[Paper]`

搜索论文数据。

**参数:**
- `keywords` (Optional[List[str]]): 关键词列表
- `conferences` (Optional[List[str]]): 会议列表
- `years` (Optional[List[int]]): 年份列表
- `min_investment_score` (Optional[float]): 最小投资评分
- `min_citation_count` (Optional[int]): 最小引用数
- `date_from` (Optional[datetime]): 开始日期
- `date_to` (Optional[datetime]): 结束日期
- `limit` (int): 结果限制，默认1000

**返回:**
- `List[Paper]`: 论文对象列表

**示例:**
```python
# 搜索transformer相关的高价值论文
papers = db.search_papers(
    keywords=['transformer', 'attention'],
    conferences=['NeurIPS', 'ICLR'],
    min_investment_score=8.0,
    limit=50
)

for paper in papers:
    print(f"{paper.title} - Score: {paper.investment_score}")
```

##### `get_papers_dataframe(search_params=None) -> pd.DataFrame`

获取论文数据的DataFrame格式。

**参数:**
- `search_params` (Optional[Dict]): 搜索参数字典

**返回:**
- `pd.DataFrame`: 论文数据DataFrame

**示例:**
```python
# 获取所有高价值论文的DataFrame
df = db.get_papers_dataframe({
    'min_investment_score': 7.0
})

print(df.head())
print(f"Shape: {df.shape}")
```

##### `get_statistics() -> Dict`

获取数据库统计信息。

**返回:**
- `Dict`: 统计信息字典

**示例:**
```python
stats = db.get_statistics()
print(f"Total papers: {stats['total_papers']}")
print(f"High potential papers: {stats['high_potential_papers']}")
print(f"Average score: {stats['avg_investment_score']:.2f}")
```

## 🕷️ 爬虫API

### BaseCrawler

所有爬虫的基础类，提供通用功能。

#### 初始化

```python
from src.crawlers.base_crawler import BaseCrawler

config = {
    'request': {'timeout': 30, 'max_retries': 3},
    'chrome': {'headless': True}
}
crawler = BaseCrawler(config)
```

#### 核心方法

##### `setup_driver() -> webdriver.Chrome`

设置Chrome WebDriver。

**返回:**
- `webdriver.Chrome`: Chrome驱动实例

##### `make_request(url: str, method: str = 'GET') -> requests.Response`

发送HTTP请求，带重试和限流。

**参数:**
- `url` (str): 请求URL
- `method` (str): 请求方法，默认'GET'

**返回:**
- `requests.Response`: 响应对象

##### `extract_keywords(title: str, abstract: str = "") -> List[str]`

从标题和摘要中提取关键词。

**参数:**
- `title` (str): 论文标题
- `abstract` (str): 论文摘要

**返回:**
- `List[str]`: 关键词列表

### OpenReviewCrawler

OpenReview网站爬虫，用于ICLR、ICML、NeurIPS等会议。

#### 初始化

```python
from src.crawlers.openreview_crawler import OpenReviewCrawler

crawler = OpenReviewCrawler(config)
```

#### 方法

##### `crawl_papers(conference, year, keywords=None, ...) -> List[Dict]`

爬取指定会议和年份的论文。

**参数:**
- `conference` (str): 会议名称 ('ICLR', 'ICML', 'NeurIPS')
- `year` (int): 年份
- `keywords` (Optional[List[str]]): 关键词过滤
- `date_from` (Optional[datetime]): 开始日期
- `date_to` (Optional[datetime]): 结束日期
- `include_ratings` (bool): 是否包含评分

**返回:**
- `List[Dict]`: 论文数据列表

**示例:**
```python
# 爬取ICLR 2024的transformer相关论文
papers = crawler.crawl_papers(
    conference='ICLR',
    year=2024,
    keywords=['transformer', 'attention']
)

print(f"Found {len(papers)} papers")
for paper in papers[:3]:
    print(f"- {paper['title']}")
```

### CVFCrawler

CVF网站爬虫，用于CVPR、ICCV、WACV等计算机视觉会议。

#### 初始化

```python
from src.crawlers.cvf_crawler import CVFCrawler

crawler = CVFCrawler(config)
```

#### 方法

##### `crawl_papers(conference, year, keywords=None, ...) -> List[Dict]`

爬取CVF会议论文。

**参数:**
- `conference` (str): 会议名称 ('CVPR', 'ICCV', 'WACV')
- `year` (int): 年份
- `keywords` (Optional[List[str]]): 关键词过滤
- `include_details` (bool): 是否包含详细信息

**示例:**
```python
# 爬取CVPR 2024的计算机视觉论文
papers = crawler.crawl_papers(
    conference='CVPR',
    year=2024,
    keywords=['object detection', 'segmentation'],
    include_details=True
)
```

## 📊 评分系统API

### InvestmentScorer

投资价值评分器，对论文进行多维度评分。

#### 初始化

```python
from src.scoring.investment_scorer import InvestmentScorer

config = {
    'scoring': {
        'weights': {
            'citation_count': 0.25,
            'citation_growth': 0.20,
            'author_h_index': 0.15,
            'venue_impact': 0.15,
            'novelty_score': 0.10,
            'technical_depth': 0.10,
            'commercial_potential': 0.05
        }
    }
}

scorer = InvestmentScorer(config)
```

#### 方法

##### `score_paper(paper_data: Dict) -> Dict`

对单篇论文进行完整评分。

**参数:**
- `paper_data` (Dict): 论文数据字典

**返回:**
- `Dict`: 评分结果字典

**示例:**
```python
paper = {
    'title': 'Attention Is All You Need',
    'abstract': 'The dominant sequence transduction models...',
    'authors': '["Ashish Vaswani", "Noam Shazeer"]',
    'conference': 'NeurIPS',
    'year': 2017
}

result = scorer.score_paper(paper)
print(f"Investment Score: {result['investment_score']}")
print(f"Recommendation: {result['investment_recommendation']}")
print(f"Technical Depth: {result['technical_depth_score']}")
```

##### `batch_score_papers(papers_data: List[Dict]) -> List[Dict]`

批量评分论文。

**参数:**
- `papers_data` (List[Dict]): 论文数据列表

**返回:**
- `List[Dict]`: 评分后的论文数据列表

**示例:**
```python
# 批量评分多篇论文
papers = [paper1, paper2, paper3]  # 论文数据列表
scored_papers = scorer.batch_score_papers(papers)

# 按评分排序
scored_papers.sort(key=lambda x: x['investment_score'], reverse=True)
```

##### `calculate_novelty_score(title: str, abstract: str, keywords: List[str]) -> float`

计算新颖性评分。

**参数:**
- `title` (str): 论文标题
- `abstract` (str): 论文摘要
- `keywords` (List[str]): 关键词列表

**返回:**
- `float`: 新颖性评分 (1-10)

##### `calculate_technical_depth_score(title: str, abstract: str) -> float`

计算技术深度评分。

**参数:**
- `title` (str): 论文标题
- `abstract` (str): 论文摘要

**返回:**
- `float`: 技术深度评分 (1-10)

##### `calculate_commercial_potential_score(title, abstract, keywords, authors) -> Dict`

计算商业化潜力评分。

**参数:**
- `title` (str): 论文标题
- `abstract` (str): 论文摘要
- `keywords` (List[str]): 关键词列表
- `authors` (List[str]): 作者列表

**返回:**
- `Dict`: 商业化潜力信息

**示例:**
```python
commercial_info = scorer.calculate_commercial_potential_score(
    title="GPT-4 Technical Report",
    abstract="We report the development of GPT-4...",
    keywords=["language model", "gpt", "ai"],
    authors=["OpenAI Team"]
)

print(f"Commercial Score: {commercial_info['score']}")
print(f"Market Size: {commercial_info['market_size']}")
print(f"Maturity: {commercial_info['maturity']}")
```

## 📈 导出系统API

### ExcelExporter

Excel报告导出器，生成专业的分析报告。

#### 初始化

```python
from src.export.excel_exporter import ExcelExporter

config = {
    'export': {
        'excel': {
            'filename_template': 'AI_Papers_Analysis_{date}.xlsx',
            'formatting': {
                'header_color': '366092',
                'highlight_color': 'FFE699'
            }
        }
    }
}

exporter = ExcelExporter(config)
```

#### 方法

##### `create_excel_report(papers_data: List[Dict], output_path=None) -> str`

创建完整的Excel报告。

**参数:**
- `papers_data` (List[Dict]): 论文数据列表
- `output_path` (Optional[str]): 输出路径

**返回:**
- `str`: 生成的文件路径

**示例:**
```python
# 生成Excel报告
papers = db.get_papers_dataframe()
report_path = exporter.create_excel_report(
    papers_data=papers.to_dict('records'),
    output_path='reports/analysis_2024.xlsx'
)

print(f"Report generated: {report_path}")
```

##### `prepare_overview_data(papers_data: List[Dict]) -> pd.DataFrame`

准备论文概览数据。

**参数:**
- `papers_data` (List[Dict]): 论文数据列表

**返回:**
- `pd.DataFrame`: 概览数据DataFrame

##### `prepare_investment_data(papers_data: List[Dict]) -> pd.DataFrame`

准备投资机会数据。

**参数:**
- `papers_data` (List[Dict]): 论文数据列表

**返回:**
- `pd.DataFrame`: 投资机会数据DataFrame

##### `prepare_trend_analysis_data(papers_data: List[Dict]) -> pd.DataFrame`

准备趋势分析数据。

**参数:**
- `papers_data` (List[Dict]): 论文数据列表

**返回:**
- `pd.DataFrame`: 趋势分析数据DataFrame

## 🔧 主系统API

### PaperMonitoringSystem

主系统类，整合所有功能模块。

#### 初始化

```python
from main import PaperMonitoringSystem

monitor = PaperMonitoringSystem(config_path="config/config.yaml")
```

#### 方法

##### `run_monitoring(conferences=None, years=None, ...) -> str`

运行完整的监控流程。

**参数:**
- `conferences` (Optional[List[str]]): 会议列表
- `years` (Optional[List[int]]): 年份列表
- `keywords` (Optional[List[str]]): 关键词列表
- `date_from` (Optional[datetime]): 开始日期
- `date_to` (Optional[datetime]): 结束日期
- `output_path` (Optional[str]): 输出路径

**返回:**
- `str`: 生成的报告路径

**示例:**
```python
# 运行完整监控流程
report_path = monitor.run_monitoring(
    conferences=['ICLR', 'CVPR'],
    years=[2023, 2024],
    keywords=['transformer', 'diffusion'],
    output_path='reports/analysis.xlsx'
)

print(f"Analysis complete: {report_path}")
```

##### `crawl_papers(conferences=None, years=None, ...) -> List[Dict]`

爬取论文数据。

##### `process_and_score_papers(papers_data: List[Dict]) -> List[Dict]`

处理和评分论文。

##### `generate_report(papers_data: List[Dict], output_path=None) -> str`

生成Excel报告。

## 📝 数据结构

### 论文数据结构

```python
paper_data = {
    # 基本信息
    'id': int,                          # 论文ID
    'title': str,                       # 论文标题
    'abstract': str,                    # 论文摘要
    'authors': str,                     # JSON格式的作者列表
    'authors_affiliations': str,        # JSON格式的作者机构
    'authors_countries': str,           # JSON格式的作者国籍
    'authors_emails': str,              # JSON格式的联系方式
    
    # 发表信息
    'conference': str,                  # 会议名称
    'year': int,                        # 年份
    'publication_date': datetime,       # 发表日期
    'paper_url': str,                   # 论文链接
    'pdf_url': str,                     # PDF链接
    
    # 引用和影响力指标
    'citation_count': int,              # 引用次数
    'citation_growth_rate': float,      # 引用增长率
    'h_index_max': float,               # 作者最高H指数
    'venue_impact_factor': float,       # 会议影响因子
    
    # 内容分析指标
    'keywords': str,                    # JSON格式的关键词
    'technical_depth_score': float,     # 技术深度评分
    'novelty_score': float,             # 新颖性评分
    'commercial_potential_score': float, # 商业潜力评分
    
    # 投资相关指标
    'investment_score': float,          # 综合投资价值评分
    'investment_recommendation': str,    # 投资建议
    'market_size_estimate': str,        # 市场规模估计
    'technology_maturity': str,         # 技术成熟度
    'startup_indicators': bool,         # 是否涉及创业公司
    'industry_partnerships': str,       # 产业合作信息
    
    # 系统信息
    'created_at': datetime,             # 创建时间
    'updated_at': datetime,             # 更新时间
    'data_source': str                  # 数据来源
}
```

### 评分结果结构

```python
scoring_result = {
    'investment_score': float,              # 综合投资评分
    'investment_recommendation': str,        # 投资建议
    'citation_count': int,                  # 引用次数
    'citation_growth_rate': float,          # 引用增长率
    'h_index_max': float,                   # 最高H指数
    'venue_impact_factor': float,           # 会议影响因子
    'technical_depth_score': float,         # 技术深度评分
    'novelty_score': float,                 # 新颖性评分
    'commercial_potential_score': float,    # 商业潜力评分
    'market_size_estimate': str,            # 市场规模估计
    'technology_maturity': str,             # 技术成熟度
    'startup_indicators': bool,             # 创业指标
    'industry_partnerships': str,           # 产业合作
    'scoring_details': dict                 # 详细评分信息
}
```

## 🚨 错误处理

### 常见异常类型

```python
# 数据库相关异常
from sqlalchemy.exc import SQLAlchemyError

try:
    db.add_paper(paper_data)
except SQLAlchemyError as e:
    print(f"Database error: {e}")

# 爬虫相关异常
from selenium.common.exceptions import WebDriverException
from requests.exceptions import RequestException

try:
    papers = crawler.crawl_papers('ICLR', 2024)
except WebDriverException as e:
    print(f"WebDriver error: {e}")
except RequestException as e:
    print(f"Request error: {e}")

# 评分相关异常
try:
    result = scorer.score_paper(paper_data)
except ValueError as e:
    print(f"Scoring error: {e}")
```

## 📚 使用示例

### 完整工作流程

```python
import yaml
from datetime import datetime
from main import PaperMonitoringSystem

# 1. 加载配置
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 2. 初始化系统
monitor = PaperMonitoringSystem()

# 3. 爬取数据
papers = monitor.crawl_papers(
    conferences=['ICLR', 'CVPR'],
    years=[2024],
    keywords=['transformer', 'diffusion']
)

# 4. 评分分析
scored_papers = monitor.process_and_score_papers(papers)

# 5. 生成报告
report_path = monitor.generate_report(
    scored_papers,
    output_path='analysis_2024.xlsx'
)

# 6. 清理资源
monitor.close()

print(f"Analysis complete: {report_path}")
```

### 自定义评分权重

```python
# 创建自定义评分配置
custom_config = {
    'scoring': {
        'weights': {
            'citation_count': 0.30,        # 增加引用权重
            'commercial_potential': 0.20,  # 增加商业权重
            'novelty_score': 0.15,         # 增加新颖性权重
            'citation_growth': 0.15,
            'author_h_index': 0.10,
            'venue_impact': 0.05,
            'technical_depth': 0.05
        }
    }
}

# 使用自定义配置
scorer = InvestmentScorer(custom_config)
result = scorer.score_paper(paper_data)
```

### 批量数据处理

```python
# 批量处理大量论文数据
def process_papers_in_batches(papers, batch_size=100):
    results = []
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        
        # 批量评分
        scored_batch = scorer.batch_score_papers(batch)
        
        # 存储到数据库
        for paper in scored_batch:
            paper_id = db.add_paper(paper)
            paper['id'] = paper_id
        
        results.extend(scored_batch)
        print(f"Processed batch {i//batch_size + 1}")
    
    return results

# 使用批量处理
all_papers = process_papers_in_batches(papers, batch_size=50)
```

---

**更多API详情请参考源代码注释和类型提示** 📝