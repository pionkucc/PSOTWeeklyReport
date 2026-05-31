"""
主页视图模块
生成主页视图HTML
"""

import json
import pandas as pd
from config import PANEL_HEADER_COLOR


def create_home_view_html(panels_data, sheet2_data=None, warning_data=None):
    """
    创建主页视图HTML

    参数:
        panels_data: 公共面板数据列表，每项包含 title 和 content_parts
        sheet2_data: Sheet2表格数据DataFrame（测试进度和缺陷统计）
        warning_data: 缺陷预警数据字典

    返回:
        主页视图HTML字符串
    """
    if warning_data is None:
        warning_data = {'overdue_rework': [], 'overdue': [], 'rework': [], 'total': 0}

    # 生成公共面板卡片HTML
    panels_html = []
    for idx, panel in enumerate(panels_data):
        is_first = (idx == 0)
        is_second = (idx == 1 and sheet2_data is not None)
        panel_card = _create_panel_card(panel, is_first=is_first, is_second=is_second, sheet2_data=sheet2_data, warning_data=warning_data)
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


def _create_panel_card(panel, is_first=False, is_second=False, sheet2_data=None, warning_data=None):
    """创建单个面板卡片HTML"""
    title = panel['title']
    content_parts = panel['content_parts']

    if warning_data is None:
        warning_data = {'overdue_rework': [], 'overdue': [], 'rework': [], 'total': 0}

    if is_first:
        lines_html, stats_html = _render_first_panel_content(content_parts)

        warning_count = warning_data['total']
        warning_list_html = _render_warning_list(warning_data)

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-row">
                <div class="panel-card panel-half" id="left-progress-card">
                    <div class="panel-card-title">测试进度概览</div>
                    <div class="panel-content">
                        {lines_html}
                    </div>
                    {stats_html}
                </div>
                <div class="panel-card panel-half warning-card">
                    <div class="panel-card-title-wrap">
                        <span class="panel-card-title">缺陷预警</span>
                        <span class="count-badge">{warning_count}</span>
                    </div>
                    <div class="warning-list" id="warning-list">
                        {warning_list_html}
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
    elif title == '下周测试计划':
        # 下周测试计划章节：特殊渲染
        plan_html = _render_next_week_plan(content_parts)

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-card">
                <div class="next-plan-list">
                    {plan_html}
                </div>
            </div>
        </div>
        '''
    elif title == '待协调事项':
        # 待协调事项章节：特殊渲染
        coord_html = _render_coord_items(content_parts)

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-card">
                <div class="coord-list">
                    {coord_html}
                </div>
            </div>
        </div>
        '''
    elif 'UI自动化' in title or '自动化建设' in title:
        # PSOT-UI自动化建设章节：特殊渲染
        metrics_html, remaining_html = _render_ui_automation(content_parts)

        html = f'''
        <div class="panel-wrapper">
            <div class="panel-section-title">
                <span class="section-title-text">{title}</span>
            </div>
            <div class="panel-card">
                <div class="three-col">
                    {metrics_html}
                </div>
                <div class="ui-remaining rich-text-content">
                    {remaining_html}
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


def _render_warning_list(warning_data):
    """
    渲染缺陷预警列表

    参数:
        warning_data: 包含 overdue_rework, overdue, rework, total 的字典

    返回:
        HTML字符串
    """
    items = []

    # 1. 超期返工数据（优先展示）
    for item in warning_data.get('overdue_rework', []):
        items.append({
            'type': 'overdue_rework',
            'code': item['code'],
            'handler': item['handler'],
            'summary': item['summary'],
            'tag': f"超期{item['overdue_days']}天|返工{item['rework_count']}次",
            'full_data': item['full_data']
        })

    # 2. 超期数据
    for item in warning_data.get('overdue', []):
        items.append({
            'type': 'overdue',
            'code': item['code'],
            'handler': item['handler'],
            'summary': item['summary'],
            'tag': f"超期{item['overdue_days']}天",
            'full_data': item['full_data']
        })

    # 3. 返工数据
    for item in warning_data.get('rework', []):
        items.append({
            'type': 'rework',
            'code': item['code'],
            'handler': item['handler'],
            'summary': item['summary'],
            'tag': f"返工{item['rework_count']}次",
            'full_data': item['full_data']
        })

    if not items:
        return '<p class="empty-content">暂无预警数据</p>'

    # 生成列表HTML
    rows_html = []
    for idx, item in enumerate(items):
        # 将full_data转为JSON字符串存入data属性，处理NaN和特殊值
        import numpy as np
        cleaned_data = {}
        for k, v in item['full_data'].items():
            if pd.isna(v) or (isinstance(v, float) and np.isnan(v)):
                cleaned_data[k] = '-'
            elif isinstance(v, pd.Timestamp):
                cleaned_data[k] = str(v)
            elif v == 'NaT':
                cleaned_data[k] = '-'
            else:
                cleaned_data[k] = v
        full_data_json = json.dumps(cleaned_data, ensure_ascii=False)
        rows_html.append(f'''
        <div class="warning-row" data-detail='{full_data_json.replace("'", "&#39;")}'>
            <span class="warning-dot"></span>
            <span class="warning-text">{item['code']} <span class="handler-tag">{item['handler']}</span> {item['summary']}</span>
            <span class="warning-tag">{item['tag']}</span>
        </div>
        ''')

    return '\n'.join(rows_html)


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


def _process_rich_text_content(full_text, remove_first_line=False):
    """
    公共方法：处理富文本内容，保留缩进、分割线、表格等样式

    参数:
        full_text: 原始HTML文本
        remove_first_line: 是否移除第一行（用于UI自动化建设等需要提取指标的章节）

    返回:
        处理后的HTML字符串
    """
    from bs4 import BeautifulSoup

    if not full_text or not full_text.strip():
        return ''

    soup = BeautifulSoup(full_text, 'html.parser')

    # 如果需要移除第一行
    if remove_first_line:
        first_p = soup.find('p')
        if first_p:
            first_p.decompose()

    # 清理空段落
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        # 保留只包含&nbsp;的空段落（可能有格式意义）
        if not text and '&nbsp;' not in str(p):
            p.decompose()

    # 确保表格样式正确
    for table in soup.find_all('table'):
        # 保留表格的原始样式
        if table.get('border'):
            table['class'] = 'rich-text-table'

    return str(soup)


def _get_rich_text_css():
    """获取富文本公共CSS样式"""
    return '''
    /* 富文本公共样式 */
    .rich-text-content p {
        font-size: 13px;
        line-height: 1.7;
        color: #333;
        margin-bottom: 8px;
    }
    .rich-text-content p[style*="padding-left"] {
        margin-bottom: 4px;
    }
    .rich-text-content hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 14px 0;
    }
    .rich-text-content ul {
        padding-left: 20px;
        margin: 8px 0;
    }
    .rich-text-content li {
        font-size: 13px;
        line-height: 1.8;
        color: #333;
    }
    .rich-text-content .rich-text-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 12px;
    }
    .rich-text-content .rich-text-table th,
    .rich-text-content .rich-text-table td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: center;
    }
    .rich-text-content .rich-text-table th {
        background: #f0f4f8;
        font-weight: 600;
        color: #333;
    }
    .rich-text-content .rich-text-table td {
        color: #555;
    }
    '''


def _render_ui_automation(content_parts):
    """
    渲染PSOT-UI自动化建设章节

    从第一行提取：完成场景数、自动化执行成功/失败率、下周计划
    生成三个卡片，下方展示剩余内容

    参数:
        content_parts: 内容片段列表

    返回:
        (metrics_html, remaining_html) 元组
    """
    import re
    from bs4 import BeautifulSoup

    # 合并所有文本内容
    full_text = ''
    for part in content_parts:
        text = part.get('text', '')
        if text:
            full_text += text

    if not full_text.strip():
        return '<p class="empty-content">暂无内容</p>', ''

    # 解析HTML
    soup = BeautifulSoup(full_text, 'html.parser')

    # 提取指标数据
    scenario_count = ''
    auto_rate = ''
    next_plan = ''
    is_success = True  # 默认成功

    # 获取纯文本用于提取数据
    plain_text = soup.get_text()

    # 提取完成场景数（格式如 "完成场景数15/70"）
    scenario_match = re.search(r'完成场景数\s*(\d+/\d+)', plain_text)
    if scenario_match:
        scenario_count = scenario_match.group(1)

    # 提取自动化执行成功率（格式如 "自动化执行成功100%" 或 "自动化执行失败100%"）
    success_match = re.search(r'自动化执行成功\s*(\d+(?:\.\d+)?%)', plain_text)
    fail_match = re.search(r'自动化执行失败\s*(\d+(?:\.\d+)?%)', plain_text)

    if success_match:
        auto_rate = success_match.group(1)
        is_success = True
    elif fail_match:
        auto_rate = fail_match.group(1)
        is_success = False

    # 提取下周计划（格式如 "下周计划：继续推进"）
    plan_match = re.search(r'下周计划[：:]\s*([^。\n]+)', plain_text)
    if plan_match:
        next_plan = plan_match.group(1).strip()

    # SVG图标
    svg_scenario = '''<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#50A5F4" stroke-width="2" style="margin:0 auto;display:block;"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>'''

    # 自动化执行SVG根据状态变色：成功#1C91FD，失败#D93025
    rate_svg_color = '#D93025' if (not is_success or auto_rate.replace('%', '') != '100') else '#1C91FD'
    svg_rate = f'''<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="{rate_svg_color}" stroke-width="2" style="margin:0 auto;display:block;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="15"></line><line x1="12" y1="19" x2="12.01" y2="17"></line></svg>'''

    svg_plan = '''<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1C91FD" stroke-width="2" style="margin:0 auto;display:block;"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>'''

    # 确定自动化执行卡片样式
    rate_bg = '#f0f4f8'
    rate_color = '#1C91FD'  # 成功时蓝色
    if not is_success or auto_rate.replace('%', '') != '100':
        rate_bg = '#fef2f2'
        rate_color = '#D93025'  # 失败时红色

    # 构建三个卡片
    metrics_html = f'''
    <div class="metric-card">
        {svg_scenario}
        <div class="metric-label">完成场景数</div>
        <div class="metric-value">{scenario_count or '-'}</div>
    </div>
    <div class="metric-card" style="background:{rate_bg};">
        {svg_rate}
        <div class="metric-label">自动化执行{'成功' if is_success else '失败'}</div>
        <div class="metric-value" style="color:{rate_color};">{auto_rate or '-'}</div>
    </div>
    <div class="metric-card">
        {svg_plan}
        <div class="metric-label">下周计划</div>
        <div class="metric-value" style="font-size:16px;">{next_plan or '-'}</div>
    </div>
    '''

    # 处理剩余内容：移除第一行（包含指标数据的那一行）
    remaining_html = _process_rich_text_content(full_text, remove_first_line=True)

    return metrics_html, remaining_html


