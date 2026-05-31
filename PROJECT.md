# 缺陷质量分析可视化报告生成器

生成清新UI风格的交互式HTML图表报告，支持主页视图、图表视图和明细视图切换。

## 在线访问

- **GitHub Pages**: https://pionkucc.github.io/PSOTWeeklyReport/PSOT_Weekly_Report_2026.05.25-2026.05.29.html
- **GitLab Pages**: https://psot-qc.pages.jihulab.com/weekly-report-project/PSOT_Weekly_Report_2026.05.25-2026.05.29.html
- **GitHub 仓库**: https://github.com/pionkucc/PSOTWeeklyReport
- **GitLab 仓库**: https://jihulab.com/psot-qc/weekly-report-project

> 注：仓库均为私有，但 Pages 公开可访问

## 快速开始

```bash
python defect_quality_report.py
```

输出文件：`PSOT_Weekly_Report_YYYY.MM.DD-YYYY.MM.DD.html`（根据日期动态生成）

## 更新数据流程

### 方式一：本地脚本推送（推荐）

```bash
python auto_push.py
```

脚本自动执行：生成报告 → Git提交 → 选择推送平台 → CI/CD自动部署

**推送选项**：
- `1` - 仅推送到 GitHub
- `2` - 仅推送到 GitLab（极狐）
- `3` - 同时推送到 GitHub 和 GitLab

### 方式二：手动操作

1. 替换 `缺陷明细.xlsx` 数据文件
2. 修改 `config.py` 中的 `SUBTITLE`（日期范围）
3. 运行 `python defect_quality_report.py`
4. Git提交并推送
5. 等待 CI/CD 部署完成

## CI/CD 自动部署

### GitHub Actions

文件：`.github/workflows/deploy.yml`

**触发条件**：push 到 main/master 分支

**查看运行状态**：https://github.com/pionkucc/PSOTWeeklyReport/actions

### GitLab CI/CD

文件：`.gitlab-ci.yml`

**触发条件**：push 到 main/master 分支

**查看运行状态**：https://jihulab.com/psot-qc/weekly-report-project/-/pipelines

## 项目结构

```
F:\AI\Claude Code\Weekly_Report\
├── defect_quality_report.py    # 主入口程序
├── config.py                   # 配置常量模块（动态文件名生成）
├── data_processor.py           # 数据处理模块
├── auto_push.py                # 本地自动推送脚本（不提交到仓库）
├── requirements.txt            # Python依赖清单
├── .gitignore                  # Git排除配置
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions工作流
├── .gitlab-ci.yml              # GitLab CI/CD工作流
├── views/
│   ├── __init__.py
│   ├── chart_views.py          # 图表视图函数
│   ├── detail_view.py          # 明细视图函数
│   └── home_view.py            # 主页视图函数
├── templates/
│   ├── __init__.py
│   └── html_template.py        # HTML模板构建
├── versions/                    # 版本备份目录
│   ├── VERSION.md              # 版本记录
│   ├── v3.1_modular_backup.zip # v3.1备份
│   ├── v3.2_modular_backup.zip # v3.2备份
│   ├── v3.3_modular_backup.zip # v3.3备份
│   ├── v3.4_modular_backup.zip # v3.4备份
│   ├── v3.4.2_modular_backup.zip # v3.4.2备份
│   └── v3.4.3_modular_backup.zip # v3.4.3备份
├── history_reports/             # 历史报告归档目录
│   └── PSOT_Weekly_Report_*.html # 带日期的历史版本
├── 缺陷明细.xlsx                # 数据源
└── PSOT_Weekly_Report.html      # 固定名称报告（Pages使用）
```

## 模块说明

### 1. config.py - 配置常量模块

**职责**：定义全局常量配置

**导出内容**：
| 常量 | 类型 | 说明 |
|------|------|------|
| `COLORS` | dict | 颜色配置字典，包含 pastel、fresh、status、status_soft、priority、severity、stage_find |
| `INPUT_FILE` | str | 输入文件路径 `'缺陷明细.xlsx'` |
| `OUTPUT_FILE` | str | 输出文件路径，动态生成 |
| `TITLE` | str | 报告标题 |
| `SUBTITLE` | str | 报告副标题（日期范围），支持两种格式 |
| `TOOLTIP_CSS` | str | Tooltip样式常量 |
| `OVERDUE_DAYS` | int | 缺陷超期天数阈值，默认3 |
| `REWORK_THRESHOLD` | int | 返工次数阈值，默认3 |

**SUBTITLE支持格式**：
- `"2026-05-18 ~ 2026-05-22"`
- `"报告周期：2026年05月25日-2026年05月29日"`

---

### 2. data_processor.py - 数据处理模块

**职责**：读取Excel数据并进行预处理

**导出函数**：

