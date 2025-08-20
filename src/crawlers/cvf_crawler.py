"""
CVF爬虫模块 - AI学术论文监控系统
CVF Crawler Module - AI Academic Paper Monitoring System

该模块负责爬取CVF网站的论文数据 (CVPR, ICCV, WACV等)
This module crawls paper data from CVF website (CVPR, ICCV, WACV, etc.)
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import urljoin

from .base_crawler import BaseCrawler, PaperData

logger = logging.getLogger(__name__)


class CVFCrawler(BaseCrawler):
    """
    CVF网站爬虫 (Computer Vision Foundation)
    CVF website crawler for CVPR, ICCV, WACV conferences
    """
    
    def __init__(self, config: Dict):
        """
        初始化CVF爬虫
        Initialize CVF crawler
        """
        super().__init__(config)
        self.base_url = "https://openaccess.thecvf.com"
        
        # URL模板
        self.url_templates = {
            'CVPR': 'https://openaccess.thecvf.com/CVPR{year}?day=all',
            'ICCV': 'https://openaccess.thecvf.com/ICCV{year}?day=all',
            'WACV': 'https://openaccess.thecvf.com/WACV{year}',
        }
        
        # 支持的会议和年份
        self.supported_conferences = ['CVPR', 'ICCV', 'WACV']
        self.supported_years = {
            'CVPR': list(range(2013, 2025)),
            'ICCV': [2013, 2015, 2017, 2019, 2021, 2023],  # ICCV是奇数年
            'WACV': list(range(2020, 2025))
        }
        
        logger.info("CVF爬虫初始化完成")
    
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
        
        if year not in self.supported_years.get(conference, []):
            raise ValueError(f"{conference} 不支持的年份: {year}")
        
        return self.url_templates[conference].format(year=year)
    
    def extract_paper_info_from_dt(self, dt_element, conference: str, year: int) -> Dict:
        """
        从dt元素中提取论文信息
        Extract paper information from dt element
        
        Args:
            dt_element: dt HTML元素 dt HTML element
            conference: 会议名称 Conference name
            year: 年份 Year
            
        Returns:
            Dict: 论文信息字典 Paper information dictionary
        """
        try:
            # 提取论文链接和标题
            link_element = dt_element.find('a')
            if not link_element:
                return {}
            
            paper_url = link_element.get('href')
            if not paper_url.startswith('http'):
                paper_url = urljoin(self.base_url, paper_url)
            
            # 从链接中提取论文名称
            paper_path = link_element.get('href', '')
            path_parts = paper_path.split('/')
            if len(path_parts) > 0:
                filename = path_parts[-1].split('.')[0]
                # CVF的文件名格式通常是: AuthorName_PaperTitle_CONFERENCE_YEAR_paper.pdf
                name_parts = filename.split('_')
                if len(name_parts) > 2:
                    # 移除作者名和后缀，保留论文标题部分
                    title_parts = name_parts[1:-2]  # 去掉第一个(作者)和最后两个(会议年份)
                    title = ' '.join(title_parts)
                else:
                    title = filename.replace('_', ' ')
            else:
                title = link_element.text.strip()
            
            # 生成PDF链接
            pdf_url = ""
            if paper_path:
                # CVF的PDF链接格式
                pdf_filename = path_parts[-1].split('.')[0]
                pdf_url = f"https://openaccess.thecvf.com/content/{conference}{year}/papers/{pdf_filename}.pdf"
            
            return {
                'title': self.clean_text(title),
                'paper_url': paper_url,
                'pdf_url': pdf_url,
                'authors': [],  # CVF网站的列表页通常不显示作者
                'abstract': ''  # 列表页通常不显示摘要
            }
            
        except Exception as e:
            logger.warning(f"提取论文信息失败: {e}")
            return {}
    
    def get_paper_details_from_page(self, paper_url: str) -> Dict:
        """
        从论文详情页获取详细信息
        Get detailed information from paper page
        
        Args:
            paper_url: 论文页面URL Paper page URL
            
        Returns:
            Dict: 详细信息字典 Detailed information dictionary
        """
        try:
            response = self.make_request(paper_url)
            soup = self.parse_html(response.text)
            
            # 提取摘要
            abstract = ""
            abstract_element = soup.find('div', {'id': 'abstract'})
            if abstract_element:
                abstract = self.clean_text(abstract_element.get_text())
            
            # 提取作者信息
            authors = []
            author_elements = soup.find_all('i')  # CVF网站作者通常在<i>标签中
            for author_elem in author_elements:
                author_text = author_elem.get_text().strip()
                if author_text and not any(skip in author_text.lower() for skip in ['abstract', 'pdf', 'bibtex']):
                    # 分割多个作者 (通常用逗号分隔)
                    author_names = [name.strip() for name in author_text.split(',')]
                    authors.extend(author_names)
                    break  # 通常第一个<i>标签就是作者信息
            
            return {
                'abstract': abstract,
                'authors': authors
            }
            
        except Exception as e:
            logger.warning(f"获取论文详情失败: {paper_url} - {e}")
            return {}
    
    def crawl_papers(self, 
                    conference: str,
                    year: int,
                    keywords: Optional[List[str]] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None,
                    include_details: bool = False) -> List[Dict]:
        """
        爬取论文主方法
        Main method to crawl papers
        
        Args:
            conference: 会议名称 Conference name
            year: 年份 Year
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date (暂未使用)
            date_to: 结束日期 End date (暂未使用)
            include_details: 是否包含详细信息 Whether to include detailed information
            
        Returns:
            List[Dict]: 论文数据列表 Paper data list
        """
        logger.info(f"开始爬取 {conference} {year} 论文")
        
        try:
            # 获取会议URL
            url = self.get_conference_url(conference, year)
            logger.info(f"访问会议页面: {url}")
            
            # 获取页面内容
            response = self.make_request(url)
            soup = self.parse_html(response.text)
            
            # 查找论文列表容器
            paper_container = soup.find('dl')  # CVF网站的论文通常在<dl>标签中
            if not paper_container:
                logger.warning("未找到论文容器")
                return []
            
            # 获取所有论文条目 (dt标签)
            paper_elements = paper_container.find_all('dt')
            logger.info(f"找到 {len(paper_elements)} 篇论文")
            
            papers = []
            
            for i, dt_element in enumerate(paper_elements):
                try:
                    # 提取基本论文信息
                    paper_info = self.extract_paper_info_from_dt(dt_element, conference, year)
                    if not paper_info or not paper_info.get('title'):
                        continue
                    
                    # 关键词过滤
                    if keywords:
                        title_lower = paper_info['title'].lower()
                        
                        keyword_match = False
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                keyword_match = True
                                break
                        
                        if not keyword_match:
                            continue
                    
                    # 获取详细信息 (可选，会增加请求时间)
                    if include_details and paper_info.get('paper_url'):
                        try:
                            details = self.get_paper_details_from_page(paper_info['paper_url'])
                            paper_info.update(details)
                            time.sleep(1)  # 避免请求过于频繁
                        except Exception as e:
                            logger.warning(f"获取论文详情失败: {e}")
                    
                    # 提取关键词和投资相关信息
                    extracted_keywords = self.extract_keywords(
                        paper_info['title'], 
                        paper_info.get('abstract', '')
                    )
                    
                    investment_match = self.match_investment_keywords(
                        paper_info['title'],
                        paper_info.get('abstract', '')
                    )
                    
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
                        keywords=extracted_keywords,
                        hot_topic_match=investment_match['hot_topic_match'],
                        commercial_potential=investment_match['commercial_potential'],
                        matched_topics=investment_match['matched_topics'],
                        data_source=f"cvf_{conference.lower()}"
                    )
                    
                    papers.append(paper_data)
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"已处理 {i + 1}/{len(paper_elements)} 篇论文")
                    
                except Exception as e:
                    logger.warning(f"处理论文 {i+1} 失败: {e}")
                    continue
            
            logger.info(f"爬取完成: {conference} {year}，共获得 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"爬取 {conference} {year} 失败: {e}")
            return []


class ECCVCrawler(BaseCrawler):
    """
    ECCV网站爬虫 (European Conference on Computer Vision)
    ECCV website crawler
    """
    
    def __init__(self, config: Dict):
        """
        初始化ECCV爬虫
        Initialize ECCV crawler
        """
        super().__init__(config)
        self.base_url = "https://www.ecva.net"
        self.papers_url = "https://www.ecva.net/papers.php"
        
        # 支持的年份 (ECCV是偶数年)
        self.supported_years = [2018, 2020, 2022, 2024]
        
        logger.info("ECCV爬虫初始化完成")
    
    def get_year_papers_mapping(self) -> Dict[str, str]:
        """
        获取年份和论文的映射关系
        Get year-papers mapping from ECCV website
        
        Returns:
            Dict[str, str]: 年份到论文内容的映射 Year to papers content mapping
        """
        try:
            response = self.make_request(self.papers_url)
            soup = self.parse_html(response.text)
            
            # ECCV网站使用注释来分隔不同年份的论文
            from lxml import html
            root = html.fromstring(str(soup))
            
            paper_year_mapping = {}
            
            # 查找年份注释和对应的论文内容
            for i in range(3):  # 通常有3个年份的数据
                try:
                    papers_content = root.xpath(f'/html/body/main/div[2]/div[{i + 1}]')[0].text_content()
                    year_comment = str(root.xpath(f'/html/body/main/div[2]/comment()[{i + 2}]')[0])
                    
                    # 从注释中提取年份
                    year_match = re.search(r'(\d{4})', year_comment)
                    if year_match:
                        year = year_match.group(1)
                        paper_year_mapping[year] = papers_content
                
                except (IndexError, AttributeError) as e:
                    logger.debug(f"解析年份映射失败 {i}: {e}")
                    continue
            
            logger.info(f"获得年份映射: {list(paper_year_mapping.keys())}")
            return paper_year_mapping
            
        except Exception as e:
            logger.error(f"获取年份映射失败: {e}")
            return {}
    
    def crawl_papers(self, 
                    conference: str,
                    year: int,
                    keywords: Optional[List[str]] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None) -> List[Dict]:
        """
        爬取ECCV论文
        Crawl ECCV papers
        
        Args:
            conference: 会议名称 (应该是'ECCV') Conference name (should be 'ECCV')
            year: 年份 Year
            keywords: 关键词列表 Keywords list
            date_from: 开始日期 Start date (暂未使用)
            date_to: 结束日期 End date (暂未使用)
            
        Returns:
            List[Dict]: 论文数据列表 Paper data list
        """
        logger.info(f"开始爬取 ECCV {year} 论文")
        
        if year not in self.supported_years:
            raise ValueError(f"ECCV 不支持的年份: {year}")
        
        try:
            # 获取页面内容
            response = self.make_request(self.papers_url)
            soup = self.parse_html(response.text)
            
            # 获取年份映射
            year_mapping = self.get_year_papers_mapping()
            year_str = str(year)
            
            if year_str not in year_mapping:
                logger.warning(f"未找到 {year} 年的论文数据")
                return []
            
            # 获取论文标题和PDF链接
            paper_titles = soup.find_all('dt', class_='ptitle')
            paper_pdfs = soup.find_all('dd')[1::2]  # 每隔一个dd元素是PDF链接
            
            if len(paper_titles) != len(paper_pdfs):
                logger.warning(f"论文标题和PDF数量不匹配: {len(paper_titles)} vs {len(paper_pdfs)}")
            
            papers = []
            
            for i, (title_elem, pdf_elem) in enumerate(zip(paper_titles, paper_pdfs)):
                try:
                    # 提取标题
                    title = self.clean_text(title_elem.get_text())
                    if not title:
                        continue
                    
                    # 检查论文是否属于指定年份
                    if title not in year_mapping[year_str]:
                        continue
                    
                    # 关键词过滤
                    if keywords:
                        title_lower = title.lower()
                        
                        keyword_match = False
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                keyword_match = True
                                break
                        
                        if not keyword_match:
                            continue
                    
                    # 提取PDF链接
                    pdf_url = ""
                    pdf_link = pdf_elem.find('a')
                    if pdf_link:
                        pdf_href = pdf_link.get('href', '')
                        if pdf_href:
                            pdf_url = urljoin(self.base_url, pdf_href)
                    
                    # 提取论文页面链接
                    paper_url = ""
                    title_link = title_elem.find('a')
                    if title_link:
                        paper_href = title_link.get('href', '')
                        if paper_href:
                            paper_url = urljoin(self.base_url, paper_href)
                    
                    # 提取关键词
                    extracted_keywords = self.extract_keywords(title)
                    
                    investment_match = self.match_investment_keywords(title)
                    
                    # 创建标准化的论文数据
                    paper_data = PaperData.create_paper_dict(
                        title=title,
                        authors=[],  # ECCV列表页不显示作者
                        conference='ECCV',
                        year=year,
                        abstract='',  # 列表页不显示摘要
                        paper_url=paper_url,
                        pdf_url=pdf_url,
                        publication_date=datetime(year, 8, 1),  # ECCV通常8月举办
                        keywords=extracted_keywords,
                        hot_topic_match=investment_match['hot_topic_match'],
                        commercial_potential=investment_match['commercial_potential'],
                        matched_topics=investment_match['matched_topics'],
                        data_source="eccv"
                    )
                    
                    papers.append(paper_data)
                    
                except Exception as e:
                    logger.warning(f"处理ECCV论文 {i+1} 失败: {e}")
                    continue
            
            logger.info(f"ECCV {year} 爬取完成，共获得 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"爬取 ECCV {year} 失败: {e}")
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
        'investment_keywords': {
            'hot_topics': ['transformer', 'diffusion', 'object detection'],
            'commercial_indicators': ['industry', 'production', 'deployment']
        }
    }
    
    # 测试CVF爬虫
    cvf_crawler = CVFCrawler(config)
    
    try:
        # 爬取CVPR 2024的论文
        papers = cvf_crawler.crawl_papers(
            conference='CVPR',
            year=2024,
            keywords=['transformer', 'diffusion']  # 可选的关键词过滤
        )
        
        print(f"CVF: 成功爬取 {len(papers)} 篇论文")
        
        # 显示前几篇论文
        for i, paper in enumerate(papers[:3]):
            print(f"\n论文 {i+1}:")
            print(f"标题: {paper['title']}")
            print(f"会议: {paper['conference']} {paper['year']}")
            print(f"PDF链接: {paper['pdf_url']}")
        
    finally:
        cvf_crawler.close()
    
    # 测试ECCV爬虫
    eccv_crawler = ECCVCrawler(config)
    
    try:
        # 爬取ECCV 2022的论文
        papers = eccv_crawler.crawl_papers(
            conference='ECCV',
            year=2022,
            keywords=['transformer']
        )
        
        print(f"\nECCV: 成功爬取 {len(papers)} 篇论文")
        
    finally:
        eccv_crawler.close()