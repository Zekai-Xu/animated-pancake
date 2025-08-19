"""
AI学术论文监控系统 - 图形用户界面
AI Academic Paper Monitoring System - Graphical User Interface

基于Streamlit的用户友好界面
User-friendly interface based on Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import os
import sys
import logging
from typing import List, Dict, Optional
import yaml

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import PaperMonitoringSystem

# 配置页面
st.set_page_config(
    page_title="AI学术论文监控系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_config():
    """加载配置文件"""
    try:
        with open('config/config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"加载配置文件失败: {e}")
        return {}


@st.cache_resource
def initialize_system():
    """初始化监控系统"""
    try:
        return PaperMonitoringSystem()
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        return None


def display_header():
    """显示页面头部"""
    st.markdown('<h1 class="main-header">🤖 AI学术论文监控系统</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #6c757d;">
            专为AI投资人设计的学术论文监控和分析平台<br>
            <em>Academic Paper Monitoring Platform for AI Investors</em>
        </p>
    </div>
    """, unsafe_allow_html=True)


def sidebar_configuration():
    """侧边栏配置"""
    st.sidebar.markdown("## 📋 系统配置")
    
    # 会议选择
    config = load_config()
    all_conferences = []
    if config:
        for category in config.get('conferences', {}).values():
            all_conferences.extend([conf['name'] for conf in category])
    
    selected_conferences = st.sidebar.multiselect(
        "选择会议 (Conference)",
        options=all_conferences,
        default=['ICLR', 'CVPR', 'NeurIPS'],
        help="选择要监控的学术会议"
    )
    
    # 年份选择
    current_year = datetime.now().year
    years_options = list(range(2020, current_year + 1))
    selected_years = st.sidebar.multiselect(
        "选择年份 (Years)",
        options=years_options,
        default=[current_year - 1, current_year],
        help="选择要分析的年份范围"
    )
    
    # 关键词输入
    keywords_input = st.sidebar.text_area(
        "关键词过滤 (Keywords)",
        value="transformer, diffusion model, large language model",
        help="输入关键词，用逗号分隔。留空则不过滤"
    )
    
    keywords = []
    if keywords_input.strip():
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    
    # 日期范围
    st.sidebar.markdown("### 📅 日期范围")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        date_from = st.date_input(
            "开始日期",
            value=date(current_year, 1, 1),
            help="论文发表的开始日期"
        )
    
    with col2:
        date_to = st.date_input(
            "结束日期",
            value=date.today(),
            help="论文发表的结束日期"
        )
    
    # 高级设置
    st.sidebar.markdown("### ⚙️ 高级设置")
    
    include_citations = st.sidebar.checkbox(
        "包含引用数据",
        value=False,
        help="获取论文引用数据 (耗时较长)"
    )
    
    min_score_threshold = st.sidebar.slider(
        "最小投资评分阈值",
        min_value=0.0,
        max_value=10.0,
        value=6.0,
        step=0.1,
        help="只显示评分高于此阈值的论文"
    )
    
    return {
        'conferences': selected_conferences,
        'years': selected_years,
        'keywords': keywords,
        'date_from': datetime.combine(date_from, datetime.min.time()) if date_from else None,
        'date_to': datetime.combine(date_to, datetime.max.time()) if date_to else None,
        'include_citations': include_citations,
        'min_score_threshold': min_score_threshold
    }


