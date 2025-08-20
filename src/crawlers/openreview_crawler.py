"""
OpenReview爬虫模块 - AI学术论文监控系统
OpenReview Crawler Module - AI Academic Paper Monitoring System

该模块负责爬取OpenReview网站的论文数据 (ICLR, ICML, NeurIPS等)
This module crawls paper data from OpenReview website (ICLR, ICML, NeurIPS, etc.)
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import json

from .base_crawler import BaseCrawler, PaperData

logger = logging.getLogger(__name__)


class OpenReviewCrawler(BaseCrawler):
    """
    OpenReview网站爬虫
    OpenReview website crawler for ICLR, ICML, NeurIPS conferences
    """
    
    def __init__(self, config: Dict):
        """
        初始化OpenReview爬虫
        Initialize OpenReview crawler
        """
        super().__init__(config)
        self.base_url = "https://openreview.net"
        
        # URL模板
        self.url_templates = {
            'ICLR': 'https://openreview.net/group?id=ICLR.cc/{year}/Conference',
            'ICML': 'https://openreview.net/group?id=ICML.cc/{year}/Conference', 
            'NeurIPS': 'https://openreview.net/group?id=NeurIPS.cc/{year}/Conference'
        }
        
        # 支持的会议和年份
        self.supported_conferences = ['ICLR', 'ICML', 'NeurIPS']
        self.supported_years = list(range(2020, 2026))  # 2020-2025
        
        logger.info("OpenReview爬虫初始化完成")
    
    def get_conference_url(self, conference: str, year: int) -> str:
        """
        获取会议URL
        Get conference URL
        
        Args:
            conference: 会议名称 Conference name
            year: 年份 Year
            
        Returns:
            str: 会议URL Conference URL
        """
        if conference not in self.supported_conferences:
            raise ValueError(f"不支持的会议: {conference}")
        
        # 对于2025年的ICLR，使用特殊的URL格式
        if conference == 'ICLR' and year == 2025:
            # 2025年可能使用不同的URL格式或还在review阶段
            return 'https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-active-submissions'
        
        if year not in self.supported_years:
            logger.warning(f"年份 {year} 可能不受支持，但仍尝试访问")
        
        return self.url_templates[conference].format(year=year)
    
    def extract_paper_rating(self, paper_url: str) -> float:
        """
        提取论文评分
        Extract paper rating from paper page
        
        Args:
            paper_url: 论文页面URL Paper page URL
            
        Returns:
            float: 论文平均评分 Paper average rating
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            # 访问论文页面
            full_url = f"{self.base_url}{paper_url}" if not paper_url.startswith('http') else paper_url
            self.driver.get(full_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "forum-replies"))
            )
            
            ratings = []
            
            # 查找评分元素 (OpenReview的评分通常在review中)
            for i in range(1, 7):  # 最多查找6个评分
                try:
                    # 尝试不同的XPath路径
                    rating_xpaths = [
                        f'//*[@id="forum-replies"]/div[{i}]/div[4]/div/div[9]/span',
                        f'//*[@id="forum-replies"]/div[{i}]/div[4]/div/div[10]/span',
                        f'//*[@id="forum-replies"]/div[{i}]//span[contains(@class, "rating")]',
                        f'//*[@id="forum-replies"]/div[{i}]//strong[contains(text(), "Rating:")]/following-sibling::text()',
                    ]
                    
                    rating_element = None
                    for xpath in rating_xpaths:
                        try:
                            rating_element = self.driver.find_element(By.XPATH, xpath)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if rating_element:
                        rating_text = rating_element.text.strip()
                        # 提取数字评分 (通常是 "6: Accept" 或 "6" 的格式)
                        rating_match = re.search(r'(\d+)', rating_text)
                        if rating_match:
                            rating = int(rating_match.group(1))
                            if 1 <= rating <= 10:  # 有效评分范围
                                ratings.append(rating)
                
                except NoSuchElementException:
                    continue
            
            # 计算平均评分
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                logger.debug(f"论文评分: {ratings} -> 平均: {avg_rating:.2f}")
                return avg_rating
            else:
                logger.debug("未找到评分信息")
                return 0.0
                
        except Exception as e:
            logger.warning(f"提取论文评分失败: {e}")
            return 0.0
    
    def extract_paper_details(self, paper_element) -> Dict:
        """
        提取论文详细信息
        Extract detailed paper information
        
        Args:
            paper_element: 论文元素 Paper element
            
        Returns:
            Dict: 论文详细信息 Paper details
        """
        try:
            # 提取标题
            title_element = paper_element.find_element(By.TAG_NAME, "h4")
            title = self.clean_text(title_element.text)
            
            # 提取论文链接
            paper_link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            # 提取PDF链接
            pdf_link = ""
            try:
                pdf_element = paper_element.find_element(By.CSS_SELECTOR, "a.pdf-link")
                pdf_link = pdf_element.get_attribute("href")
                if not pdf_link.startswith('http'):
                    pdf_link = f"{self.base_url}{pdf_link}"
            except NoSuchElementException:
                logger.debug(f"未找到PDF链接: {title}")
            
            # 提取作者信息
            authors = []
            try:
                author_elements = paper_element.find_elements(By.CSS_SELECTOR, ".note-authors a")
                authors = [self.clean_text(author.text) for author in author_elements]
            except NoSuchElementException:
                logger.debug(f"未找到作者信息: {title}")
            
            # 提取摘要 (如果在列表页面有的话)
            abstract = ""
            try:
                abstract_element = paper_element.find_element(By.CSS_SELECTOR, ".note-content")
                abstract = self.clean_text(abstract_element.text)
            except NoSuchElementException:
                pass
            
            return {
                'title': title,
                'paper_url': paper_link,
                'pdf_url': pdf_link,
                'authors': authors,
                'abstract': abstract
            }
            
        except Exception as e:
            logger.error(f"提取论文详细信息失败: {e}")
            return {}
    
    def get_paper_categories(self, conference: str, year: int) -> List[str]:
        """
        获取论文分类标签
        Get paper category tabs
        
        Args:
            conference: 会议名称 Conference name
            year: 年份 Year
            
        Returns:
            List[str]: 分类标签列表 Category tabs list
        """
        try:
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 查找分类标签 - 尝试多种选择器
            tab_selectors = [
                ".nav-tabs li[role='presentation'] a",
                ".nav-tabs li a",
                ".nav.nav-tabs li a",
                "#notes .nav-tabs li a"
            ]
            
            tab_elements = []
            for selector in tab_selectors:
                try:
                    tab_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if tab_elements:
                        logger.debug(f"使用选择器找到标签: {selector}")
                        break
                except:
                    continue
            
            categories = []
            
            # 如果找到了标签
            if tab_elements:
                for tab in tab_elements:
                    try:
                        category_id = tab.get_attribute("aria-controls")
                        category_text = tab.text.strip().lower()
                        
                        # 对于2025年，可能包含不同的分类
                        if year == 2025:
                            # 2025年可能是提交阶段，查找active submissions
                            if any(keyword in category_text for keyword in [
                                "active", "submission", "under review", "decision", "accept", "poster", "oral"
                            ]):
                                if category_id:
                                    categories.append(category_id)
                        else:
                            # 常规年份的分类
                            if any(keyword in category_text for keyword in [
                                "accept", "poster", "oral", "spotlight", "notable", "decision"
                            ]):
                                if category_id:
                                    categories.append(category_id)
                    except Exception as e:
                        logger.debug(f"处理标签失败: {e}")
                        continue
            
            # 如果没有找到标签，使用默认分类
            if not categories:
                if year == 2025:
                    categories = ["active-submissions"]  # 2025年可能还在review阶段
                else:
                    categories = ["accepted-papers", "poster-presentations", "oral-presentations"]
            
            logger.info(f"找到 {len(categories)} 个论文分类: {categories}")
            return categories
            
        except Exception as e:
            logger.error(f"获取论文分类失败: {e}")
            # 返回默认分类
            if year == 2025:
                return ["active-submissions"]
            return ["accepted-papers"]
    
    def crawl_papers_by_category(self, 
                                category_id: str, 
                                conference: str, 
                                year: int,
                                keywords: Optional[List[str]] = None,
                                max_pages: int = 100) -> List[Dict]:
        """
        按分类爬取论文
        Crawl papers by category
        
        Args:
            category_id: 分类ID Category ID
            conference: 会议名称 Conference name
            year: 年份 Year
            keywords: 关键词过滤 Keywords filter
            max_pages: 最大页数 Maximum pages
            
        Returns:
            List[Dict]: 论文数据列表 Paper data list
        """
        papers = []
        
        try:
            # 尝试点击分类标签
            try:
                category_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[aria-controls='{category_id}']"))
                )
                self.driver.execute_script("arguments[0].click();", category_tab)
                time.sleep(2)
                logger.info(f"成功点击分类标签: {category_id}")
            except TimeoutException:
                # 如果找不到标签，可能页面已经显示了内容
                logger.warning(f"未找到分类标签 {category_id}，尝试直接查找内容")
                pass
            
            # 分页爬取
            current_page = 1
            
            while current_page <= max_pages:
                logger.info(f"正在爬取 {conference}{year} - {category_id} 第 {current_page} 页")
                
                # 等待页面内容加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, category_id))
                )
                
                # 获取当前页面的论文
                try:
                    # 尝试不同的论文元素选择器
                    paper_selectors = [
                        f"#{category_id} .list-unstyled.list-paginated h4",
                        f"#{category_id} li.note",
                        f"#{category_id} .note-content",
                        ".note-content h4",  # 通用选择器
                        "li.note",  # 更通用的选择器
                        ".list-unstyled li",  # 列表项
                        "h4 a[href*='/forum?id=']"  # 论文标题链接
                    ]
                    
                    paper_elements = []
                    used_selector = None
                    
                    for selector in paper_selectors:
                        try:
                            paper_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if paper_elements:
                                used_selector = selector
                                logger.debug(f"使用选择器找到论文: {selector}, 数量: {len(paper_elements)}")
                                break
                        except NoSuchElementException:
                            continue
                    
                    if not paper_elements:
                        logger.warning(f"未找到论文元素: {category_id} 第 {current_page} 页")
                        
                        # 尝试查看页面源码以调试
                        page_source = self.driver.page_source
                        if "under review" in page_source.lower() or "submissions" in page_source.lower():
                            logger.info("检测到页面包含'under review'或'submissions'，可能论文还在审核中")
                        
                        # 尝试查找任何包含论文信息的元素
                        debug_elements = self.driver.find_elements(By.CSS_SELECTOR, "h4, .title, [class*='title'], [class*='paper']")
                        logger.debug(f"调试: 找到 {len(debug_elements)} 个可能的标题元素")
                        
                        if debug_elements:
                            for i, elem in enumerate(debug_elements[:5]):  # 只显示前5个
                                try:
                                    text = elem.text.strip()
                                    if text and len(text) > 10:  # 过滤掉太短的文本
                                        logger.debug(f"调试元素 {i}: {text[:100]}...")
                                except:
                                    pass
                        
                        break
                    
                    # 提取每篇论文的信息
                    for paper_element in paper_elements:
                        try:
                            paper_info = self.extract_paper_details(paper_element)
                            if not paper_info or not paper_info.get('title'):
                                continue
                            
                            # 关键词过滤
                            if keywords:
                                title_lower = paper_info['title'].lower()
                                abstract_lower = paper_info.get('abstract', '').lower()
                                
                                keyword_match = False
                                for keyword in keywords:
                                    if (keyword.lower() in title_lower or 
                                        keyword.lower() in abstract_lower):
                                        keyword_match = True
                                        break
                                
                                if not keyword_match:
                                    continue
                            
                            # 提取论文评分 (可选，比较耗时)
                            rating = 0.0
                            if paper_info.get('paper_url'):
                                # rating = self.extract_paper_rating(paper_info['paper_url'])
                                pass  # 暂时跳过评分提取以提高速度
                            
                            # 创建标准化的论文数据
                            paper_data = PaperData.create_paper_dict(
                                title=paper_info['title'],
                                authors=paper_info.get('authors', []),
                                conference=conference,
                                year=year,
                                abstract=paper_info.get('abstract', ''),
                                paper_url=paper_info.get('paper_url', ''),
                                pdf_url=paper_info.get('pdf_url', ''),
                                publication_date=datetime(year, 6, 1),  # 估计发表日期
                                rating=rating,
                                category=category_id,
                                data_source=f"openreview_{conference.lower()}"
                            )
                            
                            papers.append(paper_data)
                            logger.debug(f"成功提取论文: {paper_info['title']}")
                            
                        except Exception as e:
                            logger.warning(f"提取单篇论文失败: {e}")
                            continue
                    
                    logger.info(f"第 {current_page} 页完成，提取 {len(paper_elements)} 篇论文")
                    
                except Exception as e:
                    logger.error(f"处理页面内容失败: {e}")
                    break
                
                # 尝试翻页
                try:
                    next_page = current_page + 1
                    next_page_selectors = [
                        f"#{category_id} .pagination a[text()='{next_page}']",
                        f"#{category_id} nav ul li a[text()='{next_page}']"
                    ]
                    
                    next_button = None
                    for selector in next_page_selectors:
                        try:
                            next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if next_button:
                        self.driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)  # 等待页面加载
                        current_page = next_page
                    else:
                        logger.info(f"已到达最后一页: {current_page - 1}")
                        break
                        
                except Exception as e:
                    logger.info(f"翻页结束: {e}")
                    break
            
            logger.info(f"分类 {category_id} 爬取完成，共获得 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"爬取分类 {category_id} 失败: {e}")
            return papers
    
    def crawl_papers(self, 
                    conference: str,
                    year: int,
                    keywords: Optional[List[str]] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None,
                    include_ratings: bool = False) -> List[Dict]:
        """
        爬取论文主方法
        Main method to crawl papers
        
        Args:
            conference: 会议名称 Conference name
            year: 年份 Year
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date (暂未使用)
            date_to: 结束日期 End date (暂未使用)
            include_ratings: 是否包含评分 Whether to include ratings
            
        Returns:
            List[Dict]: 论文数据列表 Paper data list
        """
        logger.info(f"开始爬取 {conference} {year} 论文")
        
        try:
            # 设置WebDriver
            if not self.driver:
                self.setup_driver()
            
            # 获取会议URL
            url = self.get_conference_url(conference, year)
            logger.info(f"访问会议页面: {url}")
            
            # 访问会议页面
            self.driver.get(url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".nav-tabs"))
            )
            
            # 获取论文分类
            categories = self.get_paper_categories(conference, year)
            if not categories:
                logger.warning("未找到论文分类，尝试直接爬取")
                categories = ["accepted-papers"]  # 默认分类
            
            # 爬取每个分类的论文
            all_papers = []
            for category in categories:
                try:
                    category_papers = self.crawl_papers_by_category(
                        category, conference, year, keywords
                    )
                    all_papers.extend(category_papers)
                    
                    # 短暂休息避免过于频繁的请求
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"爬取分类 {category} 失败: {e}")
                    continue
            
            logger.info(f"爬取完成: {conference} {year}，共获得 {len(all_papers)} 篇论文")
            return all_papers
            
        except Exception as e:
            logger.error(f"爬取 {conference} {year} 失败: {e}")
            return []


# 使用示例
if __name__ == "__main__":
    # 示例配置
    config = {
        'request': {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 5
        },
        'chrome': {
            'headless': False,  # 调试时设为False
            'disable_gpu': True,
            'no_sandbox': True
        },
        'investment_keywords': {
            'hot_topics': ['transformer', 'diffusion', 'large language model'],
            'commercial_indicators': ['industry', 'production', 'deployment']
        }
    }
    
    # 创建爬虫实例
    crawler = OpenReviewCrawler(config)
    
    try:
        # 爬取ICLR 2024的论文
        papers = crawler.crawl_papers(
            conference='ICLR',
            year=2024,
            keywords=['transformer', 'diffusion']  # 可选的关键词过滤
        )
        
        print(f"成功爬取 {len(papers)} 篇论文")
        
        # 显示前几篇论文
        for i, paper in enumerate(papers[:3]):
            print(f"\n论文 {i+1}:")
            print(f"标题: {paper['title']}")
            print(f"作者: {paper['authors']}")
            print(f"会议: {paper['conference']} {paper['year']}")
            print(f"链接: {paper['paper_url']}")
        
    finally:
        # 关闭爬虫
        crawler.close()