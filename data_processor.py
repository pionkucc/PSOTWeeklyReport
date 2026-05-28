"""
数据处理模块
负责读取Excel数据并进行预处理
"""

import pandas as pd
import numpy as np
from openpyxl import load_workbook
from config import INPUT_FILE, PANEL_SHEET_INDEX


def load_data():
    """读取Excel数据，返回 DataFrame 和统计数据"""
    df = pd.read_excel(INPUT_FILE)
    total = len(df)

    # 从sheet2读取任务项统计
    df_sheet2 = pd.read_excel(INPUT_FILE, sheet_name=1)
    task_count = len(df_sheet2) - 1
    subtask_count = df_sheet2.iloc[-1, 4] if len(df_sheet2) > 0 else 0

    return df, total, task_count, subtask_count


def preprocess_data(df):
    """预处理数据，修复周期列类型转换"""
    df['缺陷修复周期(天)'] = pd.to_numeric(
        df['缺陷修复周期(天)'].replace('/', np.nan), errors='coerce'
    )
    return df


def load_panels_data():
    """读取sheet3公共面板数据，保留富文本格式"""
    wb = load_workbook(INPUT_FILE)
    ws = wb.worksheets[PANEL_SHEET_INDEX]

    panels = []
    for row_idx in range(2, ws.max_row + 1):
        title = ws.cell(row=row_idx, column=1).value
        content_cell = ws.cell(row=row_idx, column=2)

        if not title:  # 跳过空标题行
            continue

        # 解析内容，保留富文本格式
        content_parts = []
        content_value = content_cell.value

        if content_value:
            # 检查是否是富文本（CellRichText类型）
            if hasattr(content_value, '__iter__') and not isinstance(content_value, str):
                for part in content_value:
                    part_text = ''
                    part_bold = False
                    part_color = None

                    if isinstance(part, str):
                        part_text = part
                    elif hasattr(part, 'text'):
                        part_text = part.text or ''
                        if hasattr(part, 'font') and part.font:
                            font = part.font
                            part_bold = getattr(font, 'b', False) or False
                            if hasattr(font, 'color') and font.color:
                                if hasattr(font.color, 'rgb') and font.color.rgb:
                                    part_color = str(font.color.rgb)

                    content_parts.append({
                        'text': part_text,
                        'bold': part_bold,
                        'color': part_color
                    })
            else:
                # 纯文本，检查单元格整体字体样式
                cell_bold = False
                cell_color = None
                if content_cell.font:
                    cell_bold = getattr(content_cell.font, 'b', False) or False
                    if hasattr(content_cell.font, 'color') and content_cell.font.color:
                        if hasattr(content_cell.font.color, 'rgb') and content_cell.font.color.rgb:
                            cell_color = str(content_cell.font.color.rgb)

                content_parts.append({
                    'text': str(content_value),
                    'bold': cell_bold,
                    'color': cell_color
                })

        panels.append({
            'title': str(title),
            'content_parts': content_parts
        })

    wb.close()
    return panels
