"""
调试ICLR 2025爬虫 - 检查页面结构和可用数据
Debug ICLR 2025 Crawler - Check page structure and available data
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_iclr_2025():
    """调试ICLR 2025页面"""
    driver = None
    
    try:
        # 设置Chrome选项
        options = Options()
        options.add_argument('--headless=false')  # 显示浏览器以便调试
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        
        # 初始化WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 访问ICLR 2025页面
        urls_to_try = [
            'https://openreview.net/group?id=ICLR.cc/2025/Conference',
            'https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-active-submissions',
            'https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-withdrawn-submissions',
            'https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-desk-rejected-submissions'
        ]
        
        for url in urls_to_try:
            print(f"\n{'='*80}")
            print(f"正在检查URL: {url}")
            print(f"{'='*80}")
            
            driver.get(url)
            time.sleep(5)  # 等待页面加载
            
            # 检查页面标题
            title = driver.title
            print(f"页面标题: {title}")
            
            # 检查是否有错误信息
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".alert, .error, .warning")
                if error_elements:
                    print("发现错误/警告信息:")
                    for elem in error_elements:
                        print(f"  - {elem.text}")
            except:
                pass
            
            # 查找导航标签
            try:
                nav_tabs = driver.find_elements(By.CSS_SELECTOR, ".nav-tabs li a, .nav.nav-tabs li a")
                print(f"\n找到 {len(nav_tabs)} 个导航标签:")
                for i, tab in enumerate(nav_tabs):
                    try:
                        tab_text = tab.text.strip()
                        tab_id = tab.get_attribute("aria-controls") or tab.get_attribute("href")
                        print(f"  {i+1}. {tab_text} (ID: {tab_id})")
                    except Exception as e:
                        print(f"  {i+1}. 无法读取标签信息: {e}")
            except Exception as e:
                print(f"查找导航标签失败: {e}")
            
            # 查找论文相关元素
            paper_selectors = [
                "li.note",
                ".note-content",
                "h4 a[href*='/forum?id=']",
                ".list-unstyled li",
                "[class*='paper']",
                "[class*='submission']"
            ]
            
            print(f"\n查找论文元素:")
            for selector in paper_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"  {selector}: 找到 {len(elements)} 个元素")
                    
                    # 显示前几个元素的内容
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 20:
                                print(f"    - {text[:100]}...")
                        except:
                            pass
                except Exception as e:
                    print(f"  {selector}: 查找失败 - {e}")
            
            # 检查页面源码中的关键信息
            page_source = driver.page_source.lower()
            
            keywords_to_check = [
                'submission', 'under review', 'accepted', 'rejected', 
                'withdrawn', 'decision', 'paper', 'forum', 'iclr', '2025'
            ]
            
            print(f"\n页面源码关键词检查:")
            for keyword in keywords_to_check:
                count = page_source.count(keyword)
                if count > 0:
                    print(f"  '{keyword}': 出现 {count} 次")
            
            # 检查是否有分页
            pagination_elements = driver.find_elements(By.CSS_SELECTOR, ".pagination, .pager, nav[aria-label*='pagination']")
            print(f"\n分页元素: 找到 {len(pagination_elements)} 个")
            
            # 检查是否有加载更多按钮
            load_more_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='load'], [class*='more'], button[class*='show']")
            print(f"加载更多按钮: 找到 {len(load_more_elements)} 个")
            
            # 暂停以便手动检查
            if not options.arguments or '--headless=false' in str(options.arguments):
                input("按Enter继续到下一个URL...")
    
    except Exception as e:
        logger.error(f"调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print("开始调试ICLR 2025页面结构...")
    debug_iclr_2025()