"""
基础爬虫模块 - AI学术论文监控系统
Base Crawler Module - AI Academic Paper Monitoring System

该模块提供所有爬虫的基础类和通用功能
This module provides base class and common functionality for all crawlers
"""

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import json
from ratelimit import limits, sleep_and_retry

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    基础爬虫类
    Base crawler class for all conference crawlers
    """
    
    def __init__(self, config: Dict):
        """
        初始化基础爬虫
        Initialize base crawler
        
        Args:
            config: 配置字典 Configuration dictionary
        """
        self.config = config
        self.session = requests.Session()
        self.driver = None
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': config.get('request', {}).get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })
        
        # 设置代理
        if config.get('proxy', {}).get('enabled', False):
            proxies = {
                'http': config['proxy']['http'],
                'https': config['proxy']['https']
            }
            self.session.proxies.update(proxies)
        
        # 请求参数
        self.timeout = config.get('request', {}).get('timeout', 30)
        self.max_retries = config.get('request', {}).get('max_retries', 5)
        self.retry_delay = config.get('request', {}).get('retry_delay', 10)
        
        logger.info(f"初始化 {self.__class__.__name__} 爬虫")
    
    def setup_driver(self) -> webdriver.Chrome:
        """
        设置Chrome WebDriver
        Setup Chrome WebDriver
        
        Returns:
            webdriver.Chrome: Chrome驱动实例
        """
        try:
            options = Options()
            
            # Chrome选项配置
            chrome_config = self.config.get('chrome', {})
            if chrome_config.get('headless', True):
                options.add_argument('--headless')
            if chrome_config.get('disable_gpu', True):
                options.add_argument('--disable-gpu')
            if chrome_config.get('no_sandbox', True):
                options.add_argument('--no-sandbox')
            
            window_size = chrome_config.get('window_size', '1920,1080')
            options.add_argument(f'--window-size={window_size}')
            
            # 其他常用选项
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 自动下载ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver 初始化成功")
            return self.driver
            
        except Exception as e:
            logger.error(f"Chrome WebDriver 初始化失败: {e}")
            raise
    
    @sleep_and_retry
    @limits(calls=10, period=60)  # 限制每分钟10次请求
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        发送HTTP请求 (带重试和限流)
        Make HTTP request with retry and rate limiting
        
        Args:
            url: 请求URL Request URL
            method: 请求方法 Request method
            **kwargs: 其他请求参数 Additional request parameters
            
        Returns:
            requests.Response: 响应对象 Response object
        """
        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, timeout=self.timeout, **kwargs)
                else:
                    raise ValueError(f"不支持的请求方法: {method}")
                
                response.raise_for_status()
                logger.debug(f"请求成功: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {url} - {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"请求最终失败: {url}")
                    raise
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        解析HTML内容
        Parse HTML content
        
        Args:
            html_content: HTML内容 HTML content
            
        Returns:
            BeautifulSoup: 解析后的HTML对象 Parsed HTML object
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        Clean text content
        
        Args:
            text: 原始文本 Raw text
            
        Returns:
            str: 清理后的文本 Cleaned text
        """
        if not text:
            return ""
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符 (保留基本标点)
        text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}]', '', text)
        
        return text
    
    def extract_keywords(self, title: str, abstract: str = "") -> List[str]:
        """
        提取关键词
        Extract keywords from title and abstract
        
        Args:
            title: 论文标题 Paper title
            abstract: 论文摘要 Paper abstract
            
        Returns:
            List[str]: 关键词列表 Keywords list
        """
        text = f"{title} {abstract}".lower()
        
        # 常见的AI/ML关键词
        ai_keywords = [
            'neural network', 'deep learning', 'machine learning', 'artificial intelligence',
            'transformer', 'attention', 'convolution', 'cnn', 'rnn', 'lstm', 'gru',
            'generative', 'gan', 'vae', 'diffusion', 'autoencoder',
            'reinforcement learning', 'supervised', 'unsupervised', 'self-supervised',
            'computer vision', 'natural language processing', 'nlp', 'multimodal',
            'classification', 'detection', 'segmentation', 'generation', 'prediction',
            'optimization', 'training', 'inference', 'fine-tuning', 'transfer learning',
            'federated learning', 'meta learning', 'few-shot', 'zero-shot',
            'robustness', 'fairness', 'interpretability', 'explainable',
            'large language model', 'llm', 'foundation model', 'pretrained'
        ]
        
        found_keywords = []
        for keyword in ai_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def match_investment_keywords(self, title: str, abstract: str = "") -> Dict[str, bool]:
        """
        匹配投资相关关键词
        Match investment-related keywords
        
        Args:
            title: 论文标题 Paper title
            abstract: 论文摘要 Paper abstract
            
        Returns:
            Dict[str, bool]: 关键词匹配结果 Keyword matching results
        """
        text = f"{title} {abstract}".lower()
        
        # 从配置中获取投资关键词
        hot_topics = self.config.get('investment_keywords', {}).get('hot_topics', [])
        commercial_indicators = self.config.get('investment_keywords', {}).get('commercial_indicators', [])
        
        results = {
            'hot_topic_match': False,
            'commercial_potential': False,
            'matched_topics': [],
            'matched_commercial': []
        }
        
        # 检查热门话题
        for topic in hot_topics:
            if topic.lower() in text:
                results['hot_topic_match'] = True
                results['matched_topics'].append(topic)
        
        # 检查商业化指标
        for indicator in commercial_indicators:
            if indicator.lower() in text:
                results['commercial_potential'] = True
                results['matched_commercial'].append(indicator)
        
        return results
    
    def extract_author_info(self, author_text: str) -> Dict[str, List[str]]:
        """
        提取作者信息
        Extract author information
        
        Args:
            author_text: 作者文本 Author text
            
        Returns:
            Dict[str, List[str]]: 作者信息字典 Author information dictionary
        """
        # 这是一个基础实现，子类可以根据具体网站格式重写
        authors = []
        affiliations = []
        emails = []
        
        # 简单的作者名提取 (需要根据具体网站格式调整)
        if author_text:
            # 分割作者名 (通常用逗号或分号分隔)
            author_names = re.split(r'[,;]', author_text)
            authors = [name.strip() for name in author_names if name.strip()]
        
        return {
            'names': authors,
            'affiliations': affiliations,
            'emails': emails
        }
    
    @abstractmethod
    def crawl_papers(self, 
                    conference: str,
                    year: int,
                    keywords: Optional[List[str]] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None) -> List[Dict]:
        """
        爬取论文 (抽象方法，子类必须实现)
        Crawl papers (abstract method, must be implemented by subclasses)
        
        Args:
            conference: 会议名称 Conference name
            year: 年份 Year
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date
            date_to: 结束日期 End date
            
        Returns:
            List[Dict]: 论文数据列表 Paper data list
        """
        pass
    
    def close(self):
        """
        关闭资源
        Close resources
        """
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver 已关闭")
        
        if self.session:
            self.session.close()
            logger.info("Session 已关闭")


class PaperData:
    """
    论文数据标准化类
    Paper data standardization class
    """
    
    @staticmethod
    def create_paper_dict(
        title: str,
        authors: List[str],
        conference: str,
        year: int,
        abstract: str = "",
        paper_url: str = "",
        pdf_url: str = "",
        publication_date: Optional[datetime] = None,
        affiliations: List[str] = None,
        emails: List[str] = None,
        **kwargs
    ) -> Dict:
        """
        创建标准化的论文数据字典
        Create standardized paper data dictionary
        
        Args:
            title: 论文标题 Paper title
            authors: 作者列表 Authors list
            conference: 会议名称 Conference name
            year: 年份 Year
            abstract: 摘要 Abstract
            paper_url: 论文链接 Paper URL
            pdf_url: PDF链接 PDF URL
            publication_date: 发表日期 Publication date
            affiliations: 机构列表 Affiliations list
            emails: 邮箱列表 Emails list
            **kwargs: 其他参数 Additional parameters
            
        Returns:
            Dict: 标准化的论文数据字典 Standardized paper data dictionary
        """
        return {
            'title': title,
            'abstract': abstract,
            'authors': json.dumps(authors, ensure_ascii=False),
            'authors_affiliations': json.dumps(affiliations or [], ensure_ascii=False),
            'authors_countries': json.dumps([], ensure_ascii=False),  # 需要后续补充
            'authors_emails': json.dumps(emails or [], ensure_ascii=False),
            'conference': conference,
            'year': year,
            'publication_date': publication_date,
            'paper_url': paper_url,
            'pdf_url': pdf_url,
            'citation_count': kwargs.get('citation_count', 0),
            'keywords': json.dumps(kwargs.get('keywords', []), ensure_ascii=False),
            'data_source': kwargs.get('data_source', 'crawler'),
            **{k: v for k, v in kwargs.items() if k not in [
                'citation_count', 'keywords', 'data_source'
            ]}
        }


# 使用示例
if __name__ == "__main__":
    # 示例配置
    config = {
        'request': {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        'proxy': {
            'enabled': False
        },
        'chrome': {
            'headless': True,
            'disable_gpu': True,
            'no_sandbox': True
        },
        'investment_keywords': {
            'hot_topics': ['transformer', 'diffusion', 'large language model'],
            'commercial_indicators': ['industry', 'production', 'deployment']
        }
    }
    
    # 这里只是示例，实际使用时需要创建具体的子类
    # crawler = ConcreteCrawler(config)
    # papers = crawler.crawl_papers('ICLR', 2024)
    print("基础爬虫模块初始化完成")