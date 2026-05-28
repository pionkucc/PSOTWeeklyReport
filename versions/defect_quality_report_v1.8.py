"""
缺陷质量分析可视化报告生成器
生成清新UI风格的交互式HTML图表 (卡片平铺布局)

使用方法:
    python defect_quality_report.py

输出文件:
    缺陷质量分析报告.html
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ============ 配置区 ============

COLORS = {
    'pastel': ['#A8D8EA', '#AA96DA', '#FCBAD3', '#FFFFD2', '#C4E1C1', '#F9D5A7', '#B8E0D2', '#D6EADF'],
    'fresh': ['#7FB3D5', '#76D7C4', '#F7DC6F', '#F0B27A', '#E59866', '#AF7AC5', '#85C1E9', '#82E0AA'],
    'status': {'New': '#F7DC6F', 'Closed': '#82E0AA', 'ReOpen': '#F0B27A', 'Pending': '#85C1E9', 'Fixed': '#76D7C4'},
    'status_soft': {'Closed': '#B8E0D2', 'Fixed': '#D6EADF', 'New': '#A8D8EA', 'Pending': '#AA96DA', 'ReOpen': '#F9D5A7'},
    'priority': {'优先': '#E57373', '高': '#FFB74D', '中': '#64B5F6', '低': '#81C784'},
    'severity': {'严重': '#E57373', '一般': '#FFB74D', '轻微': '#64B5F6', '建议': '#81C784'},
    'stage_find': {
        '2.1-系统测试【基本流】': '#A8D8EA',
        '2.2-系统测试【备选流】': '#AA96DA',
        '4.1-回归测试【基本流】': '#FCBAD3',
        '4.2-回归测试【备选流】': '#FFFFD2'
    }
}

INPUT_FILE = '缺陷明细.xlsx'
OUTPUT_FILE = '缺陷质量分析报告.html'
TITLE = 'POST-产品标准化运营工具-质量周报'
SUBTITLE = '2026-05-18 ~ 2026-05-22'

# ============ 数据读取 ============

df = pd.read_excel(INPUT_FILE)
total = len(df)

# 从sheet2读取任务项统计
df_sheet2 = pd.read_excel(INPUT_FILE, sheet_name=1)
# 任务项数量（排除合计行）
task_count = len(df_sheet2) - 1  # 排除最后一行合计
# 子任务项数量（从合计行的第4列获取：关联任务项（子任务））
subtask_count = df_sheet2.iloc[-1, 4] if len(df_sheet2) > 0 else 0

# ============ 图表生成函数 ============

def create_pie_chart(data, title, hole=0.4, colors=None, height=350, legend_y=-0.2):
    """创建饼图"""
    counts = data.value_counts()

    if len(counts) == 0:
        fig = go.Figure()
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    else:
        marker_colors = colors if colors else COLORS['pastel'][:len(counts)]
        fig = go.Figure(go.Pie(
            labels=counts.index, values=counts.values,
            hole=hole, marker_colors=marker_colors,
            textinfo='percent', textposition='inside',
            textfont={'size': 14, 'color': '#34495e', 'family': 'Microsoft YaHei'},
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>',
            showlegend=True
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        margin=dict(t=50, l=20, r=20, b=60),
        height=height,
        showlegend=True if len(counts) > 0 else False,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=legend_y,
            xanchor='center',
            x=0.5,
            font={'size': 12, 'family': 'Microsoft YaHei'},
            itemwidth=30,
            itemsizing='constant'
        )
    )
    return fig

def create_bar_chart(data, title, orientation='v', colors=None, height=350, x_label='', y_label='数量', show_legend=False, order=None, legend_y=-0.45):
    """创建柱状图"""
    counts = data.value_counts()

    # 如果指定了顺序，使用预定义顺序（支持预留图例）
    if order is not None and show_legend:
        # 创建完整顺序，包含预留项（值为0）
        full_counts = {}
        for o in order:
            full_counts[o] = counts.get(o, 0)
        counts = pd.Series(full_counts)
    elif order is not None:
        # 无图例版本，只显示有数据的项
        counts = counts.reindex([o for o in order if o in counts.index])

    fig = go.Figure()

    if len(counts) == 0:
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    elif show_legend:
        # 添加图例版本：每个类别单独一个trace，颜色按counts.index顺序对应
        chart_colors = colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)]

        for i, (label, value) in enumerate(zip(counts.index, counts.values)):
            if orientation == 'v':
                fig.add_trace(go.Bar(
                    x=[label], y=[value],
                    name=label,
                    marker_color=chart_colors[i],
                    marker_line_color='white', marker_line_width=2,
                    text=[value] if value > 0 else None, textposition='outside',
                    textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                    hovertemplate=f'<b>{label}</b><br>数量: {value}个<extra></extra>',
                    opacity=0.85 if value > 0 else 0.3,
                    showlegend=True
                ))
            else:
                fig.add_trace(go.Bar(
                    x=[value], y=[label], orientation='h',
                    name=label,
                    marker_color=chart_colors[i],
                    marker_line_color='white', marker_line_width=2,
                    text=[value] if value > 0 else None, textposition='outside',
                    textfont={'size': 12, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                    hovertemplate=f'<b>{label}</b><br>数量: {value}个<extra></extra>',
                    opacity=0.85 if value > 0 else 0.3,
                    showlegend=True
                ))

        if orientation == 'v':
            fig.update_xaxes(tickfont={'size': 11, 'family': 'Microsoft YaHei'})
        else:
            fig.update_yaxes(tickfont={'size': 10, 'family': 'Microsoft YaHei'})
    else:
        # 无图例版本
        if orientation == 'v':
            fig.add_trace(go.Bar(
                x=counts.index, y=counts.values,
                marker_color=colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)],
                marker_line_color='white', marker_line_width=2,
                text=counts.values, textposition='outside',
                textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                hovertemplate='<b>%{x}</b><br>数量: %{y}个<extra></extra>',
                opacity=0.85
            ))
            fig.update_xaxes(tickfont={'size': 11, 'family': 'Microsoft YaHei'})
        else:
            fig.add_trace(go.Bar(
                x=counts.values, y=counts.index, orientation='h',
                marker_color=colors[:len(counts)] if colors else COLORS['fresh'][:len(counts)],
                marker_line_color='white', marker_line_width=2,
                text=counts.values, textposition='outside',
                textfont={'size': 12, 'color': '#34495e', 'family': 'Microsoft YaHei'},
                hovertemplate='<b>%{y}</b><br>数量: %{x}个<extra></extra>',
                opacity=0.85
            ))
            fig.update_yaxes(tickfont={'size': 10, 'family': 'Microsoft YaHei'})

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        plot_bgcolor='#fafafa',
        margin=dict(t=50, l=20, r=20, b=100),
        height=height + 50 if show_legend else height,
        xaxis_title=x_label, yaxis_title=y_label,
        barmode='group' if show_legend else 'relative',
        showlegend=show_legend if len(counts) > 0 else False,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=legend_y,
            xanchor='center',
            x=0.5,
            font={'size': 10, 'family': 'Microsoft YaHei'},
            itemwidth=30,
            itemsizing='constant',
            tracegroupgap=0,
            valign='middle',
            itemclick=False,
            itemdoubleclick=False
        ) if show_legend else None
    )
    fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
    return fig

def create_histogram(data, title, height=300):
    """创建直方图"""
    fig = go.Figure()

    if len(data) == 0:
        fig.add_annotation(text='暂无数据', x=0.5, y=0.5, showarrow=False,
                          font={'size': 16, 'color': '#999', 'family': 'Microsoft YaHei'})
    else:
        fig.add_trace(go.Histogram(
            x=data, nbinsx=int(data.max()) + 1,
            marker_color='#7FB3D5', marker_line_color='white', marker_line_width=2,
            opacity=0.85,
            hovertemplate='修复周期: %{x}天<br>数量: %{y}个<extra></extra>'
        ))

        mean_val = data.mean()
        fig.add_annotation(
            x=mean_val, y=1.05,
            text=f'平均 {mean_val:.1f}天',
            showarrow=False,
            font=dict(size=12, color='#E74C3C', family='Microsoft YaHei'),
            xref='x domain', yref='y domain'
        )

    fig.update_layout(
        title=dict(text=title, x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
        paper_bgcolor='white',
        plot_bgcolor='#fafafa',
        margin=dict(t=50, l=60, r=30, b=50),
        height=height,
        xaxis_title='修复周期(天)', yaxis_title='数量'
    )
    fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
    return fig

def create_metrics_cards_html():
    """创建质量指标卡片HTML (5个小卡片平铺)"""
    global task_count, subtask_count

    closed = len(df[df['缺陷状态'] == 'Closed'])
    legacy_count = len(df[df['缺陷状态'] != 'Closed'])  # 遗留缺陷：非Closed状态
    close_rate = closed / total * 100 if total > 0 else 0

    # 基本流占比（发现阶段包含"基本流"的缺陷）
    df['发现阶段'] = df['发现阶段'].str.strip()
    basic_flow = len(df[df['发现阶段'].str.contains('基本流', na=False)])
    basic_flow_rate = basic_flow / total * 100 if total > 0 else 0

    # 返工率（返工次数>0的缺陷）
    rework = len(df[df['返工次数'] > 0])
    rework_rate = rework / total * 100 if total > 0 else 0

    # 平均修复时长（天）
    fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
    fix_period = pd.to_numeric(fix_period, errors='coerce')
    avg_fix_time = fix_period.mean()
    max_fix_time = fix_period.max()
    min_fix_time = fix_period.min()
    avg_fix_time_str = f'{avg_fix_time:.2f}天' if avg_fix_time > 0 else '--'
    max_fix_time_str = f'{max_fix_time:.0f}天' if max_fix_time > 0 else '--'
    min_fix_time_str = f'{min_fix_time:.0f}天' if min_fix_time > 0 else '--'

    cards = [
        ('任务项', f'{task_count}个', 'linear-gradient(135deg, #A8D8EA 0%, #B8E0D2 100%)', 'icon-task', f'子任务项{subtask_count}个'),
        ('平均修复时长', avg_fix_time_str, 'linear-gradient(135deg, #F7DC6F 0%, #F9D5A7 100%)', 'icon-clock', f'最大{max_fix_time_str}<br>最小{min_fix_time_str}'),
        ('遗留缺陷', f'{legacy_count}个', 'linear-gradient(135deg, #82E0AA 0%, #A8D8EA 100%)', 'icon-bug', f'关闭率{close_rate:.1f}%'),
        ('基本流占比', f'{basic_flow_rate:.1f}%', 'linear-gradient(135deg, #F0B27A 0%, #FCBAD3 100%)', 'icon-chart', f'{basic_flow}/{total}个'),
        ('返工率', f'{rework_rate:.1f}%', 'linear-gradient(135deg, #AA96DA 0%, #D6EADF 100%)', 'icon-refresh', f'{rework}/{total}个')
    ]

    cards_html = ''.join([
        f'<div class="metric-card" style="background:{c[2]}">'
        f'<div class="metric-header">'
        f'<span class="metric-name">{c[0]}</span>'
        f'<div class="metric-icon {c[3]}"></div>'
        f'</div>'
        f'<div class="metric-value">{c[1]}</div>'
        f'<div class="metric-subtitle">{c[4]}</div>'
        f'</div>'
        for c in cards
    ])

    return f'<div class="metrics-container"><div class="metrics-title">质量指标概览</div><div class="metrics-row">{cards_html}</div></div>'

# ============ 生成HTML ============

# 图表配置 (隐藏工具栏)
config = {
    'displayModeBar': False,
    'scrollZoom': False,
    'displaylogo': False,
    'responsive': True
}

# 生成各个图表的HTML (按用户指定顺序)
charts_html = []

# 1. 质量指标概览 (5个小卡片) - 直接生成HTML
metrics_html = create_metrics_cards_html()

# 2. 处理人员缺陷统计 (复合图表: 堆叠柱状图 + 折线图)
# 按处理人员和缺陷状态分组统计
status_list = ['Closed', 'Fixed', 'New', 'Pending', 'ReOpen']
handler_status_counts = df.groupby(['处理人员', '缺陷状态']).size().unstack(fill_value=0)

# 确保所有状态列都存在
for status in status_list:
    if status not in handler_status_counts.columns:
        handler_status_counts[status] = 0

# 按状态顺序重新排列列
handler_status_counts = handler_status_counts[status_list]

# 按总数排序处理人员
handler_totals = handler_status_counts.sum(axis=1)
handler_status_counts = handler_status_counts.loc[handler_totals.sort_values(ascending=False).index]

# 计算每个处理人员的总数用于显示
totals = handler_status_counts.sum(axis=1).tolist()
handlers = handler_status_counts.index.tolist()

# 计算每个处理人员的平均修复时长
df['缺陷修复周期(天)'] = pd.to_numeric(df['缺陷修复周期(天)'].replace('/', np.nan), errors='coerce')
avg_fix_time = df.groupby('处理人员')['缺陷修复周期(天)'].mean()
avg_fix_time = avg_fix_time.reindex(handlers).fillna(0)

fig = go.Figure()

# 添加堆叠柱状图（缺陷状态）- 使用柔和清新配色
for status in status_list:
    fig.add_trace(go.Bar(
        x=handlers,
        y=handler_status_counts[status],
        name=status,
        marker_color=COLORS['status_soft'].get(status, '#A8D8EA'),
        marker_line_color='white',
        marker_line_width=1,
        opacity=0.85,
        hovertemplate=f'<b>{status}</b><br>数量: %{{y}}个<extra></extra>'
    ))

# 添加总数标注
for i, (handler, cnt) in enumerate(zip(handlers, totals)):
    fig.add_annotation(
        x=handler,
        y=cnt,
        text=str(cnt),
        showarrow=False,
        font={'size': 12, 'color': '#2c3e50', 'family': 'Microsoft YaHei'},
        yshift=5
    )

# 添加平均修复时长折线图（次轴）- 曲线样式，淡红色配色
fig.add_trace(go.Scatter(
    x=handlers,
    y=avg_fix_time.values,
    name='平均修复时长(天)',
    mode='lines+markers+text',
    line=dict(color='#F5C4D0', width=2.5, shape='spline'),
    marker=dict(size=10, color='#F5C4D0', line=dict(color='white', width=1.5)),
    text=[f'{v:.2f}' if v > 0 else '' for v in avg_fix_time.values],
    textposition='top center',
    textfont={'size': 10, 'color': '#F5C4D0', 'family': 'Microsoft YaHei'},
    yaxis='y2',
    customdata=avg_fix_time.values,
    hovertemplate='<b>平均修复时长</b><br>%{customdata:.2f}天<extra></extra>'
))

fig.update_layout(
    title=dict(text='处理人员缺陷统计', x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
    paper_bgcolor='white',
    plot_bgcolor='#fafafa',
    margin=dict(t=50, l=20, r=60, b=80),
    height=400,
    yaxis=dict(
        title='数量',
        gridcolor='#e8e8e8',
        griddash='dot'
    ),
    yaxis2=dict(
        title=dict(text='平均修复时长(天)', font={'color': '#2c3e50'}),
        overlaying='y',
        side='right',
        gridcolor='#e8e8e8',
        griddash='dot'
    ),
    barmode='stack',
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.25,
        xanchor='center',
        x=0.5,
        font={'size': 11, 'family': 'Microsoft YaHei'},
        itemwidth=30,
        itemsizing='constant'
    )
)
fig.update_xaxes(tickangle=15, tickfont={'size': 11, 'family': 'Microsoft YaHei'})
# 第一个图表嵌入Plotly库
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=True, config=config))

# 3. 缺陷状态分布 (饼图)
status_counts = df['缺陷状态'].value_counts()
fig = create_pie_chart(
    df['缺陷状态'], '缺陷状态分布', hole=0.4,
    colors=[COLORS['status'].get(s, '#A8D8EA') for s in status_counts.index]
)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 4. 关联任务项统计 (横向柱状图)
fig = create_bar_chart(df['关联任务项'], '关联任务项统计', orientation='h', colors=COLORS['fresh'], show_legend=True, legend_y=-0.3)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 5. 缺陷趋势分析 (面积折线图 - 宽卡片)
# 从副标题提取时间范围
import re
date_range_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*~\s*(\d{4}-\d{2}-\d{2})', SUBTITLE)
if date_range_match:
    start_date = pd.to_datetime(date_range_match.group(1))
    end_date = pd.to_datetime(date_range_match.group(2))
else:
    start_date = pd.to_datetime('2026-05-18')
    end_date = pd.to_datetime('2026-05-22')

# 生成完整日期序列（格式：MM-DD）
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
all_dates = [d.strftime('%m-%d') for d in date_range]

# 获取登记时间列（datetime类型）
register_time_col = df.columns[11]  # 登记时间.1
close_time_col = df.columns[13]  # 关闭时间

# 提取日期（格式：MM-DD）
df['登记日期'] = pd.to_datetime(df[register_time_col]).dt.strftime('%m-%d')
df['关闭日期'] = pd.to_datetime(df[close_time_col]).dt.strftime('%m-%d')

# 统计每日新增缺陷（New状态，按登记日期）
new_counts = df[df['缺陷状态'] == 'New'].groupby('登记日期').size()

# 统计每日关闭缺陷（Closed状态，按关闭日期）
closed_counts = df[df['缺陷状态'] == 'Closed'].groupby('关闭日期').size()

# 统计每日遗留缺陷（New、ReOpen、Pending、Fixed状态，按登记日期）
# 遗留缺陷指尚未关闭的缺陷，包含四种状态
legacy_df = df[df['缺陷状态'].isin(['New', 'ReOpen', 'Pending', 'Fixed'])]
legacy_counts = legacy_df.groupby('登记日期').size()

# 构建趋势数据（按日期序列填充，无数据则为0）
new_data = [new_counts.get(d, 0) for d in all_dates]
closed_data = [closed_counts.get(d, 0) for d in all_dates]
legacy_data = [legacy_counts.get(d, 0) for d in all_dates]

# 趋势图配色
trend_colors = {
    '新增缺陷': '#A8D8EA',   # 天蓝
    '关闭缺陷': '#B8E0D2',   # 薄荷绿
    '遗留缺陷': '#AA96DA'    # 薰衣草紫
}

fig = go.Figure()

# 趋势图专用配色（莫兰迪清新风格，减少红绿蓝）
trend_unique_colors = {
    '新增缺陷': '#E8C4A0',   # 奶茶杏 - 温暖柔和
    '遗留缺陷': '#C9B1FF',   # 淡紫丁香 - 优雅清新
    '关闭缺陷': '#F5D5C8'    # 裸粉色 - 柔和温暖
}

# 新增缺陷
fig.add_trace(go.Scatter(
    x=all_dates, y=new_data,
    name='新增缺陷',
    mode='lines+markers',
    line=dict(color='#A0E7E5', width=2.5, shape='spline'),
    marker=dict(size=12, color='#A0E7E5'),
    fill='tozeroy',
    fillcolor='rgba(160, 231, 229, 0.3)',
    hovertemplate='<b>新增缺陷</b><br>%{x}: %{y}个<extra></extra>'
))

# 遗留缺陷
fig.add_trace(go.Scatter(
    x=all_dates, y=legacy_data,
    name='遗留缺陷',
    mode='lines+markers',
    line=dict(color='#FFD69B', width=2.5, shape='spline'),
    marker=dict(size=12, color='#FFD69B'),
    fill='tozeroy',
    fillcolor='rgba(255, 214, 155, 0.3)',
    hovertemplate='<b>遗留缺陷</b><br>%{x}: %{y}个<extra></extra>'
))

# 关闭缺陷
fig.add_trace(go.Scatter(
    x=all_dates, y=closed_data,
    name='关闭缺陷',
    mode='lines+markers',
    line=dict(color='#F5C4D0', width=2.5, shape='spline'),
    marker=dict(size=12, color='#F5C4D0'),
    fill='tozeroy',
    fillcolor='rgba(245, 196, 208, 0.3)',
    hovertemplate='<b>关闭缺陷</b><br>%{x}: %{y}个<extra></extra>'
))

fig.update_layout(
    title=dict(text='缺陷趋势分析', x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
    paper_bgcolor='white',
    plot_bgcolor='#fafafa',
    margin=dict(t=50, l=20, r=20, b=60),
    height=350,
    xaxis_title='日期',
    yaxis_title='缺陷数量',
    showlegend=True,
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.25,
        xanchor='center',
        x=0.5,
        font={'size': 11, 'family': 'Microsoft YaHei'},
        itemwidth=30,
        itemsizing='constant'
    ),
    hovermode='x unified'
)
fig.update_xaxes(tickfont={'size': 11, 'family': 'Microsoft YaHei'})
fig.update_yaxes(gridcolor='#e8e8e8', griddash='dot')
trend_chart_html = fig.to_html(full_html=False, include_plotlyjs=False, config=config)  # 单独存储，用于宽卡片

# 5. 缺陷修复周期分布 (直方图)
fix_period = df['缺陷修复周期(天)'].replace('/', np.nan)
fix_period = pd.to_numeric(fix_period, errors='coerce').dropna()
fig = create_histogram(fix_period, '缺陷修复周期分布')
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 6. 缺陷返工情况 (饼图)
rework_counts = df['返工次数'].value_counts()
rework_labels = [f'返工{i}次' if i > 0 else '无返工' for i in rework_counts.index]
fig = go.Figure(go.Pie(
    labels=rework_labels, values=rework_counts.values,
    hole=0.45, marker_colors=['#82E0AA', '#F7DC6F', '#F0B27A'][:len(rework_counts)],
    textinfo='label+percent', textposition='outside',
    textfont={'size': 13, 'color': '#34495e', 'family': 'Microsoft YaHei'},
    hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
))
fig.update_layout(
    title=dict(text='缺陷返工情况', x=0.5, font={'size': 16, 'color': '#2c3e50', 'family': 'Microsoft YaHei'}),
    paper_bgcolor='white',
    margin=dict(t=50, l=20, r=20, b=20), height=300,
    showlegend=True, legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5)
)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 7. 缺陷发现阶段分布 (横向柱状图)
df['发现阶段'] = df['发现阶段'].str.strip()  # 清除前导空格
stage_order = ['2.1-系统测试【基本流】', '2.2-系统测试【备选流】', '4.1-回归测试【基本流】', '4.2-回归测试【备选流】']
stage_colors = [COLORS['stage_find'].get(s, '#C4E1C1') for s in stage_order]
fig = create_bar_chart(df['发现阶段'], '缺陷发现阶段分布', orientation='h', colors=stage_colors, show_legend=True, order=stage_order)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 8. 缺陷类型分布 (环形图)
fig = create_pie_chart(df['缺陷类型'], '缺陷类型分布', hole=0.55, colors=COLORS['pastel'], legend_y=-0.5)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 9. 缺陷引入原因分析 (横向柱状图)
fig = create_bar_chart(df['引入原因'].dropna(), '缺陷引入原因分析', orientation='h', colors=COLORS['pastel'])
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 10. 缺陷优先级分布 (柱状图)
priority_order = ['优先', '高', '中', '低']
fig = create_bar_chart(
    df['优先级'], '缺陷优先级分布', orientation='v',
    colors=[COLORS['priority'].get(p, '#A8D8EA') for p in priority_order],
    show_legend=True,
    order=priority_order,
    legend_y=-0.2
)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 11. 缺陷严重程度分布 (横向柱状图)
severity_order = ['严重', '一般', '轻微', '建议']
fig = create_bar_chart(
    df['严重程度'], '缺陷严重程度分布', orientation='h',
    colors=[COLORS['severity'].get(s, '#A8D8EA') for s in severity_order],
    show_legend=True,
    order=severity_order,
    legend_y=-0.2
)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# 12. 缺陷引入阶段分布 (横向柱状图)
fig = create_bar_chart(df['引入阶段'].dropna(), '缺陷引入阶段分布', orientation='h', colors=COLORS['fresh'], show_legend=True, legend_y=-0.2)
charts_html.append(fig.to_html(full_html=False, include_plotlyjs=False, config=config))

# ============ 组装完整HTML ============

html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}

        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .card-full {{
            grid-column: 1 / -1;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px 30px;
            transition: all 0.3s ease;
        }}

        .card-wide {{
            grid-column: span 2;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .metrics-container {{
            width: 100%;
        }}

        .metrics-title {{
            text-align: center;
            font-size: 16px;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: 'Microsoft YaHei';
        }}

        .metrics-row {{
            display: flex;
            gap: 20px;
            justify-content: stretch;
            width: 100%;
        }}

        .metric-card {{
            flex: 1;
            height: 120px;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            justify-content: center;
            transition: all 0.3s ease;
            cursor: default;
            padding: 15px 18px;
            position: relative;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metric-name {{
            font-size: 15px;
            color: #5a6c7d;
            font-family: 'Microsoft YaHei';
            font-weight: bold;
        }}

        .metric-icon {{
            width: 22px;
            height: 22px;
            opacity: 0.7;
            position: relative;
        }}

        .icon-task {{
            width: 20px;
            height: 22px;
            border: 2px solid #fff;
            border-radius: 4px;
            position: relative;
        }}
        .icon-task::before {{
            content: '';
            position: absolute;
            top: 5px;
            left: 4px;
            width: 10px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}
        .icon-task::after {{
            content: '';
            position: absolute;
            top: 10px;
            left: 4px;
            width: 7px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}

        .icon-bug {{
            width: 20px;
            height: 20px;
            position: relative;
        }}
        .icon-bug::before {{
            content: '';
            position: absolute;
            top: 3px;
            left: 5px;
            width: 10px;
            height: 14px;
            border: 2px solid #fff;
            border-radius: 50% 50% 45% 45%;
        }}
        .icon-bug::after {{
            content: '';
            position: absolute;
            top: 7px;
            left: 1px;
            width: 4px;
            height: 2px;
            background: #fff;
            box-shadow: 12px 0 0 #fff, 6px 6px 0 #fff, 6px 10px 0 #fff;
        }}

        .icon-check {{
            width: 22px;
            height: 22px;
            border: 2px solid #fff;
            border-radius: 50%;
            position: relative;
        }}
        .icon-check::before {{
            content: '';
            position: absolute;
            top: 4px;
            left: 7px;
            width: 5px;
            height: 9px;
            border: 2.5px solid #fff;
            border-top: none;
            border-left: none;
            transform: rotate(45deg);
            border-radius: 0 0 2px 0;
        }}

        .icon-chart {{
            width: 22px;
            height: 22px;
            position: relative;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
        }}
        .icon-chart::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 5px;
            height: 14px;
            background: #fff;
            border-radius: 2px 2px 0 0;
        }}
        .icon-chart::after {{
            content: '';
            position: absolute;
            bottom: 0;
            right: 0;
            width: 5px;
            height: 8px;
            background: #fff;
            border-radius: 2px 2px 0 0;
        }}

        .icon-refresh {{
            width: 20px;
            height: 20px;
            position: relative;
        }}
        .icon-refresh::before {{
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 16px;
            height: 16px;
            border: 2px solid #fff;
            border-radius: 50%;
            border-top-color: transparent;
            border-left-color: transparent;
            transform: rotate(-45deg);
        }}
        .icon-refresh::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 3px;
            width: 6px;
            height: 6px;
            border-top: 2px solid #fff;
            border-right: 2px solid #fff;
            transform: rotate(45deg);
        }}

        .icon-clock {{
            width: 20px;
            height: 20px;
            border: 2px solid #fff;
            border-radius: 50%;
            position: relative;
        }}
        .icon-clock::before {{
            content: '';
            position: absolute;
            top: 3px;
            left: 7px;
            width: 2px;
            height: 6px;
            background: #fff;
            border-radius: 1px;
        }}
        .icon-clock::after {{
            content: '';
            position: absolute;
            top: 7px;
            left: 7px;
            width: 5px;
            height: 2px;
            background: #fff;
            border-radius: 1px;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            font-family: 'Microsoft YaHei';
            margin-top: 12px;
        }}

        .metric-subtitle {{
            font-size: 11px;
            color: #aaa;
            font-family: 'Microsoft YaHei';
            position: absolute;
            bottom: 8px;
            right: 15px;
            line-height: 1.4;
            text-align: right;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}

        .plotly-graph-div {{
            width: 100% !important;
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}

            .header h1 {{
                font-size: 28px;
            }}
        }}

        /* 表格hover效果 */
        .plotly-table tbody tr:hover td {{
            background-color: #e8f8f5 !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{TITLE}</h1>
            <p>{SUBTITLE} | 共 {total} 条缺陷数据</p>
        </div>

        <div class="grid">
            <div class="card-full">{metrics_html}</div>
            <div class="card-wide">{charts_html[0]}</div>
            <div class="card">{charts_html[1]}</div>
            <div class="card">{charts_html[2]}</div>
            <div class="card-wide">{trend_chart_html}</div>
            {''.join([f'<div class="card">{html}</div>' for html in charts_html[3:]])}
        </div>
    </div>
</body>
</html>
'''

# 保存文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'报告已生成: {OUTPUT_FILE}')
print(f'共 {total} 条缺陷数据')