#### `load_data()`
- **功能**：读取Excel数据
- **返回**：`(df, total, task_count, subtask_count)`

#### `preprocess_data(df)`
- **功能**：预处理修复周期列，将 '/' 替换为 NaN，转换为数值类型
- **返回**：处理后的 DataFrame

#### `load_panels_data()`
- **功能**：读取Sheet3公共面板数据，保留富文本格式
- **返回**：面板数据列表，每项包含 title 和 content_parts

#### `load_sheet2_data()`
- **功能**：读取Sheet2测试进度和缺陷统计数据
- **返回**：DataFrame（测试进度表格数据）

#### `load_warning_data()`
- **功能**：读取缺陷预警数据，筛选超期、返工、超期返工三类
- **返回**：dict，包含 overdue_rework、overdue、rework、total

---

### 3. views/chart_views.py - 图表视图模块

**职责**：生成各类ECharts图表

**导出函数**：

| 函数 | 功能 | 参数 |
|------|------|------|
| `chart_to_html(chart, chart_id)` | 将ECharts图表转换为内嵌HTML | chart对象, chart_id |
| `create_pie_chart(data, title, hole, colors, height)` | 创建饼图/环形图 | 数据列, 标题, 内径比例, 颜色, 高度 |
| `create_horizontal_bar_with_legend(data, title, colors, chart_id, order)` | 创建横向柱状图（带图例） | 数据列, 标题, 颜色, 图表ID, 排序 |
| `create_vertical_bar_with_legend(data, title, colors, chart_id, order)` | 创建纵向柱状图（带图例） | 同上 |
| `create_histogram(data, title, height)` | 创建直方图 | 数据列, 标题, 高度 |
| `create_metrics_cards_html(df, total, task_count, subtask_count)` | 创建质量指标卡片 | df, 总数, 任务数, 子任务数 |

---

### 4. views/detail_view.py - 明细视图模块

**职责**：生成缺陷明细列表视图

**导出函数**：

#### `create_detail_view_html(df, total)`
- **功能**：创建完整的明细视图HTML
- **参数**：`df` - DataFrame，`total` - int
- **返回**：HTML字符串

**功能特性**：
1. **筛选导航栏**：状态、处理人员、优先级下拉筛选 + 重置按钮
2. **数据表格**：9列展示
3. **排序**：按登记时间倒序
4. **弹窗详情**：双击行弹出完整字段展示

---

### 5. views/home_view.py - 主页视图模块

**职责**：生成主页视图HTML

**导出函数**：

#### `create_home_view_html(panels_data, sheet2_data, warning_data)`
- **功能**：创建主页视图HTML
- **参数**：
  - `panels_data`: 公共面板数据列表
  - `sheet2_data`: Sheet2表格数据DataFrame
  - `warning_data`: 缺陷预警数据字典
- **返回**：HTML字符串

**功能特性**：
1. **本周测试概况**：两列卡片布局
   - 测试进度概览：动态提取[xxx]标签、进度指标、缺陷统计
   - 缺陷预警：数据驱动展示
     - 三类预警：超期返工（优先级最高）> 超期 > 返工
     - 展示格式：蓝色圆点 + 缺陷编号 + 处理人标签（浅蓝色）+ 缺陷摘要（省略号截断）+ 浅红色标签
     - 点击行弹出详情弹窗，展示全部字段
     - 高度同步左侧卡片，超出滚动
2. **测试进度和缺陷统计**：表格 + 条形图双卡片
3. **待协调事项**：特殊渲染
   - 按序号（如1、）划分事项，蓝色圆形序号
   - 按"——"分隔事项要点和协调人员
   - 协调人员红色样式带警告SVG图标
   - 保留富文本格式（缩进、分割线、表格）
4. **下周测试计划**：特殊渲染
   - 每行作为一个计划项
   - SVG同心圆图标（蓝色外圈 + 白色中圈）
   - 浅蓝背景卡片 + 蓝色边框
   - 支持富文本格式（同待协调事项）
5. **PSOT-UI自动化建设**：特殊渲染
   - 提取完成场景数、自动化执行成功/失败率、下周计划
   - 三列卡片展示（带SVG图标），min-height 160px
   - 成功/失败动态变色（蓝色/红色）
   - 下方展示剩余富文本内容
6. **其他章节**：普通富文本渲染

#### `get_home_view_css()`
- **功能**：获取主页视图专用CSS

#### `get_home_view_js()`
- **功能**：获取主页视图专用JS（tooltip检测、预警弹窗、高度同步）

---

### 6. templates/html_template.py - HTML模板模块

**职责**：组装完整的HTML报告页面

**导出函数**：

#### `build_html_template(total, metrics_html, charts_html, trend_chart_html, detail_view_html, home_view_html)`
- **功能**：组装完整HTML报告
- **返回**：完整HTML字符串