def _render_next_week_plan(content_parts):
    """
    渲染下周测试计划章节

    每一行作为一个计划项，每个计划项包含SVG图标和文本内容
    支持富文本格式（同待协调事项）

    参数:
        content_parts: 内容片段列表

    返回:
        HTML字符串
    """
    from bs4 import BeautifulSoup

    # 合并所有文本内容
    full_text = ''
    for part in content_parts:
        text = part.get('text', '')
        if text:
            full_text += text

    if not full_text.strip():
        return '<p class="empty-content">暂无内容</p>'

    # SVG图标
    svg_target = '''<svg viewBox="0 0 25 25" style="width:25px;height:25px;fill:#1C91FD;"><circle cx="12" cy="12" r="12"></circle><circle cx="12" cy="12" r="6" fill="#fff"></circle><circle cx="12" cy="12" r="0" fill="#1C91FD"></circle></svg>'''

    # 解析HTML，保留富文本格式
    soup = BeautifulSoup(full_text, 'html.parser')

    # 按行分割
    items_html = []

    # 遍历所有段落元素
    for element in soup.find_all(['p', 'div']):
        # 获取内容文本（非空）
        text = element.get_text(strip=True)
        if not text:
            continue

        # 获取HTML内容（保留富文本样式）
        inner_html = element.decode_contents().strip()

        # 构建计划项HTML
        items_html.append(f'''
        <div class="next-plan-item">
            <div class="next-plan-icon">{svg_target}</div>
            <div class="next-plan-text">{inner_html}</div>
        </div>
        ''')

    # 如果没有段落元素，按换行分割纯文本
    if not items_html:
        lines = full_text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # 处理可能存在的HTML标签
                line_soup = BeautifulSoup(line, 'html.parser')
                inner_text = line_soup.get_text(strip=True)
                if inner_text:
                    items_html.append(f'''
                    <div class="next-plan-item">
                        <div class="next-plan-icon">{svg_target}</div>
                        <div class="next-plan-text">{inner_text}</div>
                    </div>
                    ''')

    return '\n'.join(items_html) if items_html else '<p class="empty-content">暂无内容</p>'


