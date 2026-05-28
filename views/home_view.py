"""
主页视图模块
生成主页视图HTML
"""

from config import PANEL_HEADER_COLOR


def create_home_metrics_html(df, total, task_count, subtask_count):
    """创建主页视图专用的质量指标卡片HTML（使用统一渐变背景）"""
    closed = len(df[df['缺陷状态'] == 'Closed'])
    legacy_count = len(df[df['缺陷状态'] != 'Closed'])
    close_rate = closed / total * 100 if total > 0 else 0

    df['发现阶段'] = df['发现阶段'].str.strip()
    basic_flow = len(df[df['发现阶段'].str.contains('基本流', na=False)])
    basic_flow_rate = basic_flow / total * 100 if total > 0 else 0

    rework = len(df[df['返工次数'] > 0])
    rework_rate = rework / total * 100 if total > 0 else 0

    fix_period = df['缺陷修复周期(天)'].dropna()
    avg_fix_time = fix_period.mean()
    max_fix_time = fix_period.max()
    min_fix_time = fix_period.min()
    avg_fix_time_str = f'{avg_fix_time:.2f}天' if avg_fix_time > 0 else '--'
    max_fix_time_str = f'{max_fix_time:.0f}天' if max_fix_time > 0 else '--'
    min_fix_time_str = f'{min_fix_time:.0f}天' if min_fix_time > 0 else '--'

    cards = [
        ('任务项', f'{task_count}个', 'icon-task', f'子任务项{subtask_count}个'),
        ('平均修复时长', avg_fix_time_str, 'icon-clock', f'最大{max_fix_time_str}<br>最小{min_fix_time_str}'),
        ('遗留缺陷', f'{legacy_count}个', 'icon-bug', f'关闭率{close_rate:.1f}%'),
        ('基本流占比', f'{basic_flow_rate:.1f}%', 'icon-chart', f'{basic_flow}/{total}个'),
        ('返工率', f'{rework_rate:.1f}%', 'icon-refresh', f'{rework}/{total}个')
    ]

    cards_html = ''.join([
        f'<div class="metric-card">'
        f'<div class="metric-header">'
        f'<span class="metric-name">{c[0]}</span>'
        f'<div class="metric-icon {c[2]}"></div>'
        f'</div>'
        f'<div class="metric-value">{c[1]}</div>'
        f'<div class="metric-subtitle">{c[3]}</div>'
        f'</div>'
        for c in cards
    ])

    return f'<div class="metrics-container"><div class="metrics-title">质量指标概览</div><div class="metrics-row">{cards_html}</div></div>'


def create_home_view_html(metrics_html, panels_data):
    """
    创建主页视图HTML

    参数:
        metrics_html: 质量指标概览HTML
        panels_data: 公共面板数据列表，每项包含 title 和 content_parts

    返回:
        主页视图HTML字符串
    """
    # 生成公共面板卡片HTML
    panels_html = []
    for panel in panels_data:
        panel_card = _create_panel_card(panel)
        panels_html.append(panel_card)

    panels_html_str = '\n'.join(panels_html)

    html = f'''
    <!-- 质量指标概览 -->
    <div class="card-full home-metrics-card">{metrics_html}</div>

    <!-- 公共面板 -->
    <div class="panels-section">
        <div class="panels-grid">
            {panels_html_str}
        </div>
    </div>
    '''
    return html


def _create_panel_card(panel):
    """创建单个面板卡片HTML"""
    title = panel['title']
    content_parts = panel['content_parts']

    # 将内容按换行符分割成多行
    lines_html = _render_content_lines(content_parts)

    html = f'''
    <div class="panel-card">
        <div class="panel-header" onclick="togglePanel(this)">
            <span class="panel-title">{title}</span>
            <span class="panel-toggle">▼</span>
        </div>
        <div class="panel-content">
            {lines_html}
        </div>
    </div>
    '''
    return html


def _render_content_lines(content_parts):
    """
    渲染内容，按换行符分割成多行，保留富文本样式
    """
    if not content_parts:
        return '<p class="empty-content">暂无内容</p>'

    # 先合并所有文本片段
    full_text = ''
    parts_with_offset = []  # 记录每个片段的起始位置和样式

    for part in content_parts:
        start_offset = len(full_text)
        text = part['text']
        full_text += text
        parts_with_offset.append({
            'start': start_offset,
            'end': start_offset + len(text),
            'bold': part['bold'],
            'color': part['color']
        })

    # 按换行符分割
    lines = full_text.split('\n')

    lines_html = []
    current_offset = 0

    for line in lines:
        line_len = len(line)
        line_end = current_offset + line_len

        # 渲染这一行的每个字符
        line_html = _render_line_with_styles(line, current_offset, parts_with_offset)

        if line_html.strip():
            lines_html.append(f'<p>{line_html}</p>')

        current_offset = line_end + 1  # +1 是换行符

    return '\n'.join(lines_html) if lines_html else '<p class="empty-content">暂无内容</p>'