#### `save_report(html_content)`
- **功能**：保存HTML报告到文件

**内置功能**：
1. **截图功能**（v3.4.2新增）
   - 使用 dom-to-image-more 库截取完整页面
   - 完美保留 CSS 渐变背景（包括多层径向渐变）
   - 截图成功弹窗：预览 + 保存 + 复制到剪贴板
   - 保存功能：File System Access API 选择保存位置
   - 复制功能：Clipboard API 图片粘贴支持
2. **视图切换**：主页/图表/明细三视图切换
3. **图表交互**：切换表格、放大弹窗

---

### 7. defect_quality_report.py - 主入口程序

**职责**：协调各模块，生成完整报告

**执行流程**：
```
1. 加载数据 (data_processor.load_data)
2. 预处理数据 (data_processor.preprocess_data)
3. 生成图表视图（13个图表）
4. 加载公共面板数据 (data_processor.load_panels_data)
5. 加载Sheet2数据 (data_processor.load_sheet2_data)
6. 加载预警数据 (data_processor.load_warning_data)
7. 生成主页视图 (home_view.create_home_view_html)
8. 生成明细视图 (detail_view.create_detail_view_html)
9. 组装HTML模板 (html_template.build_html_template)
10. 保存报告 (html_template.save_report)
```

---

## 数据源结构

**文件**：`缺陷明细.xlsx`

**Sheet1 - 缺陷明细**：
| 列索引 | 列名 | 说明 |
|--------|------|------|
| 0 | 登记时间 | 时间范围 |
| 1 | 迭代版本 | 版本信息 |
| 2 | 关联模块 | 模块名称 |
| 3 | 缺陷编号 | 唯一标识 |
| 4 | 产品线 | 产品分类 |
| 5 | 产品模块 | 模块分类 |
| 6 | 缺陷状态 | New/Closed/Fixed/Pending/ReOpen |
| 7 | 缺陷摘要 | 问题描述 |
| 8 | 优先级 | 低/中/高/优先 |
| 9 | 登记人 | 登记者 |
| 10 | 处理人员 | 负责人 |
| 11 | 登记时间.1 | 具体时间 |
| 12 | 修复时间 | 修复时间 |
| 13 | 关闭时间 | 关闭时间 |
| 14 | 发现阶段 | 测试阶段 |
| 15 | 引入阶段 | 引入环节 |
| 16 | 引入原因 | 原因分类 |
| 17 | 缺陷来源 | 来源渠道 |
| 18 | 返工次数 | 返工计数 |
| 19 | 严重程度 | 严重/一般/轻微/建议 |
| 20 | 缺陷类型 | 类型分类 |
| 21 | 缺陷修复周期(天) | 修复时长 |
| 22 | 缺陷关闭周期(天) | 关闭时长 |

**Sheet3 - 公共面板**：
- 按行存储，每行包含标题和内容
- 内容支持富文本格式（HTML）

---

## 视图切换功能

报告支持三种视图：

### 主页视图（默认）
- 本周测试概况（进度概览 + 缺陷预警）
- 测试进度和缺陷统计（表格 + 条形图）
- 待协调事项（序号卡片 + 协调人员标签）
- PSOT-UI自动化建设（三列指标卡片 + 详情）
- 其他面板内容

### 图表视图
- 质量指标概览（5个卡片）
- 13个可视化图表

### 明细视图
- 筛选导航栏
- 数据表格（分页/排序）
- 详情弹窗

---

## 配色方案

**主色调**：蓝色 #1C91FD

**字体**：-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif

**状态配色**：
| 状态 | 颜色 |
|------|------|
| New | #F7DC6F（黄色） |
| Closed | #82E0AA（绿色） |
| Fixed | #76D7C4（青色） |
| Pending | #AA96DA（紫色） |
| ReOpen | #F0B27A（橙色） |

---

## 依赖库

**Python依赖**：
```
pandas
pyecharts
numpy
openpyxl (Excel读取)
beautifulsoup4 (富文本解析)
```

**前端CDN依赖**：
```
echarts@5 (图表渲染)
dom-to-image-more@3.5 (截图功能，完美保留CSS渐变)
```

---

## 扩展指南

### 添加新图表

1. 在 `views/chart_views.py` 中创建新函数
2. 在主程序 `defect_quality_report.py` 中调用
3. 将返回的HTML添加到 `charts_html` 列表

### 修改配色

编辑 `config.py` 中的 `COLORS` 字典

### 调整预警阈值

编辑 `config.py` 中的 `OVERDUE_DAYS` 和 `REWORK_THRESHOLD`

### 调整明细表格列

编辑 `views/detail_view.py` 中的 `display_cols` 和 `detail_cols` 字典