def _render_coord_items(content_parts):
    """
    渲染待协调事项章节

    按序号（如 1、 或 1.）划分事项，每个事项按"——"分隔事项要点和协调人员

    参数:
        content_parts: 内容片段列表

    返回:
        HTML字符串
    """
    import re
    from bs4 import BeautifulSoup

    # 合并所有文本内容
    full_text = ''
    for part in content_parts:
        text = part.get('text', '')
        if text:
            full_text += text

    if not full_text.strip():
        return '<p class="empty-content">暂无内容</p>'

    items = []

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(full_text, 'html.parser')

    # 遍历所有直接子元素（包括 p, div, hr, table 等）
    current_item = None

    for element in soup.children:
        # 跳过空白文本节点
        if isinstance(element, str) and not element.strip():
            continue

        # 处理标签元素
        if hasattr(element, 'name'):
            # 对于非内容元素（hr, table等），直接添加到当前事项
            if element.name in ['hr', 'table', 'br']:
                if current_item:
                    current_item['content'] += '\n' + str(element)
                continue

            # 对于内容元素（p, div等）
            if element.name in ['p', 'div']:
                # 获取纯文本内容
                p_text = element.get_text(strip=True)

                # 检查是否以序号开头
                num_match = re.match(r'^(\d+)[、.．]\s*', p_text)

                if num_match:
                    # 保存上一个事项
                    if current_item:
                        items.append(current_item)

                    # 新事项
                    num = num_match.group(1)

                    # 移除序号后的纯文本
                    remaining_text = p_text[len(num_match.group(0)):]

                    # 按"——"分割纯文本
                    if '——' in remaining_text:
                        dash_pos = remaining_text.find('——')
                        content_text = remaining_text[:dash_pos].strip()
                        assignee_text = remaining_text[dash_pos + 2:].strip()
                    else:
                        content_text = remaining_text.strip()
                        assignee_text = ''

                    # 提取事项要点部分的HTML（不包含序号和协调人员）
                    p_html = str(element)

                    # 构建事项要点HTML：保留原有格式
                    content_soup = BeautifulSoup(p_html, 'html.parser')
                    content_p = content_soup.find(['p', 'div'])

                    if content_p:
                        # 获取内部HTML
                        inner_html = content_p.decode_contents()

                        # 移除开头的序号
                        inner_text = content_p.get_text()
                        if inner_text.strip().startswith(num_match.group(0)):
                            inner_html = _remove_number_from_html(inner_html, num_match.group(0))

                        # 移除协调人员部分（从"——"开始）
                        if '——' in inner_html or '——' in content_p.get_text():
                            inner_html = _remove_assignee_from_html(inner_html, '——')

                        content_html = inner_html.strip()
                    else:
                        content_html = content_text

                    current_item = {
                        'num': num,
                        'content': content_html,
                        'assignee': assignee_text
                    }

                elif current_item:
                    # 继续上一个事项
                    p_text_clean = element.get_text(strip=True)

                    if '——' in p_text_clean:
                        dash_pos = p_text_clean.find('——')
                        additional_assignee = p_text_clean[dash_pos + 2:].strip()

                        # 保留原始HTML标签和样式
                        p_html = str(element)
                        # 移除协调人员部分
                        p_html_clean = _remove_assignee_from_html(p_html, '——')
                        current_item['content'] += '\n' + p_html_clean
                        if additional_assignee:
                            current_item['assignee'] += ' ' + additional_assignee
                    else:
                        # 添加内容，保留完整的HTML格式（包括<p>标签及其样式）
                        p_html = str(element)
                        current_item['content'] += '\n' + p_html

    # 保存最后一个事项
    if current_item:
        items.append(current_item)

    if not items:
        return '<p class="empty-content">暂无内容</p>'

    # 渲染HTML
    items_html = []
    for item in items:
        num_html = f'<div class="coord-num">{item["num"]}</div>'

        # 事项要点
        content_html = item.get('content', '').strip()

        # 清理可能残留的未闭合标签
        content_html = _clean_html_tags(content_html)

        # 协调人员
        assignee_html = ''
        assignee = item.get('assignee', '').strip()
        if assignee:
            assignee_html = f'''
            <div class="coord-assignee">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 8v4M11 16h2"></path></svg>
                <span>{assignee}</span>
            </div>
            '''

        text_html = f'''
        <div class="coord-text">
            {content_html}
            {assignee_html}
        </div>
        '''

        items_html.append(f'''
        <div class="coord-item">
            {num_html}
            {text_html}
        </div>
        ''')

    return '\n'.join(items_html)


