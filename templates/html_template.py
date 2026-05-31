"""
HTML模板模块
负责组装完整的HTML报告页面
"""

from config import TITLE, SUBTITLE, OUTPUT_FILE
from views.home_view import get_home_view_css, get_home_view_js


def build_html_template(total, metrics_html, charts_html, trend_chart_html, detail_view_html, home_view_html):
    """组装完整HTML报告"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dom-to-image-more@3.5/dist/dom-to-image-more.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(22, 119, 255, 0.35) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(22, 119, 255, 0.28) 0%, transparent 50%),
                radial-gradient(ellipse at 40% 60%, rgba(22, 119, 255, 0.2) 0%, transparent 40%),
                radial-gradient(ellipse at 70% 30%, rgba(22, 119, 255, 0.22) 0%, transparent 45%),
                radial-gradient(ellipse at 50% 50%, rgba(22, 119, 255, 0.15) 0%, transparent 60%),
                linear-gradient(180deg, #d6ebff 0%, #e6f4ff 50%, #f0f5ff 100%);
            min-height: 100vh;
            padding: 30px 20px;
            -webkit-font-smoothing: antialiased;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; color: #2c3e50; }}
        .header h1 {{ font-size: 36px; font-weight: 700; margin-bottom: 10px; margin-top: 20px; color: #103979; }}
        .header p {{ font-size: 16px; color: #5d6d7e; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); padding: 20px; transition: all 0.3s ease; position: relative; height: 420px; overflow: hidden; }}
        .card-full {{ grid-column: 1 / -1; background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); padding: 20px 30px; transition: all 0.3s ease; }}
        .card-wide {{ grid-column: span 2; background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); padding: 20px; transition: all 0.3s ease; position: relative; height: 420px; overflow: hidden; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 60px rgba(0,0,0,0.15); }}
        .chart-card {{ height: 100%; }}
        .chart-toolbar {{ position: absolute; top: 10px; right: 15px; display: flex; gap: 6px; z-index: 10; }}
        .chart-btn {{ width: 32px; height: 32px; border-radius: 8px; border: none; background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf0 100%); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 15px; color: #7c8a9a; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }}
        .chart-btn:hover {{ background: linear-gradient(135deg, #e0e4e8 0%, #d4d8dc 100%); color: #667eea; transform: translateY(-1px); box-shadow: 0 3px 6px rgba(0,0,0,0.12); }}
        .chart-btn.active {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; box-shadow: 0 3px 8px rgba(102,126,234,0.3); }}
        .chart-container {{ min-height: 350px; }}
        .table-container {{ display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 20px; background: white; z-index: 5; overflow: hidden; }}
        .table-container.active {{ display: flex; flex-direction: column; }}
        .table-title {{ text-align: center; font-size: 16px; color: #2c3e50; font-weight: bold; font-family: 'Microsoft YaHei'; margin-bottom: 15px; flex-shrink: 0; }}
        .table-body {{ flex: 1; overflow: auto; }}
        .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; font-family: 'Microsoft YaHei'; }}
        .data-table th {{ background: #f5f7fa; padding: 8px 10px; text-align: left; font-weight: 600; color: #333; border-bottom: 2px solid #e0e0e0; position: sticky; top: 0; }}
        .data-table td {{ padding: 6px 10px; border-bottom: 1px solid #eee; color: #555; white-space: nowrap; }}
        .data-table tr:hover td {{ background: #f9f9f9; }}
        .metrics-container {{ width: 100%; }}
        .metrics-title {{ text-align: center; font-size: 16px; color: #2c3e50; font-weight: bold; margin-bottom: 20px; font-family: 'Microsoft YaHei'; }}
        .metrics-row {{ display: flex; gap: 20px; justify-content: stretch; width: 100%; }}
        .metric-card {{ flex: 1; height: 120px; border-radius: 12px; display: flex; flex-direction: column; align-items: stretch; justify-content: center; transition: all 0.3s ease; cursor: default; padding: 15px 18px; position: relative; }}
        .metric-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .metric-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .metric-name {{ font-size: 15px; color: #5a6c7d; font-family: 'Microsoft YaHei'; font-weight: bold; }}
        .metric-icon {{ width: 22px; height: 22px; opacity: 0.7; position: relative; }}
        .icon-task {{ width: 20px; height: 22px; border: 2px solid #fff; border-radius: 4px; position: relative; }}
        .icon-task::before {{ content: ''; position: absolute; top: 5px; left: 4px; width: 10px; height: 2px; background: #fff; border-radius: 1px; }}
        .icon-task::after {{ content: ''; position: absolute; top: 10px; left: 4px; width: 7px; height: 2px; background: #fff; border-radius: 1px; }}
        .icon-bug {{ width: 20px; height: 20px; position: relative; }}
        .icon-bug::before {{ content: ''; position: absolute; top: 3px; left: 5px; width: 10px; height: 14px; border: 2px solid #fff; border-radius: 50% 50% 45% 45%; }}
        .icon-bug::after {{ content: ''; position: absolute; top: 7px; left: 1px; width: 4px; height: 2px; background: #fff; box-shadow: 12px 0 0 #fff, 6px 6px 0 #fff, 6px 10px 0 #fff; }}
        .icon-chart {{ width: 22px; height: 22px; position: relative; display: flex; align-items: flex-end; justify-content: space-between; }}
        .icon-chart::before {{ content: ''; position: absolute; bottom: 0; left: 0; width: 5px; height: 14px; background: #fff; border-radius: 2px 2px 0 0; }}
        .icon-chart::after {{ content: ''; position: absolute; bottom: 0; right: 0; width: 5px; height: 8px; background: #fff; border-radius: 2px 2px 0 0; }}
        .icon-screenshot {{ width: 20px; height: 20px; position: relative; }}
        .icon-screenshot::before {{ content: ''; position: absolute; top: 3px; left: 3px; width: 14px; height: 12px; border: 2px solid #fff; border-radius: 3px; }}
        .icon-screenshot::after {{ content: ''; position: absolute; top: 7px; left: 7px; width: 6px; height: 6px; border: 2px solid #fff; border-radius: 50%; }}
        .icon-clock {{ width: 20px; height: 20px; border: 2px solid #fff; border-radius: 50%; position: relative; }}
        .icon-clock::before {{ content: ''; position: absolute; top: 3px; left: 7px; width: 2px; height: 6px; background: #fff; border-radius: 1px; }}
        .icon-clock::after {{ content: ''; position: absolute; top: 7px; left: 7px; width: 5px; height: 2px; background: #fff; border-radius: 1px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2c3e50; font-family: 'Microsoft YaHei'; margin-top: 12px; }}
        .metric-subtitle {{ font-size: 11px; color: #aaa; font-family: 'Microsoft YaHei'; position: absolute; bottom: 8px; right: 15px; line-height: 1.4; text-align: right; }}
        {get_home_view_css()}
        .view-switch {{ position: absolute; top: 20px; right: 20px; display: flex; gap: 10px; }}
        .view-btn {{ padding: 10px 20px; border-radius: 25px; border: 2px solid transparent; background: rgba(145, 202, 255, 0.5); color: #ffffff; font-family: 'Microsoft YaHei'; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(22,119,255,0.1); display: inline-flex; align-items: center; }}
        .view-btn:hover {{ background: rgba(186, 224, 255, 0.7); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(22,119,255,0.2); }}
        .view-btn.active {{ background: rgba(145, 202, 255, 0.5); color: #ffffff; font-weight: 600; box-shadow: 0 4px 20px rgba(22,119,255,0.2); border: 2px solid rgba(255,255,255,0.85); }}
        .view-btn.home-btn {{ padding: 10px 14px; border-radius: 50%; }}
        .view-btn.home-btn.active {{ background: rgba(145, 202, 255, 0.5); border: 2px solid rgba(255,255,255,0.85); }}
        .view-btn.screenshot-btn {{ padding: 10px 14px; border-radius: 50%; }}
        .view-btn svg {{ flex-shrink: 0; }}
        .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); backdrop-filter: blur(8px); z-index: 1000; display: none; align-items: center; justify-content: center; }}
        .modal-overlay.active {{ display: flex; }}
        .modal-content {{ background: white; border-radius: 16px; padding: 20px; max-width: 95vw; max-height: 95vh; overflow: auto; position: relative; animation: modalIn 0.3s ease; }}
        @keyframes modalIn {{ from {{ transform: scale(0.9); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
        .modal-close {{ position: absolute; top: 10px; right: 15px; width: 32px; height: 32px; border-radius: 50%; border: none; background: #f0f0f0; cursor: pointer; font-size: 18px; color: #666; transition: all 0.3s ease; }}
        .modal-close:hover {{ background: #e74c3c; color: white; transform: rotate(90deg); }}
        .modal-chart {{ width: 1000px; height: 650px; }}
        .screenshot-modal {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); backdrop-filter: blur(8px); z-index: 2000; display: none; align-items: center; justify-content: center; }}
        .screenshot-modal.active {{ display: flex; }}
        .screenshot-dialog {{ background: white; border-radius: 16px; padding: 28px 32px; max-width: 520px; width: 90%; text-align: center; animation: modalIn 0.3s ease; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .screenshot-dialog .success-icon {{ width: 56px; height: 56px; margin: 0 auto 16px; background: linear-gradient(135deg, #82E0AA, #2ECC71); border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
        .screenshot-dialog .success-icon svg {{ width: 28px; height: 28px; }}
        .screenshot-dialog h3 {{ font-size: 18px; color: #2c3e50; margin-bottom: 6px; }}
        .screenshot-dialog p {{ font-size: 13px; color: #95a5a6; margin-bottom: 20px; }}
        .screenshot-preview {{ max-height: 200px; overflow: hidden; border-radius: 8px; border: 1px solid #eee; margin-bottom: 20px; }}
        .screenshot-preview img {{ width: 100%; display: block; }}
        .screenshot-actions {{ display: flex; gap: 12px; justify-content: center; }}
        .screenshot-actions button {{ padding: 10px 28px; border-radius: 25px; border: none; font-size: 14px; font-family: 'Microsoft YaHei'; font-weight: 500; cursor: pointer; transition: all 0.3s ease; display: inline-flex; align-items: center; gap: 6px; }}
        .screenshot-actions .btn-save {{ background: linear-gradient(135deg, #1C91FD, #1677FF); color: white; box-shadow: 0 4px 15px rgba(22,119,255,0.3); }}
        .screenshot-actions .btn-save:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(22,119,255,0.4); }}
        .screenshot-actions .btn-clipboard {{ background: #f5f7fa; color: #5d6d7e; border: 1px solid #e0e0e0; }}
        .screenshot-actions .btn-clipboard:hover {{ background: #e8ecf0; transform: translateY(-2px); }}
        .screenshot-loading {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); z-index: 3000; align-items: center; justify-content: center; }}
        .screenshot-loading.active {{ display: flex; }}
        .screenshot-loading .loading-spinner {{ background: white; border-radius: 16px; padding: 28px 36px; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .screenshot-loading .spinner {{ width: 40px; height: 40px; border: 3px solid #e0e0e0; border-top: 3px solid #1C91FD; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 12px; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .screenshot-loading p {{ font-size: 14px; color: #5d6d7e; font-family: 'Microsoft YaHei'; }}
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} .header h1 {{ font-size: 28px; }} .modal-chart {{ width: 95vw; height: 400px; }} .screenshot-dialog {{ padding: 20px; }} .screenshot-actions {{ flex-direction: column; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="position: relative;">
            <div class="view-switch">
                <button class="view-btn home-btn active" data-view="home" onclick="switchView('home')"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg></button>
                <button class="view-btn" data-view="chart" onclick="switchView('chart')"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px"><path d="M3 3v18h18V3H3zm16 16H5V5h14v14zm-2-2h-2v-6h2v6zm-4 0h-2v-4h2v4zm-4 0h-2v-8h2v8z"/></svg>图表</button>
                <button class="view-btn" data-view="detail" onclick="switchView('detail')"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="margin-right:4px"><path d="M3 3h18v2H3V3zm0 4h18v2H3V7zm0 4h18v2H3v-2zm0 4h12v2H3v-2zm0 4h8v2H3v-2z"/></svg>明细</button>
                <button class="view-btn screenshot-btn" onclick="screenshotReport()" title="截图"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15.2A3.2 3.2 0 1 0 12 8.8a3.2 3.2 0 0 0 0 6.4z"/><path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg></button>
            </div>
            <h1>{TITLE}</h1>
            <p>{SUBTITLE} | 共 {total} 条缺陷数据</p>
        </div>

        <!-- 主页视图 -->
        <div class="view-container active" id="homeView">
            {home_view_html}
        </div>

        <!-- 图表视图 -->
        <div class="view-container" id="chartView">
            <div class="grid">
                <div class="card-full">{metrics_html}</div>
                <div class="card-wide chart-card">{charts_html[0]}</div>
                <div class="card chart-card">{charts_html[1]}</div>
                <div class="card chart-card">{charts_html[2]}</div>
                <div class="card-wide chart-card">{trend_chart_html}</div>
                {''.join([f'<div class="card chart-card">{html}</div>' for html in charts_html[3:]])}
            </div>
        </div>

        <div class="view-container" id="detailView">
            {detail_view_html}
        </div>
    </div>

    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <button class="modal-close" onclick="closeModal()">&times;</button>
            <div id="modalChart" class="modal-chart"></div>
        </div>
    </div>

    <!-- 截图加载遮罩 -->
    <div class="screenshot-loading" id="screenshotLoading">
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>正在截取页面...</p>
        </div>
    </div>

    <!-- 截图成功弹窗 -->
    <div class="screenshot-modal" id="screenshotModal" onclick="closeScreenshotModal(event)">
        <div class="screenshot-dialog" onclick="event.stopPropagation()">
            <div class="success-icon">
                <svg viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
            </div>
            <h3>截图成功</h3>
            <p>图片已生成，可选择下载或复制到剪贴板</p>
            <div class="screenshot-preview"><img id="screenshotPreviewImg" src="" alt="截图预览" /></div>
            <div class="screenshot-actions">
                <button class="btn-save" onclick="saveScreenshot()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM15 3v2h3.59l-9.83 9.83 1.41 1.41L20 6.41V10h2V3h-7z"/></svg>
                    保存
                </button>
                <button class="btn-clipboard" onclick="copyToClipboard()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                    复制到剪贴板
                </button>
            </div>
        </div>
    </div>

    <script>
        var chartConfigs = [
            {{ title: '处理人员缺陷统计', categoryCol: '处理人员', hasPercent: false }},
            {{ title: '缺陷状态分布', categoryCol: '缺陷状态', hasPercent: true }},
            {{ title: '关联任务项统计', categoryCol: '任务项', hasPercent: false }},
            {{ title: '缺陷趋势分析', categoryCol: '日期', hasPercent: false }},
            {{ title: '缺陷修复周期分布', categoryCol: '修复周期(天)', hasPercent: false }},
            {{ title: '缺陷返工情况', categoryCol: '返工次数', hasPercent: true }},
            {{ title: '缺陷发现阶段分布', categoryCol: '发现阶段', hasPercent: false }},
            {{ title: '缺陷类型分布', categoryCol: '缺陷类型', hasPercent: true }},
            {{ title: '缺陷引入原因分析', categoryCol: '引入原因', hasPercent: false }},
            {{ title: '缺陷优先级分布', categoryCol: '优先级', hasPercent: false }},
            {{ title: '缺陷严重程度分布', categoryCol: '严重程度', hasPercent: false }},
            {{ title: '缺陷引入阶段分布', categoryCol: '引入阶段', hasPercent: false }}
        ];

        document.querySelectorAll('.chart-card').forEach(function(card, idx) {{
            var chartDiv = card.querySelector('div[id^="chart_"]');
            if (!chartDiv) return;

            var chartId = chartDiv.id;
            var wrapper = card.closest('.card') || card.closest('.card-wide');
            var toolbar = document.createElement('div');
            toolbar.className = 'chart-toolbar';
            toolbar.innerHTML = '<button class="chart-btn" title="切换表格" onclick="toggleTable(\\'' + chartId + '\\', ' + idx + ')"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3h18v18H3V3zm2 2v14h14V5H5zm2 2h4v4H7V7zm6 0h4v4h-4V7zm-6 6h4v4H7v-4zm6 0h4v4h-4v-4z"/></svg></button><button class="chart-btn" title="放大" onclick="enlargeChart(\\'' + chartId + '\\')"><svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zm.5-7H9v2H7v1h2v2h1v-2h2V9h-2V7z"/></svg></button>';
            wrapper.insertBefore(toolbar, wrapper.firstChild);

            var tableDiv = document.createElement('div');
            tableDiv.className = 'table-container';
            tableDiv.id = 'table_' + chartId;
            wrapper.appendChild(tableDiv);
        }});

        function toggleTable(chartId, idx) {{
            var chartDiv = document.getElementById(chartId);
            var wrapper = chartDiv.closest('.card') || chartDiv.closest('.card-wide');
            var tableDiv = document.getElementById('table_' + chartId);
            var btns = wrapper.querySelectorAll('.chart-btn');
            var toggleBtn = btns[0];
            var config = chartConfigs[idx] || {{ categoryCol: '类别', hasPercent: false }};

            if (tableDiv.classList.contains('active')) {{
                tableDiv.classList.remove('active');
                chartDiv.style.display = 'block';
                var customLegend = wrapper.querySelector('.custom-legend');
                if (customLegend) customLegend.style.display = 'block';
                toggleBtn.classList.remove('active');
                var chart = echarts.getInstanceByDom(document.getElementById(chartId));
                if (chart) chart.resize();
            }} else {{
                tableDiv.classList.add('active');
                chartDiv.style.display = 'none';
                var customLegend = wrapper.querySelector('.custom-legend');
                if (customLegend) customLegend.style.display = 'none';
                toggleBtn.classList.add('active');

                var chart = echarts.getInstanceByDom(document.getElementById(chartId));
                if (chart) {{
                    var option = chart.getOption();
                    var titleText = '';
                    if (option.title && option.title[0] && option.title[0].text) {{
                        titleText = option.title[0].text;
                    }}

                    var titleHtml = titleText ? '<div class="table-title">' + titleText + '</div>' : '';

                    if (option.series && option.series[0] && option.series[0].type === 'pie') {{
                        var pieData = option.series[0].data;
                        if (!pieData || pieData.length === 0) {{
                            tableDiv.innerHTML = '<div class="table-title">暂无数据</div>';
                            return;
                        }}
                        var total = 0;
                        pieData.forEach(function(item) {{
                            var val = (typeof item === 'object') ? (item.value || 0) : (Array.isArray(item) ? item[1] : 0);
                            total += val;
                        }});

                        var headers = '<tr><th>' + config.categoryCol + '</th><th>数量</th>';
                        if (config.hasPercent) headers += '<th>占比</th>';
                        headers += '</tr>';

                        var html = titleHtml + '<div class="table-body"><table class="data-table"><thead>' + headers + '</thead><tbody>';
                        pieData.forEach(function(item) {{
                            var name = (typeof item === 'object') ? item.name : (Array.isArray(item) ? item[0] : item);
                            var val = (typeof item === 'object') ? (item.value || 0) : (Array.isArray(item) ? item[1] : 0);
                            html += '<tr><td>' + name + '</td><td>' + val + '</td>';
                            if (config.hasPercent) {{
                                var percent = (val / total * 100).toFixed(1);
                                html += '<td>' + percent + '%</td>';
                            }}
                            html += '</tr>';
                        }});
                        html += '</tbody></table></div>';
                        tableDiv.innerHTML = html;
                    }} else {{
                        var categories = [];
                        var isHorizontal = option.yAxis && option.yAxis[0] && option.yAxis[0].data && option.yAxis[0].data.length > 0;

                        if (isHorizontal) {{
                            categories = option.yAxis[0].data;
                        }} else if (option.xAxis && option.xAxis[0] && option.xAxis[0].data) {{
                            categories = option.xAxis[0].data;
                        }}

                        var seriesCount = option.series.length;
                        var isMultiSeries = seriesCount > 1;

                        if (isMultiSeries) {{
                            var headers = '<tr><th>' + config.categoryCol + '</th>';
                            option.series.forEach(function(s) {{
                                if (s.name) headers += '<th>' + s.name + '</th>';
                            }});
                            headers += '</tr>';

                            var html = titleHtml + '<div class="table-body"><table class="data-table"><thead>' + headers + '</thead><tbody>';

                            for (var i = 0; i < categories.length; i++) {{
                                html += '<tr><td>' + categories[i] + '</td>';
                                option.series.forEach(function(s) {{
                                    var val = s.data[i];
                                    var displayVal;
                                    if (typeof val === 'object' && val !== null) {{
                                        displayVal = val.value !== undefined ? val.value : (Array.isArray(val) ? val[1] : val);
                                    }} else {{
                                        displayVal = val;
                                    }}
                                    if (s.name && s.name.indexOf('修复时长') !== -1 && typeof displayVal === 'number') {{
                                        html += '<td>' + displayVal.toFixed(2) + '</td>';
                                    }} else {{
                                        html += '<td>' + (displayVal !== undefined && displayVal !== null ? displayVal : 0) + '</td>';
                                    }}
                                }});
                                html += '</tr>';
                            }}
                            html += '</tbody></table></div>';
                            tableDiv.innerHTML = html;
                        }} else {{
                            var values = [];
                            if (option.series[0] && option.series[0].data) {{
                                option.series[0].data.forEach(function(v) {{
                                    if (typeof v === 'object' && v !== null && v.value !== undefined) {{
                                        values.push(v.value);
                                    }} else {{
                                        values.push(v);
                                    }}
                                }});
                            }}

                            var headers = '<tr><th>' + config.categoryCol + '</th><th>数量</th></tr>';
                            var html = titleHtml + '<div class="table-body"><table class="data-table"><thead>' + headers + '</thead><tbody>';
                            for (var i = 0; i < categories.length; i++) {{
                                html += '<tr><td>' + categories[i] + '</td><td>' + (values[i] || 0) + '</td></tr>';
                            }}
                            html += '</tbody></table></div>';
                            tableDiv.innerHTML = html;
                        }}
                    }}
                }}
            }}
        }}

        function enlargeChart(chartId) {{
            var modal = document.getElementById('modalOverlay');
            var modalChartDiv = document.getElementById('modalChart');

            var originalChart = echarts.getInstanceByDom(document.getElementById(chartId));
            if (!originalChart) return;

            modal.classList.add('active');

            var modalChart = echarts.init(modalChartDiv);
            var option = originalChart.getOption();
            modalChart.setOption(option);
        }}

        function closeModal(event) {{
            if (event && event.target !== document.getElementById('modalOverlay')) return;
            var modal = document.getElementById('modalOverlay');
            modal.classList.remove('active');
            var modalChart = echarts.getInstanceByDom(document.getElementById('modalChart'));
            if (modalChart) modalChart.dispose();
        }}

        function switchView(view) {{
            var homeView = document.getElementById('homeView');
            var chartView = document.getElementById('chartView');
            var detailView = document.getElementById('detailView');
            var btns = document.querySelectorAll('.view-btn');
            btns.forEach(function(btn) {{
                btn.classList.remove('active');
                if (btn.dataset.view === view) btn.classList.add('active');
            }});
            if (view === 'home') {{
                homeView.style.display = 'block';
                chartView.style.display = 'none';
                detailView.style.display = 'none';
            }} else if (view === 'chart') {{
                homeView.style.display = 'none';
                chartView.style.display = 'block';
                detailView.style.display = 'none';
                setTimeout(function() {{
                    document.querySelectorAll('div[id^=\"chart_\"]').forEach(function(chartDiv) {{
                        var chart = echarts.getInstanceByDom(chartDiv);
                        if (chart) chart.resize();
                    }});
                }}, 100);
            }} else {{
                homeView.style.display = 'none';
                chartView.style.display = 'none';
                detailView.style.display = 'block';
            }}
        }}
        var _screenshotBlob = null;

        function screenshotReport() {{
            var loading = document.getElementById('screenshotLoading');
            loading.classList.add('active');

            // 使用 dom-to-image-more 截取整个 body，完美保留 CSS 渐变
            domtoimage.toBlob(document.body, {{
                scale: 2,
                width: document.documentElement.offsetWidth,
                height: document.documentElement.scrollHeight,
                style: {{
                    overflow: 'visible'
                }},
                filter: function(node) {{
                    // 过滤掉遮罩层，不参与截图
                    if (node.id === 'screenshotLoading' ||
                        node.id === 'screenshotModal' ||
                        node.id === 'modalOverlay') {{
                        return false;
                    }}
                    return true;
                }}
            }}).then(function(blob) {{
                loading.classList.remove('active');
                _screenshotBlob = blob;
                var url = URL.createObjectURL(blob);
                document.getElementById('screenshotPreviewImg').src = url;
                document.getElementById('screenshotModal').classList.add('active');
            }}).catch(function(err) {{
                loading.classList.remove('active');
                console.error('截图失败:', err);
                alert('截图失败，请重试');
            }});
        }}

        function saveScreenshot() {{
            if (!_screenshotBlob) return;
            var now = new Date();
            var ts = now.getFullYear() + '' + String(now.getMonth()+1).padStart(2,'0') + String(now.getDate()).padStart(2,'0') + '_' + String(now.getHours()).padStart(2,'0') + String(now.getMinutes()).padStart(2,'0');
            var defaultName = 'report_screenshot_' + ts + '.png';

            // 使用 File System Access API 选择保存位置
            if ('showSaveFilePicker' in window) {{
                var writableStream = null;
                showSaveFilePicker({{
                    suggestedName: defaultName,
                    types: [ {{
                        description: 'PNG 图片',
                        accept: {{ 'image/png': ['.png'] }}
                    }} ]
                }}).then(function(handle) {{
                    return handle.createWritable();
                }}).then(function(writable) {{
                    writableStream = writable;
                    return writable.write(_screenshotBlob);
                }}).then(function() {{
                    return writableStream.close();
                }}).then(function() {{
                    var btn = document.querySelector('.btn-save');
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="#2ECC71"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg> 已保存';
                    btn.style.background = 'linear-gradient(135deg, #2ECC71, #27AE60)';
                    setTimeout(function() {{
                        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM15 3v2h3.59l-9.83 9.83 1.41 1.41L20 6.41V10h2V3h-7z"/></svg> 保存';
                        btn.style.background = 'linear-gradient(135deg, #1C91FD, #1677FF)';
                    }}, 2000);
                }}).catch(function(err) {{
                    if (err.name !== 'AbortError') {{
                        console.error('保存失败:', err);
                        alert('保存失败，请重试');
                    }}
                }});
            }} else {{
                // 降级为传统下载方式
                var url = URL.createObjectURL(_screenshotBlob);
                var a = document.createElement('a');
                a.href = url;
                a.download = defaultName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }}
        }}

        function copyToClipboard() {{
            if (!_screenshotBlob) return;
            var btn = document.querySelector('.btn-clipboard');
            if (navigator.clipboard && navigator.clipboard.write) {{
                var item = new ClipboardItem({{ 'image/png': _screenshotBlob }});
                navigator.clipboard.write([item]).then(function() {{
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="#2ECC71"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg> 已复制';
                    btn.style.color = '#2ECC71';
                    btn.style.borderColor = '#2ECC71';
                    setTimeout(function() {{
                        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg> 复制到剪贴板';
                        btn.style.color = '';
                        btn.style.borderColor = '';
                    }}, 2000);
                }}).catch(function(err) {{
                    console.error('复制失败:', err);
                    alert('复制失败，浏览器可能不支持此功能');
                }});
            }} else {{
                alert('当前浏览器不支持复制图片到剪贴板，请使用下载功能');
            }}
        }}

        function closeScreenshotModal(event) {{
            if (event && event.target !== document.getElementById('screenshotModal')) return;
            document.getElementById('screenshotModal').classList.remove('active');
            var img = document.getElementById('screenshotPreviewImg');
            if (img.src) {{
                URL.revokeObjectURL(img.src);
                img.src = '';
            }}
            _screenshotBlob = null;
        }}
        {get_home_view_js()}
    </script>
</body>
</html>'''


def save_report(html_content):
    """保存HTML报告到文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
