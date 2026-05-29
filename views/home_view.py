"""
主页视图模块
生成主页视图HTML
"""

import pandas as pd
from config import PANEL_HEADER_COLOR


def create_home_view_html(panels_data, sheet2_data=None):
    """
    创建主页视图HTML

    参数:
        panels_data: 公共面板数据列表，每项包含 title 和 content_parts
        sheet2_data: Sheet2表格数据DataFrame（测试进度和缺陷统计）

    返回:
        主页视图HTML字符串
    """
    # 生成公共面板卡片HTML
    panels_html = []
    for idx, panel in enumerate(panels_data):
        # 第一个章节：本周测试概况（精细化处理）
        # 第二个章节：测试进度和缺陷统计（表格展示）
        # 其他章节：普通渲染
        is_first = (idx == 0)
        is_second = (idx == 1 and sheet2_data is not None)
        panel_card = _create_panel_card(panel, is_first=is_first, is_second=is_second, sheet2_data=sheet2_data)
        panels_html.append(panel_card)

    panels_html_str = '\n'.join(panels_html)

    html = f'''
    <!-- 公共面板 -->
    <div class="panels-section">
        <div class="panels-grid">
            {panels_html_str}
        </div>
    </div>
    '''
    return html


def _create_panel_card(panel, is_first=False, is_second=False, sheet2_data=None):
    """创建单个面板卡片HTML"""
    title = panel['title']
    content_parts = panel['content_parts']

    if is_first:
        # 第一个章节：精细化处理
        lines_html, stats_html = _render_first_panel_content(content_parts)

        # 统计缺陷预警内容的行数
        warning_count = 0  # 暂时为0，后续可以从数据中获取

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-row">
                <div class="panel-card panel-half">
                    <div class="panel-card-title">测试进度概览</div>
                    <div class="panel-content">
                        {lines_html}
                    </div>
                    {stats_html}
                </div>
                <div class="panel-card panel-half">
                    <div class="panel-card-title-wrap">
                        <span class="panel-card-title">缺陷预警</span>
                        <span class="count-badge">{warning_count}</span>
                    </div>
                    <div class="panel-content placeholder-content">
                        <p class="empty-content">暂无内容</p>
                    </div>
                </div>
            </div>
        </div>
        '''
    elif is_second:
        # 第二个章节：测试进度和缺陷统计（表格展示）
        table_html, bar_chart_html, chart_title = _render_table_content(sheet2_data)

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-card panel-full-card">
                {table_html}
            </div>
            <div class="panel-card bar-chart-card">
                <div class="bar-chart-title">{chart_title}</div>
                <div class="bar-chart-body">
                    {bar_chart_html}
                </div>
            </div>
        </div>
        '''
    else:
        # 其他章节：普通渲染
        lines_html = _render_content_lines(content_parts)
        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-card">
                <div class="panel-content">
                    {lines_html}
                </div>
            </div>
        </div>
        '''
    return html


def _render_table_content(df):
    """渲染Sheet2表格内容"""
    if df is None or df.empty:
        return '<p class="empty-content">暂无数据</p>'

    # 过滤掉"合计"行（如果有）
    df_display = df[df.iloc[:, 0] != '合计'].copy() if len(df) > 0 else df

    # 获取所有列名，排除"关联缺陷"列（通常是最后一列）
    all_cols = df_display.columns.tolist()
    # 查找并排除包含"关联缺陷"的列
    available_cols = [col for col in all_cols if '关联缺陷' not in str(col)]

    # 构建表头
    header_html = '<thead><tr>'
    for col in available_cols:
        # 去掉表头中的（个）
        col_display = str(col).replace('（个）', '').replace('(个)', '')
        header_html += f'<th>{col_display}</th>'
    header_html += '</tr></thead>'

    # 构建表格内容
    body_html = '<tbody>'
    for _, row in df_display.iterrows():
        body_html += '<tr>'
        for col in available_cols:
            value = row[col]
            # 处理进度列，添加进度条样式
            if '进度' in str(col):
                if pd.isna(value) or value == '/':
                    body_html += '<td><span style="color:#9ca3af;">/</span></td>'
                else:
                    try:
                        # 处理进度值，确保显示为百分比格式
                        if '%' in str(value):
                            progress_val = float(str(value).replace('%', ''))
                            display_val = str(value)
                        else:
                            progress_val = float(value) * 100
                            display_val = f'{progress_val:.0f}%'
                        # 根据进度值设置颜色
                        progress_color = _get_progress_color(progress_val)
                        body_html += f'<td><div class="progress-mini"><div class="progress-track"><div class="progress-fill" style="width:{progress_val}%;background:{progress_color}"></div></div><span class="progress-text">{display_val}</span></div></td>'
                    except:
                        body_html += f'<td>{value}</td>'
            elif '任务项名称' in str(col):
                # 任务项名称列：居中、最大宽度300px、tooltip
                if pd.isna(value):
                    body_html += '<td style="text-align:center;">-</td>'
                else:
                    body_html += f'<td style="text-align:center;"><span class="task-name-cell" title="{value}">{value}</span></td>'
            elif '个数' in str(col) or '总数' in str(col) or '个' in str(col):
                # 数值列居中显示
                body_html += f'<td style="text-align:center;">{value if not pd.isna(value) else 0}</td>'
            else:
                body_html += f'<td>{value if not pd.isna(value) else ""}</td>'
        body_html += '</tr>'

    # 添加合计行（如果有）
    if len(df) > 0:
        summary_row = df[df.iloc[:, 0] == '合计']
        if not summary_row.empty:
            body_html += '<tr class="summary-row">'
            for col in available_cols:
                value = summary_row[col].values[0]
                if '进度' in str(col):
                    try:
                        # 处理进度值，确保显示为百分比格式
                        if '%' in str(value):
                            progress_val = float(str(value).replace('%', ''))
                            display_val = str(value)
                        else:
                            progress_val = float(value) * 100
                            display_val = f'{progress_val:.0f}%'
                        # 根据进度值设置颜色
                        progress_color = _get_progress_color(progress_val)
                        body_html += f'<td><div class="progress-mini"><div class="progress-track"><div class="progress-fill" style="width:{progress_val}%;background:{progress_color}"></div></div><span class="progress-text">{display_val}</span></div></td>'
                    except:
                        body_html += f'<td>{value}</td>'
                elif '任务项名称' in str(col):
                    if pd.isna(value):
                        body_html += '<td style="text-align:center;font-weight:600;">-</td>'
                    else:
                        body_html += f'<td style="text-align:center;font-weight:600;"><span class="task-name-cell" title="{value}">{value}</span></td>'
                elif '个数' in str(col) or '总数' in str(col) or '个' in str(col):
                    body_html += f'<td style="text-align:center;font-weight:600;">{value if not pd.isna(value) else 0}</td>'
                else:
                    body_html += f'<td style="font-weight:600;">{value if not pd.isna(value) else ""}</td>'
            body_html += '</tr>'

    body_html += '</tbody>'

    # 生成条形图卡片
    bar_chart_html, chart_title = _render_progress_bar_chart(df, df_display)

    return f'''
    <div class="table-wrap">
        <table class="stats-table">
            {header_html}
            {body_html}
        </table>
    </div>
    ''', bar_chart_html, chart_title


def _get_progress_color(progress_val):
    """根据进度值返回颜色"""
    if progress_val < 30:
        return '#ef4444'  # 红色
    else:
        return '#1c91fd'  # 蓝色


def _render_progress_bar_chart(df_full, df_display):
    """渲染进度条形图，根据合计测试进度决定显示测试进度或回归进度"""
    if df_display is None or df_display.empty:
        return '', '各任务项测试进度对比'

    # 检查合计行的测试进度是否为100%
    use_regression = False
    if len(df_full) > 0:
        summary_row = df_full[df_full.iloc[:, 0] == '合计']
        if not summary_row.empty:
            for col in df_full.columns:
                if '测试进度' in str(col):
                    test_progress = summary_row[col].values[0]
                    try:
                        if '%' in str(test_progress):
                            progress_num = float(str(test_progress).replace('%', ''))
                        else:
                            progress_num = float(test_progress) * 100
                        if progress_num >= 100:
                            use_regression = True
                    except:
                        pass

    # 确定使用哪个进度列
    task_col = None
    progress_col = None
    subtask_col = None

    for col in df_display.columns:
        if '任务项名称' in str(col):
            task_col = col
        elif '回归进度' in str(col) and use_regression:
            progress_col = col
        elif '测试进度' in str(col) and not progress_col:
            progress_col = col
        elif '子任务项' in str(col):
            subtask_col = col

    if not task_col or not progress_col:
        return '', '各任务项测试进度对比'

    chart_title = '各任务项回归进度对比' if use_regression else '各任务项测试进度对比'

    bars_html = ''
    for _, row in df_display.iterrows():
        task_name = row[task_col] if not pd.isna(row[task_col]) else ''
        progress_val = row[progress_col]

        # 处理进度值
        if pd.isna(progress_val) or progress_val == '/':
            continue

        try:
            if '%' in str(progress_val):
                progress_num = float(str(progress_val).replace('%', ''))
            else:
                progress_num = float(progress_val) * 100
        except:
            continue

        # 获取子任务项数量
        subtask_count = ''
        if subtask_col and not pd.isna(row[subtask_col]):
            subtask_count = f'{int(row[subtask_col])} 个子任务'

        bars_html += f'''
        <div class="bar-row">
            <div class="bar-info"><span class="bar-label">{task_name}</span><span class="bar-value" style="color:{_get_progress_color(progress_num)}">{progress_num:.0f}%</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:{progress_num}%;background:{_get_progress_color(progress_num)}">{subtask_count}</div></div>
        </div>
        '''

    return bars_html, chart_title


def _render_first_panel_content(content_parts):
    """
    渲染第一个面板内容，将[xxx]转换为标签样式，提取进度指标和缺陷状态统计
    返回: (内容HTML, 统计卡片HTML)
    """
    if not content_parts:
        return '<p class="empty-content">暂无内容</p>', ''

    import re

    # 合并所有文本
    full_text = ''
    for part in content_parts:
        full_text += part['text']

    try:
        # 提取测试总进度和回归总进度
        test_progress_match = re.search(r'测试总进度[为：:]?\s*(\d+(?:\.\d+)?%)', full_text)
        regression_progress_match = re.search(r'回归总进度[为：:]?\s*(\d+(?:\.\d+)?%)', full_text)

        test_progress = test_progress_match.group(1) if test_progress_match else '0%'
        regression_progress = regression_progress_match.group(1) if regression_progress_match else '0%'

        # 从原文中移除进度相关文字
        clean_text = re.sub(r'[、，]?\s*测试总进度[为：:]?\s*\d+(?:\.\d+)?%', '', full_text)
        clean_text = re.sub(r'[、，]?\s*回归总进度[为：:]?\s*\d+(?:\.\d+)?%', '', clean_text)

        # 提取本周新增缺陷总数
        defect_total_match = re.search(r'本周新增缺陷总数(\d+)个', clean_text)
        defect_total = defect_total_match.group(1) if defect_total_match else None

        # 提取缺陷状态统计（只提取存在的标签）
        status_labels = ['已关闭', '待修复', '待验证', '延期', '重新打开', '被拒绝']
        status_colors = {
            '已关闭': '#22c55e',
            '待修复': '#ef4444',
            '待验证': '#f59e0b',
            '延期': '#8b5cf6',
            '重新打开': '#ec4899',
            '被拒绝': '#6b7280'
        }
        defect_status = {}
        for label in status_labels:
            match = re.search(rf'{label}(\d+)个', clean_text)
            if match:
                defect_status[label] = match.group(1)

        # 从原文中移除缺陷统计相关文字
        clean_text = re.sub(r'本周新增缺陷总数\d+个', '', clean_text)
        for label in status_labels:
            clean_text = re.sub(rf'{label}\d+个', '', clean_text)

        # 清理多余标点符号
        clean_text = re.sub(r'[，。]+$', '', clean_text.strip())
        clean_text = re.sub(r'^[，。]+', '', clean_text)

        # 将[xxx]格式替换为标签，并清理顿号、逗号、句号
        def replace_badge(match):
            return f'<span class="badge">{match.group(1)}</span>'

        clean_text = re.sub(r'\[([^\]]+)\][、，。]?', replace_badge, clean_text)

        # 按换行分割
        lines = clean_text.split('\n')
        lines_html = []
        for line in lines:
            line = line.strip()
            if line:
                lines_html.append(f'<p>{line}</p>')

        content_html = '\n'.join(lines_html) if lines_html else ''

        # 生成进度统计卡片
        def get_progress_color(value):
            try:
                num = float(value.replace('%', ''))
                return '#6b7280' if num == 0 else '#1c91fd'
            except:
                return '#6b7280'

        stats_html = f'''
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-label">测试总进度</div>
                <div class="stat-value" style="color: {get_progress_color(test_progress)}">{test_progress}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">回归总进度</div>
                <div class="stat-value" style="color: {get_progress_color(regression_progress)}">{regression_progress}</div>
            </div>
        </div>
        '''

        # 生成缺陷统计区域
        defect_html = ''
        if defect_total:
            defect_items = ''
            for label, count in defect_status.items():
                color = status_colors.get(label, '#6b7280')
                defect_items += f'<div class="defect-item"><div class="dot" style="background:{color};"></div><span class="label">{label}</span><span class="count">{count}</span></div>\n'

            defect_html = f'''
        <div class="defect-summary">
            <p class="defect-total">本周新增缺陷总数：<span class="defect-count">{defect_total}</span>个</p>
            <div class="defect-list">
                {defect_items}            </div>
        </div>'''

        return content_html, stats_html + defect_html

    except Exception as e:
        # 异常时返回原始内容
        lines = full_text.split('\n')
        lines_html = [f'<p>{line.strip()}</p>' for line in lines if line.strip()]
        return '\n'.join(lines_html), ''


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
    return '''
    /* 主页视图容器 */
    .view-container {
        display: none;
    }
    .view-container.active {
        display: block;
    }

    /* 公共面板区域 */
    .panels-section {
        margin-top: 0;
    }

    /* 面板网格 - 单列布局 */
    .panels-grid {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    /* 面板包裹 - 标题在卡片上方 */
    .panel-wrapper {
    }

    /* 章节标题 - 在卡片外部上方 */
    .panel-section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-size: 18px;
        font-weight: 700;
        color: #1c91fd;
    }
    .panel-section-title::before {
        content: "";
        display: block;
        width: 4px;
        height: 24px;
        background: #1c91fd;
        border-radius: 2px;
    }

    /* 卡片标题行 */
    .panel-card-title-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    /* 数量标签 */
    .count-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        height: 28px;
        padding: 0 8px;
        background: #ffdcdb9c;
        color: #e74c3c;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 700;
    }

    /* 两列布局 */
    .panel-row {
        display: flex;
        gap: 20px;
    }
    .panel-half {
        flex: 1;
    }
    .panel-placeholder {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .placeholder-content {
        text-align: center;
    }

    /* 面板卡片 */
    .panel-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        padding: 20px;
    }

    /* 全宽卡片（表格用） */
    .panel-full-card {
        padding: 0;
    }

    /* 表格容器 */
    .table-wrap {
        overflow-x: auto;
        max-height: 500px;
        overflow-y: auto;
    }

    /* 统计表格 */
    .stats-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 13px;
        min-width: 1000px;
    }
    .stats-table th {
        background: #1c91fd;
        color: #fff;
        text-align: center;
        padding: 12px 16px;
        font-weight: 600;
        white-space: nowrap;
        position: sticky;
        top: 0;
    }
    .stats-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #e5e7eb;
        white-space: nowrap;
    }
    .stats-table tr:hover td {
        background: #f8fafc;
        transition: background .2s;
    }
    .stats-table .summary-row {
        background: #e8f0f8 !important;
        font-weight: 600;
    }

    /* 进度条 */
    .progress-mini {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .progress-track {
        width: 64px;
        height: 6px;
        background: #e5e7eb;
        border-radius: 6px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: #1c91fd;
        border-radius: 6px;
    }
    .progress-text {
        font-size: 11px;
        font-weight: 600;
    }

    /* 条形图卡片 */
    .bar-chart-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        margin-top: 20px;
        padding: 20px;
    }
    .bar-chart-title {
        font-size: 15px;
        font-weight: 600;
        color: #1c91fd;
        margin-bottom: 16px;
    }
    .bar-chart-body .bar-row {
        margin-bottom: 14px;
    }
    .bar-row .bar-info {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .bar-label {
        font-weight: 600;
    }
    .bar-value {
        color: #1c91fd;
        font-weight: 700;
    }
    .bar-chart-body .bar-track {
        height: 28px;
        background: #f0f4f8;
        border-radius: 14px;
        overflow: hidden;
    }
    .bar-chart-body .bar-fill {
        height: 100%;
        background: #1c91fd;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 10px;
        color: #fff;
        font-size: 12px;
        font-weight: 600;
        transition: width .6s ease;
    }

    /* 任务项名称列 */
    .task-name-cell {
        display: inline-block;
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: middle;
        cursor: default;
        position: relative;
    }
    .task-name-cell.overflow:hover::after {
        content: attr(title);
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        bottom: 100%;
        background: #1c91fd;
        color: #fff;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 400;
        white-space: normal;
        max-width: 300px;
        z-index: 100;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }

    /* 第一个卡片内的标题 */
    .panel-card-title {
        font-size: 15px;
        font-weight: 600;
        color: #1c91fd;
        margin-bottom: 12px;
    }

    /* 标签样式 */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        font-size: 12px;
        background: #f0f4f8;
        color: #1c91fd;
        border-radius: 12px;
        margin: 0 2px;
    }
    .panel-badges {
        margin-bottom: 12px;
    }

    /* 进度统计卡片 */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 12px;
    }
    .stat-box {
        background: #f0f4f8;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .stat-label {
        font-size: 12px;
        color: #6b7280;
    }
    .stat-value {
        font-size: 26px;
        font-weight: 700;
        margin-top: 4px;
    }

    /* 缺陷统计区域 */
    .defect-summary {
        border-top: 1px solid #e5e7eb;
        margin-top: 14px;
        padding-top: 14px;
    }
    .defect-total {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .defect-count {
        color: #1c91fd;
        font-size: 20px;
        font-weight: 700;
    }
    .defect-list {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 8px;
        margin-top: 12px;
    }
    .defect-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
    }
    .defect-item .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .defect-item .label {
        color: #6b7280;
    }
    .defect-item .count {
        font-weight: 600;
        margin-left: auto;
    }

    /* 面板内容 */
    .panel-content p {
        color: #333;
        line-height: 1.8;
        margin-bottom: 12px;
        font-size: 14px;
    }
    .panel-content p:last-child {
        margin-bottom: 0;
    }
    .panel-content .empty-content {
        color: #9ca3af;
        font-style: italic;
    }
    '''

def get_home_view_js():
    """获取主页视图专用JS"""
    return '''
    // 检测任务项名称是否超出宽度
    document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('.task-name-cell').forEach(function(el) {
            if (el.scrollWidth > el.clientWidth) {
                el.classList.add('overflow');
            }
        });
    });
    '''