def display_monitoring_results(papers_data: List[Dict]):
    """显示监控结果"""
    if not papers_data:
        st.warning("未找到符合条件的论文数据")
        return
    
    # 统计信息
    st.markdown('<h2 class="sub-header">📊 统计概览</h2>', unsafe_allow_html=True)
    
    total_papers = len(papers_data)
    high_value_papers = len([p for p in papers_data if p.get('investment_score', 0) >= 8.0])
    avg_score = sum([p.get('investment_score', 0) for p in papers_data]) / total_papers if total_papers > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="论文总数",
            value=total_papers,
            help="本次分析的论文总数量"
        )
    
    with col2:
        st.metric(
            label="高价值论文",
            value=high_value_papers,
            delta=f"{high_value_papers/total_papers*100:.1f}%" if total_papers > 0 else "0%",
            help="投资评分 ≥ 8.0 的论文数量"
        )
    
    with col3:
        st.metric(
            label="平均投资评分",
            value=f"{avg_score:.2f}",
            help="所有论文的平均投资评分"
        )
    
    with col4:
        conferences_count = len(set([p.get('conference', 'Unknown') for p in papers_data]))
        st.metric(
            label="涉及会议数",
            value=conferences_count,
            help="涵盖的学术会议数量"
        )
    
    # 可视化图表
    st.markdown('<h2 class="sub-header">📈 数据可视化</h2>', unsafe_allow_html=True)
    
    # 创建图表标签页
    tab1, tab2, tab3, tab4 = st.tabs(["投资评分分布", "会议分析", "技术趋势", "时间分析"])
    
    with tab1:
        # 投资评分分布直方图
        scores = [p.get('investment_score', 0) for p in papers_data]
        fig_hist = px.histogram(
            x=scores,
            nbins=20,
            title="论文投资评分分布",
            labels={'x': '投资评分', 'y': '论文数量'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab2:
        # 按会议分析
        conference_stats = {}
        conference_scores = {}
        
        for paper in papers_data:
            conf = paper.get('conference', 'Unknown')
            score = paper.get('investment_score', 0)
            
            if conf not in conference_stats:
                conference_stats[conf] = 0
                conference_scores[conf] = []
            
            conference_stats[conf] += 1
            conference_scores[conf].append(score)
        
        # 计算平均分
        for conf in conference_scores:
            conference_scores[conf] = sum(conference_scores[conf]) / len(conference_scores[conf])
        
        # 会议论文数量柱状图
        fig_bar = px.bar(
            x=list(conference_stats.keys()),
            y=list(conference_stats.values()),
            title="各会议论文数量",
            labels={'x': '会议', 'y': '论文数量'},
            color=list(conference_scores.values()),
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # 会议平均评分散点图
        fig_scatter = px.scatter(
            x=list(conference_stats.values()),
            y=list(conference_scores.values()),
            text=list(conference_stats.keys()),
            title="会议论文数量 vs 平均投资评分",
            labels={'x': '论文数量', 'y': '平均投资评分'},
            size=[20] * len(conference_stats)
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        # 技术趋势分析
        tech_trends = analyze_tech_trends(papers_data)
        
        if tech_trends:
            # 技术领域论文数量
            fig_pie = px.pie(
                values=list(tech_trends.values()),
                names=list(tech_trends.keys()),
                title="技术领域分布"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab4:
        # 时间分析
        year_stats = {}
        for paper in papers_data:
            year = paper.get('year', 'Unknown')
            if year not in year_stats:
                year_stats[year] = 0
            year_stats[year] += 1
        
        # 按年份统计
        sorted_years = sorted([y for y in year_stats.keys() if isinstance(y, int)])
        year_counts = [year_stats[y] for y in sorted_years]
        
        fig_line = px.line(
            x=sorted_years,
            y=year_counts,
            title="论文数量年度趋势",
            labels={'x': '年份', 'y': '论文数量'},
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # 高价值论文列表
    st.markdown('<h2 class="sub-header">⭐ 高价值论文推荐</h2>', unsafe_allow_html=True)
    
    high_value_papers_list = [p for p in papers_data if p.get('investment_score', 0) >= 8.0]
    high_value_papers_list.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
    
    if high_value_papers_list:
        for i, paper in enumerate(high_value_papers_list[:10], 1):  # 显示前10篇
            with st.expander(f"#{i} {paper.get('title', 'Unknown Title')} (评分: {paper.get('investment_score', 0):.2f})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**会议**: {paper.get('conference', 'Unknown')} {paper.get('year', 'Unknown')}")
                    
                    # 解析作者
                    try:
                        authors = json.loads(paper.get('authors', '[]')) if isinstance(paper.get('authors'), str) else paper.get('authors', [])
                        if authors:
                            st.write(f"**作者**: {', '.join(authors[:3])}{'等' if len(authors) > 3 else ''}")
                    except:
                        st.write("**作者**: 未知")
                    
                    if paper.get('abstract'):
                        st.write(f"**摘要**: {paper.get('abstract', '')[:200]}...")
                
                with col2:
                    st.write(f"**投资建议**: {paper.get('investment_recommendation', '未知')}")
                    st.write(f"**技术成熟度**: {paper.get('technology_maturity', '未知')}")
                    st.write(f"**商业潜力**: {paper.get('commercial_potential_score', 0):.2f}")
                    st.write(f"**市场规模**: {paper.get('market_size_estimate', '未知')}")
                    
                    if paper.get('paper_url'):
                        st.markdown(f"[📄 查看论文]({paper.get('paper_url')})")
                    if paper.get('pdf_url'):
                        st.markdown(f"[📥 下载PDF]({paper.get('pdf_url')})")
    else:
        st.info("未找到高价值论文 (评分 ≥ 8.0)")


def analyze_tech_trends(papers_data: List[Dict]) -> Dict[str, int]:
    """分析技术趋势"""
    tech_categories = {
        'Large Language Model': ['large language model', 'llm', 'language model', 'gpt', 'bert'],
        'Computer Vision': ['computer vision', 'image', 'visual', 'detection', 'segmentation'],
        'Diffusion Model': ['diffusion', 'diffusion model', 'stable diffusion'],
        'Transformer': ['transformer', 'attention', 'self-attention'],
        'Multimodal': ['multimodal', 'multi-modal', 'vision-language'],
        'Reinforcement Learning': ['reinforcement learning', 'rl', 'policy'],
        'Graph Neural Network': ['graph', 'gnn', 'graph neural network'],
        'Natural Language Processing': ['nlp', 'natural language', 'text processing'],
        '其他': []
    }
    
    tech_counts = {tech: 0 for tech in tech_categories.keys()}
    
    for paper in papers_data:
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        text = f"{title} {abstract}"
        
        categorized = False
        for tech, keywords in tech_categories.items():
            if tech == '其他':
                continue
            for keyword in keywords:
                if keyword in text:
                    tech_counts[tech] += 1
                    categorized = True
                    break
            if categorized:
                break
        
        if not categorized:
            tech_counts['其他'] += 1
    
    return {k: v for k, v in tech_counts.items() if v > 0}


def main():
    """主函数"""
    display_header()
    
    # 侧边栏配置
    config = sidebar_configuration()
    
    # 主要内容区域
    st.markdown('<h2 class="sub-header">🚀 开始监控</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("配置完成后，点击 **开始监控** 按钮启动论文爬取和分析流程。")
        
        # 显示当前配置
        with st.expander("📋 当前配置预览", expanded=False):
            st.write(f"**会议**: {', '.join(config['conferences']) if config['conferences'] else '全部'}")
            st.write(f"**年份**: {', '.join(map(str, config['years'])) if config['years'] else '未选择'}")
            st.write(f"**关键词**: {', '.join(config['keywords']) if config['keywords'] else '无过滤'}")
            st.write(f"**日期范围**: {config['date_from'].strftime('%Y-%m-%d') if config['date_from'] else '不限'} 至 {config['date_to'].strftime('%Y-%m-%d') if config['date_to'] else '不限'}")
    
    with col2:
        start_monitoring = st.button(
            "🔍 开始监控",
            type="primary",
            use_container_width=True
        )
    
    # 监控执行
    if start_monitoring:
        if not config['conferences']:
            st.error("请至少选择一个会议！")
            return
        
        if not config['years']:
            st.error("请至少选择一个年份！")
            return
        
        # 显示进度
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 初始化系统
            status_text.text("正在初始化系统...")
            monitor = initialize_system()
            
            if not monitor:
                st.error("系统初始化失败！")
                return
            
            progress_bar.progress(10)
            
            # 爬取数据
            status_text.text("正在爬取论文数据...")
            papers_data = monitor.crawl_papers(
                conferences=config['conferences'],
                years=config['years'],
                keywords=config['keywords'],
                date_from=config['date_from'],
                date_to=config['date_to']
            )
            
            progress_bar.progress(50)
            
            if not papers_data:
                st.warning("未获得任何论文数据，请检查配置或网络连接。")
                return
            
            # 处理和评分
            status_text.text("正在分析和评分论文...")
            scored_papers = monitor.process_and_score_papers(papers_data)
            
            progress_bar.progress(80)
            
            # 过滤低分论文
            filtered_papers = [p for p in scored_papers if p.get('investment_score', 0) >= config['min_score_threshold']]
            
            progress_bar.progress(90)
            
            # 生成报告
            status_text.text("正在生成Excel报告...")
            report_path = monitor.generate_report(filtered_papers)
            
            progress_bar.progress(100)
            status_text.text("监控完成！")
            
            # 显示成功信息
            st.markdown(f"""
            <div class="success-box">
                <h4>✅ 监控完成！</h4>
                <p>成功分析了 <strong>{len(scored_papers)}</strong> 篇论文</p>
                <p>符合评分阈值的论文: <strong>{len(filtered_papers)}</strong> 篇</p>
                <p>Excel报告已生成: <code>{report_path}</code></p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示结果
            display_monitoring_results(filtered_papers)
            
            # 清理资源
            monitor.close()
            
        except Exception as e:
            st.error(f"监控过程中发生错误: {e}")
            st.write("请查看日志文件获取详细错误信息。")
    
    # 帮助信息
    st.markdown("---")
    with st.expander("❓ 使用帮助", expanded=False):
        st.markdown("""
        ### 系统功能
        
        1. **多会议支持**: 支持ICLR、CVPR、ICCV、NeurIPS等主流AI会议
        2. **智能评分**: 基于引用数、技术深度、商业潜力等多维度评分
        3. **投资分析**: 专为投资人设计的分析指标和建议
        4. **Excel报告**: 生成专业的分析报告，包含详细数据和图表
        
        ### 使用步骤
        
        1. 在左侧面板选择要监控的会议和年份
        2. 可选择性输入关键词进行过滤
        3. 设置日期范围和其他高级选项
        4. 点击"开始监控"按钮启动分析
        5. 等待系统完成爬取、分析和评分
        6. 查看结果并下载Excel报告
        
        ### 评分说明
        
        - **投资评分**: 综合评分(1-10分)，考虑引用数、技术深度、商业潜力等因素
        - **8.0+**: 强烈推荐关注的高价值论文
        - **6.5-8.0**: 建议关注的优质论文
        - **5.0-6.5**: 一般关注价值的论文
        
        ### 注意事项
        
        - 首次运行可能需要较长时间
        - 网络连接不稳定可能影响数据获取
        - 某些学术API有访问限制，可能影响引用数据获取
        """)


if __name__ == "__main__":
    main()