def _remove_number_from_html(html_content, number_text):
    """从HTML开头移除序号"""
    import re

    # 简化处理：直接替换开头的序号文本
    # 获取纯文本确认开头是序号
    plain_text = re.sub(r'<[^>]+>', '', html_content)

    if plain_text.strip().startswith(number_text):
        # 使用正则移除（考虑序号可能在标签内外）
        # 尝试多种模式
        patterns = [
            # 序号直接在开头
            r'^' + re.escape(number_text),
            # 序号在开头标签后
            r'^([^<]*?)' + re.escape(number_text),
            # 序号可能被标签包裹
            r'^(<[^>]*>)' + re.escape(number_text),
        ]

        for pattern in patterns:
            result = re.sub(pattern, '', html_content, count=1)
            if result != html_content:
                return result

    return html_content


def _remove_assignee_from_html(html_content, dash_text):
    """从HTML中移除协调人员部分（从'——'开始的内容）"""
    import re
    from bs4 import BeautifulSoup

    # 获取纯文本找到"——"的位置
    plain_text = re.sub(r'<[^>]+>', '', html_content)

    if dash_text not in plain_text:
        return html_content

    # 找到"——"在纯文本中的位置
    dash_pos_plain = plain_text.find(dash_text)

    # 在HTML中找到对应位置
    # 计算到"——"之前的字符数（不包括HTML标签）
    char_count = 0
    html_pos = 0
    in_tag = False

    for i, c in enumerate(html_content):
        if c == '<':
            in_tag = True
        elif c == '>':
            in_tag = False
        elif not in_tag:
            if char_count < dash_pos_plain:
                char_count += 1
                html_pos = i + 1
            else:
                break

    # 截取到"——"之前的HTML（包含闭合标签）
    result = html_content[:html_pos]

    # 确保HTML标签闭合
    result = _close_html_tags(result)

    return result.strip()


