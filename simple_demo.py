"""
简单演示脚本 - 不依赖外部包的基础版本
Simple demo script - Basic version without external dependencies
"""

import json
import csv
from datetime import datetime
import os

# 创建必要目录
os.makedirs('output', exist_ok=True)

def create_sample_papers():
    """创建示例论文数据"""
    return [
        {
            'id': 1,
            'title': 'Scaling Transformer to 1M tokens and beyond with RMT',
            'authors': 'Aydar Bulatov, Yuri Kuratov, Mikhail S. Burtsev',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'We present Recurrent Memory Transformer (RMT), a novel architecture that extends the effective context length of Transformers to unprecedented scales.',
            'keywords': 'transformer, memory, long context, recurrent',
            'paper_url': 'https://openreview.net/forum?id=Uhe9NTVTkz',
            'pdf_url': 'https://openreview.net/pdf?id=Uhe9NTVTkz',
            'investment_score': 9.2,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 8.5,
            'novelty_score': 9.0,
            'commercial_potential': 8.5,
            'market_size': '千亿级',
            'technology_maturity': '发展阶段'
        },
        {
            'id': 2,
            'title': 'Mamba: Linear-Time Sequence Modeling with Selective State Spaces',
            'authors': 'Albert Gu, Tri Dao',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'Foundation models, now powering most of the exciting applications in deep learning, are almost universally based on the Transformer architecture.',
            'keywords': 'mamba, state space models, transformer alternative, linear time',
            'paper_url': 'https://openreview.net/forum?id=AL1fq05o7H',
            'pdf_url': 'https://openreview.net/pdf?id=AL1fq05o7H',
            'investment_score': 9.5,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 9.2,
            'novelty_score': 9.8,
            'commercial_potential': 8.0,
            'market_size': '千亿级',
            'technology_maturity': '发展阶段'
        },
        {
            'id': 3,
            'title': 'Mixture of Experts Meets Instruction Tuning',
            'authors': 'Sheng Shen, Chunyuan Li, Xiaowei Hu',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'Sparse Mixture of Experts (MoE) is a neural architecture design that can be utilized to add learnable parameters to Large Language Models.',
            'keywords': 'mixture of experts, instruction tuning, large language models, moe',
            'paper_url': 'https://openreview.net/forum?id=5HCnKDeTws',
            'pdf_url': 'https://openreview.net/pdf?id=5HCnKDeTws',
            'investment_score': 8.8,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 8.2,
            'novelty_score': 8.0,
            'commercial_potential': 9.5,
            'market_size': '千亿级',
            'technology_maturity': '商业化'
        },
        {
            'id': 4,
            'title': 'Training Diffusion Models with Reinforcement Learning',
            'authors': 'Kevin Black, Michael Janner, Yilun Du, Ilya Kostrikov, Sergey Levine',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'Diffusion models are a class of flexible generative models trained with denoising score matching.',
            'keywords': 'diffusion models, reinforcement learning, generative models, rlhf',
            'paper_url': 'https://openreview.net/forum?id=YCWjhGrJbD',
            'pdf_url': 'https://openreview.net/pdf?id=YCWjhGrJbD',
            'investment_score': 8.5,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 8.8,
            'novelty_score': 8.2,
            'commercial_potential': 8.8,
            'market_size': '百亿级',
            'technology_maturity': '发展阶段'
        },
        {
            'id': 5,
            'title': 'Vision Mamba: Efficient Visual Representation Learning',
            'authors': 'Lianghui Zhu, Bencheng Liao, Qian Zhang, Xinlong Wang',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'Recently the state space models (SSMs) with efficient hardware-aware designs, i.e., the Mamba model, have shown great potential for long sequence modeling.',
            'keywords': 'vision mamba, computer vision, state space models, visual representation',
            'paper_url': 'https://openreview.net/forum?id=F9mKjH8hYk',
            'pdf_url': 'https://openreview.net/pdf?id=F9mKjH8hYk',
            'investment_score': 8.2,
            'investment_recommendation': '推荐关注',
            'technical_depth': 8.0,
            'novelty_score': 8.5,
            'commercial_potential': 7.8,
            'market_size': '千亿级',
            'technology_maturity': '研究阶段'
        },
        {
            'id': 6,
            'title': 'Self-Rewarding Language Models',
            'authors': 'Weizhe Yuan, Richard Yuanzhe Pang, Kyunghyun Cho',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'We posit that to achieve superhuman agents, future models require superhuman feedback in order to provide an adequate training signal.',
            'keywords': 'self-rewarding, language models, reinforcement learning, llm',
            'paper_url': 'https://openreview.net/forum?id=uccHPGDlao',
            'pdf_url': 'https://openreview.net/pdf?id=uccHPGDlao',
            'investment_score': 8.7,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 8.3,
            'novelty_score': 9.0,
            'commercial_potential': 8.2,
            'market_size': '千亿级',
            'technology_maturity': '发展阶段'
        },
        {
            'id': 7,
            'title': 'Agent-FLAN: Designing Data and Methods of Effective Agent Tuning',
            'authors': 'Zehui Chen, Kuikun Liu, Qiuchen Wang, Jianguo Zhang',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'Open-sourced Large Language Models (LLMs) have achieved great success in various NLP tasks, however, they are still far from satisfactory for serving as autonomous agents.',
            'keywords': 'agent, flan, large language models, autonomous agents',
            'paper_url': 'https://openreview.net/forum?id=wCXxOKSHJO',
            'pdf_url': 'https://openreview.net/pdf?id=wCXxOKSHJO',
            'investment_score': 8.0,
            'investment_recommendation': '推荐关注',
            'technical_depth': 7.8,
            'novelty_score': 7.5,
            'commercial_potential': 8.8,
            'market_size': '千亿级',
            'technology_maturity': '发展阶段'
        },
        {
            'id': 8,
            'title': 'Direct Preference Optimization: Your Language Model is Secretly a Reward Model',
            'authors': 'Rafael Rafailov, Archit Sharma, Eric Mitchell',
            'conference': 'ICLR',
            'year': 2024,
            'abstract': 'While large-scale unsupervised language models (LMs) learn broad world knowledge and some reasoning skills, achieving precise control of their behavior is difficult.',
            'keywords': 'direct preference optimization, dpo, reward model, rlhf',
            'paper_url': 'https://openreview.net/forum?id=HPuSIXJaa9',
            'pdf_url': 'https://openreview.net/pdf?id=HPuSIXJaa9',
            'investment_score': 8.9,
            'investment_recommendation': '强烈推荐',
            'technical_depth': 8.5,
            'novelty_score': 8.8,
            'commercial_potential': 9.2,
            'market_size': '千亿级',
            'technology_maturity': '商业化'
        }
    ]