def _render_line_with_styles(line, line_start, parts_with_offset):
    """渲染单行文本，应用富文本样式"""
    if not line:
        return ''

    result = []
    i = 0
    line_end = line_start + len(line)

    while i < len(line):
        char_offset = line_start + i

        # 找到当前字符所在的片段
        current_part = None
        for part in parts_with_offset:
            if part['start'] <= char_offset < part['end']:
                current_part = part
                break

        if current_part:
            # 收集连续相同样式的字符
            run_start = i
            while i < len(line):
                char_offset = line_start + i
                # 检查是否仍在同一个样式片段内
                in_same_part = (current_part['start'] <= char_offset < current_part['end'])
                if not in_same_part:
                    break
                i += 1

            run_text = line[run_start:i]

            # 应用样式
            style = ''
            if current_part['bold']:
                style += 'font-weight: bold;'
            if current_part['color']:
                # 处理ARGB格式（去掉前两位Alpha）
                color = current_part['color']
                if len(color) == 8:
                    color = color[2:]  # 去掉ARGB的Alpha通道
                style += f'color: #{color};'

            if style:
                result.append(f'<span style="{style}">{run_text}</span>')
            else:
                result.append(run_text)
        else:
            result.append(line[i])
            i += 1

    return ''.join(result)


def get_home_view_css():
    """获取主页视图专用CSS"""
    return f'''
    /* 主页视图容器 */
    .view-container {{
        display: none;
    }}
    .view-container.active {{
        display: block;
    }}

    /* 主页质量指标卡片 */
    .home-metrics-card {{
        margin-bottom: 25px;
    }}

    /* 主页质量指标小卡片背景渐变 - 左上深到右下浅 */
    .home-metrics-card .metric-card {{
        background: linear-gradient(135deg, #B8D4F8 0%, #E8F4FF 100%);
    }}

    /* 公共面板区域 */
    .panels-section {{
        margin-top: 0;
    }}

    /* 面板网格 - 单列布局 */
    .panels-grid {{
        display: flex;
        flex-direction: column;
        gap: 20px;
    }}

    /* 面板卡片 */
    .panel-card {{
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        transition: box-shadow 0.3s ease;
    }}
    .panel-card:hover {{
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }}

    /* 面板标题 */
    .panel-header {{
        background: linear-gradient(135deg, #5FB0FF 0%, #4AA0F0 100%);
        color: white;
        padding: 10px 20px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        user-select: none;
        transition: background 0.3s ease;
    }}
    .panel-header:hover {{
        background: linear-gradient(135deg, #2589E8 0%, #1A7AD6 100%);
    }}
    .panel-title {{
        font-size: 15px;
        font-weight: 600;
    }}
    .panel-toggle {{
        font-size: 14px;
        transition: transform 0.3s ease;
    }}
    .panel-card.collapsed .panel-toggle {{
        transform: rotate(-90deg);
    }}

    /* 面板内容 */
    .panel-content {{
        padding: 20px;
        background: white;
        max-height: 500px;
        overflow: hidden;
        transition: max-height 0.4s ease, padding 0.4s ease;
    }}
    .panel-card.collapsed .panel-content {{
        max-height: 0;
        padding: 0 20px;
    }}
    .panel-content p {{
        color: #5d6d7e;
        line-height: 1.8;
        margin-bottom: 8px;
        padding-left: 12px;
        position: relative;
    }}
    .panel-content p:before {{
        content: "•";
        color: {PANEL_HEADER_COLOR};
        font-weight: bold;
        position: absolute;
        left: 0;
    }}
    .panel-content p:last-child {{
        margin-bottom: 0;
    }}
    .panel-content .empty-content {{
        color: #aaa;
        font-style: italic;
    }}
    .panel-content .empty-content:before {{
        content: "";
    }}

    /* 视图切换按钮 */
    .view-switcher {{
        display: flex;
        gap: 8px;
    }}
    .view-btn {{
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        background: #f0f3f5;
        color: #5d6d7e;
        transition: all 0.3s ease;
    }}
    .view-btn:hover {{
        background: #e8ecef;
    }}
    .view-btn.active {{
        background: #AA96DA;
        color: white;
    }}
    .view-btn.home-btn {{
        padding: 10px 15px;
        font-size: 20px;
    }}
    .view-btn.home-btn.active {{
        background: {PANEL_HEADER_COLOR};
    }}
    '''

def get_home_view_js():
    """获取主页视图专用JS"""
    return '''
    // 面板折叠切换
    function togglePanel(header) {
        const card = header.parentElement;
        card.classList.toggle('collapsed');
    }
    '''