def _close_html_tags(html_content):
    """闭合未闭合的HTML标签"""
    import re

    # 自闭合标签，不需要闭合
    void_tags = {'br', 'hr', 'img', 'input', 'meta', 'link', 'col', 'area', 'base', 'embed', 'source', 'track', 'wbr'}

    # 找到所有开始标签
    open_tags = re.findall(r'<([a-z]+)[^>]*>', html_content, re.IGNORECASE)

    # 找到所有闭合标签
    close_tags = re.findall(r'</([a-z]+)>', html_content, re.IGNORECASE)

    # 计算需要闭合的标签
    open_count = {}
    close_count = {}

    for tag in open_tags:
        open_count[tag] = open_count.get(tag, 0) + 1

    for tag in close_tags:
        close_count[tag] = close_count.get(tag, 0) + 1

    # 添加缺失的闭合标签
    missing_tags = []
    for tag in open_count:
        # 跳过自闭合标签
        if tag.lower() in void_tags:
            continue
        missing = open_count[tag] - close_count.get(tag, 0)
        for _ in range(missing):
            missing_tags.append(tag)

    # 添加闭合标签（逆序添加，确保正确嵌套）
    for tag in reversed(missing_tags):
        html_content += f'</{tag}>'

    return html_content


def _clean_html_tags(html_content):
    """清理HTML标签，确保正确闭合"""
    return _close_html_tags(html_content)