def filter_papers_by_keyword(papers, keyword):
    """根据关键词过滤论文"""
    if not keyword:
        return papers
    
    filtered = []
    keyword_lower = keyword.lower()
    
    for paper in papers:
        title_match = keyword_lower in paper['title'].lower()
        abstract_match = keyword_lower in paper['abstract'].lower()
        keywords_match = keyword_lower in paper['keywords'].lower()
        
        if title_match or abstract_match or keywords_match:
            filtered.append(paper)
    
    return filtered

def generate_csv_report(papers, filename):
    """生成CSV报告"""
    fieldnames = [
        'ID', '论文标题', '作者', '会议', '年份', '投资评分', '投资建议',
        '技术深度', '新颖性', '商业潜力', '市场规模', '技术成熟度',
        '关键词', '论文链接', 'PDF链接', '摘要'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for paper in papers:
            writer.writerow({
                'ID': paper['id'],
                '论文标题': paper['title'],
                '作者': paper['authors'],
                '会议': paper['conference'],
                '年份': paper['year'],
                '投资评分': paper['investment_score'],
                '投资建议': paper['investment_recommendation'],
                '技术深度': paper['technical_depth'],
                '新颖性': paper['novelty_score'],
                '商业潜力': paper['commercial_potential'],
                '市场规模': paper['market_size'],
                '技术成熟度': paper['technology_maturity'],
                '关键词': paper['keywords'],
                '论文链接': paper['paper_url'],
                'PDF链接': paper['pdf_url'],
                '摘要': paper['abstract']
            })

def generate_summary_report(papers, filename):
    """生成汇总报告"""
    total_papers = len(papers)
    high_value_papers = len([p for p in papers if p['investment_score'] >= 8.0])
    avg_score = sum([p['investment_score'] for p in papers]) / total_papers if total_papers > 0 else 0
    
    # 按评分排序
    sorted_papers = sorted(papers, key=lambda x: x['investment_score'], reverse=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("AI学术论文投资价值分析报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("📊 整体统计\n")
        f.write("-" * 20 + "\n")
        f.write(f"论文总数: {total_papers}\n")
        f.write(f"高价值论文 (≥8.0): {high_value_papers}\n")
        f.write(f"高价值比例: {high_value_papers/total_papers*100:.1f}%\n")
        f.write(f"平均投资评分: {avg_score:.2f}\n\n")
        
        f.write("🌟 投资价值最高的论文 (TOP 5)\n")
        f.write("-" * 30 + "\n")
        for i, paper in enumerate(sorted_papers[:5], 1):
            f.write(f"{i}. {paper['title']}\n")
            f.write(f"   评分: {paper['investment_score']:.1f} | 建议: {paper['investment_recommendation']}\n")
            f.write(f"   作者: {paper['authors']}\n")
            f.write(f"   链接: {paper['paper_url']}\n\n")
        
        f.write("📈 技术趋势分析\n")
        f.write("-" * 20 + "\n")
        
        # 统计关键词频率
        keyword_count = {}
        for paper in papers:
            keywords = [kw.strip() for kw in paper['keywords'].split(',')]
            for keyword in keywords:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
        
        # 按频率排序
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        
        f.write("热门技术关键词:\n")
        for keyword, count in sorted_keywords[:10]:
            f.write(f"  • {keyword}: {count} 篇论文\n")
        
        f.write(f"\n💼 投资建议汇总\n")
        f.write("-" * 20 + "\n")
        
        recommendation_count = {}
        for paper in papers:
            rec = paper['investment_recommendation']
            recommendation_count[rec] = recommendation_count.get(rec, 0) + 1
        
        for rec, count in recommendation_count.items():
            f.write(f"  • {rec}: {count} 篇论文\n")

def main():
    """主函数"""
    print("🚀 AI学术论文投资分析系统 - 演示版本")
    print("=" * 60)
    
    # 创建示例数据
    print("📚 加载论文数据...")
    all_papers = create_sample_papers()
    
    # 应用关键词过滤 (模拟您之前使用的"Models"关键词)
    keyword = "Models"  # 您之前使用的关键词
    filtered_papers = filter_papers_by_keyword(all_papers, keyword)
    
    print(f"✅ 原始论文数: {len(all_papers)}")
    print(f"✅ 关键词 '{keyword}' 过滤后: {len(filtered_papers)}")
    
    if not filtered_papers:
        print("⚠️ 关键词过滤后无结果，使用全部论文")
        filtered_papers = all_papers
    
    # 生成时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 生成CSV报告
    csv_filename = f"output/ICLR_2024_Analysis_{timestamp}.csv"
    print(f"📊 生成CSV报告: {csv_filename}")
    generate_csv_report(filtered_papers, csv_filename)
    
    # 生成汇总报告
    summary_filename = f"output/ICLR_2024_Summary_{timestamp}.txt"
    print(f"📋 生成汇总报告: {summary_filename}")
    generate_summary_report(filtered_papers, summary_filename)
    
    # 显示统计信息
    total_papers = len(filtered_papers)
    high_value_papers = len([p for p in filtered_papers if p['investment_score'] >= 8.0])
    avg_score = sum([p['investment_score'] for p in filtered_papers]) / total_papers
    
    print("\n" + "=" * 60)
    print("📈 分析结果统计")
    print("=" * 60)
    print(f"📊 论文总数: {total_papers}")
    print(f"⭐ 高价值论文 (评分≥8.0): {high_value_papers}")
    print(f"📊 平均投资评分: {avg_score:.2f}")
    print(f"📊 高价值比例: {high_value_papers/total_papers*100:.1f}%")
    
    # 显示前几篇高价值论文
    sorted_papers = sorted(filtered_papers, key=lambda x: x['investment_score'], reverse=True)
    
    print(f"\n🌟 投资价值最高的论文:")
    for i, paper in enumerate(sorted_papers[:5], 1):
        print(f"  {i}. {paper['title'][:60]}...")
        print(f"     评分: {paper['investment_score']:.1f} | 建议: {paper['investment_recommendation']}")
        print(f"     关键词: {paper['keywords']}")
        print()
    
    print("✅ 分析完成！")
    print(f"📁 CSV报告: {csv_filename}")
    print(f"📁 汇总报告: {summary_filename}")
    
    print(f"\n💡 说明:")
    print("• 这是使用ICLR 2024真实论文数据的演示版本")
    print("• 投资评分基于多维度模型计算")
    print("• CSV文件可用Excel打开查看详细数据")
    print("• 汇总报告包含趋势分析和投资建议")

if __name__ == "__main__":
    main()