def _split_by_dash(html_content):
    """
    按"——"分割HTML内容为事项要点和协调人员

    参数:
        html_content: HTML内容

    返回:
        (content_part, assignee_part) 元组
    """
    if '——' not in html_content:
        return html_content, ''

    # 找到"——"在HTML中的位置
    dash_pos = html_content.find('——')

    # 分割
    content_part = html_content[:dash_pos]
    assignee_part = html_content[dash_pos + 2:]  # 跳过"——"

    # 清理assignee中的HTML标签，但保留文本
    # 由于原始HTML可能没有正确闭合，我们提取纯文本
    import re
    assignee_text = re.sub(r'<[^>]+>', '', assignee_part)
    assignee_text = assignee_text.strip()

    return content_part.strip(), assignee_text


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
        color: #103979;
    }
    .panel-section-title::before {
        content: "";
        display: block;
        width: 4px;
        height: 24px;
        background: #103979;
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
        height: 20px;
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
        color: #103979;
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

    /* 待协调事项样式 */
    .coord-list {
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .coord-item {
        display: flex;
        gap: 12px;
        padding: 14px 16px;
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .coord-num {
        width: 28px;
        height: 28px;
        background: #1C91FD;
        color: #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
    }
    .coord-text {
        font-size: 13px;
        line-height: 1.7;
        flex: 1;
    }
    .coord-text hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 14px 0;
    }
    .coord-text table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 12px;
    }
    .coord-text th,
    .coord-text td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: center;
    }
    .coord-text th {
        background: #f0f4f8;
        font-weight: 600;
        color: #333;
    }
    .coord-text td {
        color: #555;
    }
    .coord-text p[style*="padding-left"] {
        margin-bottom: 4px;
    }
    .coord-assignee {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 8px;
        font-size: 12px;
        color: #D93025;
        font-weight: 700;
    }

    /* UI自动化建设 */
    .three-col {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px;
    }
    .three-col .metric-card {
        background: #f0f4f8;
        border-radius: 8px;
        text-align: center;
        min-height: 160px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .three-col .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .three-col .metric-card .metric-label {
        font-size: 12px;
        color: #6b7280;
        margin-top: 8px;
    }
    .three-col .metric-card .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #50A5F4;
        margin-top: 4px;
    }
    .ui-remaining.rich-text-content {
        margin-top: 16px;
    }
    .ui-remaining.rich-text-content ul {
        padding-left: 20px;
        margin: 8px 0;
    }
    .ui-remaining.rich-text-content li {
        font-size: 13px;
        line-height: 1.8;
        color: #333;
    }
    .ui-remaining.rich-text-content hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 14px 0;
    }
    .ui-remaining.rich-text-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 12px;
    }
    .ui-remaining.rich-text-content th,
    .ui-remaining.rich-text-content td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: center;
    }
    .ui-remaining.rich-text-content th {
        background: #f0f4f8;
        font-weight: 600;
        color: #333;
    }
    .ui-remaining.rich-text-content td {
        color: #555;
    }
    .ui-remaining.rich-text-content p[style*="padding-left"] {
        margin-bottom: 4px;
    }

    /* 下周测试计划样式 */
    .next-plan-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .next-plan-item {
        display: flex;
        gap: 12px;
        padding: 14px 16px;
        background: #f0f7ff;
        border: 1px solid #dbeafe;
        border-radius: 8px;
        align-items: flex-start;
    }
    .next-plan-icon {
        flex-shrink: 0;
    }
    .next-plan-text {
        font-size: 13px;
        line-height: 1.7;
        flex: 1;
        color: #333;
        align-self: center;
        margin-top: 3px;
    }
    .next-plan-text p {
        margin: 0;
    }
    .next-plan-list .empty-content {
        color: #9ca3af;
        font-style: italic;
    }

    /* 缺陷预警卡片 */
    .warning-card {
        display: flex;
        flex-direction: column;
    }
    .warning-list {
        flex: 1;
        overflow-y: auto;
        max-height: 100%;
    }
    .warning-list .empty-content {
        color: #9ca3af;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
    .warning-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
        margin-bottom: 6px;
    }
    .warning-dot {
        width: 8px;
        height: 8px;
        background: #1C91FD;
        border-radius: 50%;
        flex-shrink: 0;
        margin-right: 8px;
    }
    .warning-row:hover {
        background: #f0f4f8;
    }
    .warning-row:last-child {
        margin-bottom: 0;
    }
    .warning-text {
        flex: 1;
        font-size: 13px;
        color: #333;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: 10px;
    }
    .handler-tag {
        display: inline-block;
        padding: 4px 10px;
        background: #e3f2fd;
        color: #1976d2;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin: 0 4px;
    }
    .warning-tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        background: #ffdcdb9c;
        color: #e74c3c;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* 缺陷详情弹窗 - 与明细视图一致 */
    .warning-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(170,150,218,0.15);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    .warning-modal-overlay.active {
        opacity: 1;
        visibility: visible;
    }
    .warning-modal {
        background: white;
        border-radius: 16px;
        width: 90%;
        max-width: 600px;
        max-height: 80vh;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(170,150,218,0.25);
        transform: scale(0.8) translateY(-30px);
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .warning-modal-overlay.active .warning-modal {
        transform: scale(1) translateY(0);
        opacity: 1;
    }
    .warning-modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        background: #f8f9fa;
        border-radius: 16px 16px 0 0;
        border-bottom: 1px solid #eee;
    }
    .warning-modal-title {
        font-family: 'Microsoft YaHei';
        font-size: 16px;
        color: #1C91FD;
        font-weight: 600;
    }
    .warning-modal-close {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #fff;
        border: 1px solid #eee;
        color: #1C91FD;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
    }
    .warning-modal-close:hover {
        transform: rotate(90deg);
        background: #1C91FD;
        border-color: #1C91FD;
        color: #fff;
    }
    .warning-modal-body {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
    }
    .warning-modal-body::-webkit-scrollbar { width: 4px; }
    .warning-modal-body::-webkit-scrollbar-thumb { background: #1C91FD; border-radius: 2px; }
    .warning-detail-row {
        display: flex;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: #fff;
        transition: all 0.2s;
    }
    .warning-detail-row:hover {
        background: #fafafa;
        transform: translateX(6px);
    }
    .warning-detail-row:last-child {
        margin-bottom: 0;
    }
    .warning-detail-label {
        width: 90px;
        flex-shrink: 0;
        font-family: 'Microsoft YaHei';
        font-size: 13px;
        color: #1C91FD;
        font-weight: bold;
    }
    .warning-detail-value {
        flex: 1;
        font-family: 'Microsoft YaHei';
        font-size: 13px;
        color: #333;
        word-break: break-all;
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

        // 同步缺陷预警卡片高度
        syncWarningListHeight();
        window.addEventListener('resize', syncWarningListHeight);

        // 初始化预警行点击事件
        initWarningRowClick();
    });

    // 同步缺陷预警列表高度与左侧卡片一致
    function syncWarningListHeight() {
        var leftCard = document.getElementById('left-progress-card');
        var warningList = document.getElementById('warning-list');
        if (leftCard && warningList) {
            var leftHeight = leftCard.offsetHeight;
            var titleHeight = warningList.previousElementSibling ? warningList.previousElementSibling.offsetHeight : 0;
            // 计算可用高度：左侧卡片高度 - 标题行高度 - padding
            var availableHeight = leftHeight - 50; // 50px为标题行和padding预留
            warningList.style.maxHeight = Math.max(availableHeight, 100) + 'px';
        }
    }

    // 初始化预警行点击事件
    function initWarningRowClick() {
        document.querySelectorAll('.warning-row').forEach(function(row) {
            row.addEventListener('click', function() {
                var detailJson = this.getAttribute('data-detail');
                if (detailJson) {
                    try {
                        var detail = JSON.parse(detailJson);
                        showWarningModal(detail);
                    } catch (e) {
                        console.error('解析详情数据失败', e);
                    }
                }
            });
        });
    }

    // 显示详情弹窗
    function showWarningModal(detail) {
        // 字段名称映射（排除不需要展示的字段）
        var excludeFields = ['登记时间', '任务分类', '关联任务项'];
        var fieldLabels = {
            '缺陷编号': '缺陷编号',
            '产品线': '产品线',
            '产品模块': '产品模块',
            '缺陷状态': '缺陷状态',
            '缺陷摘要': '缺陷摘要',
            '优先级': '优先级',
            '登记人': '登记人',
            '处理人员': '处理人员',
            '登记时间.1': '登记时间',
            '修复时间': '修复时间',
            '关闭时间': '关闭时间',
            '发现阶段': '发现阶段',
            '引入阶段': '引入阶段',
            '引入原因': '引入原因',
            '缺陷来源': '缺陷来源',
            '返工次数': '返工次数',
            '严重程度': '严重程度',
            '缺陷类型': '缺陷类型',
            '缺陷修复周期(天)': '缺陷修复周期(天)',
            '缺陷关闭周期(天)': '缺陷关闭周期(天)'
        };

        // 构建详情内容
        var detailHtml = '';
        for (var key in detail) {
            if (detail.hasOwnProperty(key)) {
                // 跳过排除字段
                if (excludeFields.indexOf(key) !== -1) continue;
                // 跳过未定义标签的字段
                if (!fieldLabels[key]) continue;
                var label = fieldLabels[key];
                var value = detail[key];
                // 处理特殊值
                if (value === null || value === undefined || value === '' || (typeof value === 'number' && isNaN(value))) {
                    value = '-';
                } else if (typeof value === 'object') {
                    value = JSON.stringify(value);
                }
                detailHtml += '<div class="warning-detail-row">' +
                    '<div class="warning-detail-label">' + label + '</div>' +
                    '<div class="warning-detail-value">' + value + '</div>' +
                    '</div>';
            }
        }

        // 创建弹窗
        var modalHtml = '<div class="warning-modal-overlay" id="warning-modal-overlay">' +
            '<div class="warning-modal">' +
            '<div class="warning-modal-header">' +
            '<span class="warning-modal-title">缺陷详情 - ' + (detail['缺陷编号'] || '') + '</span>' +
            '<button class="warning-modal-close" onclick="closeWarningModal()">&times;</button>' +
            '</div>' +
            '<div class="warning-modal-body">' + detailHtml + '</div>' +
            '</div>' +
            '</div>';

        // 移除已存在的弹窗
        var existingModal = document.getElementById('warning-modal-overlay');
        if (existingModal) {
            existingModal.remove();
        }

        // 添加弹窗到页面
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // 显示弹窗
        setTimeout(function() {
            document.getElementById('warning-modal-overlay').classList.add('active');
        }, 10);

        // 点击遮罩关闭
        document.getElementById('warning-modal-overlay').addEventListener('click', function(e) {
            if (e.target === this) {
                closeWarningModal();
            }
        });
    }

    // 关闭详情弹窗
    function closeWarningModal() {
        var modal = document.getElementById('warning-modal-overlay');
        if (modal) {
            modal.classList.remove('active');
            setTimeout(function() {
                modal.remove();
            }, 300);
        }
    }
    '''
