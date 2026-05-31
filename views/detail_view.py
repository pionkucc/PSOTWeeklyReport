"""
明细视图模块
包含缺陷明细列表和弹窗详情功能，使用 Vue3 + Element Plus 日期组件
"""

import json
import pandas as pd


def create_detail_view_html(df, total):
    """创建缺陷明细视图HTML（筛选导航栏 + 数据表格）"""
    # 定义表格展示列及中文名
    display_cols = {
        '缺陷编号': '缺陷编号',
        '缺陷状态': '缺陷状态',
        '缺陷摘要': '缺陷摘要',
        '优先级': '优先级',
        '严重程度': '严重程度',
        '处理人员': '处理人员',
        '缺陷修复周期(天)': '修复周期(天)'
    }

    # 定义弹窗明细列及中文名
    detail_cols = {
        '缺陷编号': '缺陷编号',
        '缺陷状态': '缺陷状态',
        '缺陷摘要': '缺陷摘要',
        '优先级': '优先级',
        '严重程度': '严重程度',
        '处理人员': '处理人员',
        '发现阶段': '发现阶段',
        '引入阶段': '引入阶段',
        '引入原因': '引入原因',
        '缺陷来源': '缺陷来源',
        '缺陷类型': '缺陷类型',
        df.columns[9]: '登记人',
        df.columns[11]: '登记时间',
        df.columns[12]: '修改时间',
        df.columns[13]: '关闭时间',
        '缺陷修复周期(天)': '修复周期(天)',
        '缺陷关闭周期(天)': '关闭周期(天)'
    }

    # 时间列名
    register_time_col = df.columns[11]  # 登记时间
    modify_time_col = df.columns[12]    # 修改时间（修复时间）
    close_time_col = df.columns[13]     # 关闭时间

    # 获取筛选器选项
    status_options = sorted(df['缺陷状态'].dropna().unique().tolist())
    handler_options = sorted(df['处理人员'].dropna().unique().tolist())
    priority_options = ['低', '中', '高', '优先']
    stage_options = sorted(df['发现阶段'].dropna().unique().tolist())
    type_options = sorted(df['缺陷类型'].dropna().unique().tolist())

    # 按登记时间倒序排列
    df_sorted = df.sort_values(by=register_time_col, ascending=False)

    # 筛选需要的列：展示列 + 筛选器需要的额外列
    filter_cols = ['发现阶段', '缺陷类型']
    all_row_cols = list(display_cols.keys()) + [c for c in filter_cols if c not in display_cols]

    # 生成表格行数据（包含筛选字段）
    table_data = df_sorted[all_row_cols].fillna('')
    rows_json = table_data.to_dict(orient='records')

    # 生成三种日期列表（用于日期筛选）
    def format_date_list(col):
        dates = df_sorted[col].fillna('')
        return [str(pd.to_datetime(d, errors='coerce').strftime('%Y-%m-%d')) if pd.notna(d) and d != '' else '' for d in dates]

    register_dates = format_date_list(register_time_col)
    modify_dates = format_date_list(modify_time_col)
    close_dates = format_date_list(close_time_col)

    # 获取各日期范围
    def get_date_range(date_list):
        valid_dates = [d for d in date_list if d]
        return [min(valid_dates), max(valid_dates)] if valid_dates else ['', '']

    register_range = get_date_range(register_dates)
    modify_range = get_date_range(modify_dates)
    close_range = get_date_range(close_dates)

    # 生成完整明细数据
    detail_data = df_sorted[list(detail_cols.keys())].fillna('')
    detail_rows_json = detail_data.to_dict(orient='records')

    # 转为JS格式
    rows_js = json.dumps(rows_json, ensure_ascii=False, default=str)
    detail_rows_js = json.dumps(detail_rows_json, ensure_ascii=False, default=str)
    register_dates_js = json.dumps(register_dates, ensure_ascii=False)
    modify_dates_js = json.dumps(modify_dates, ensure_ascii=False)
    close_dates_js = json.dumps(close_dates, ensure_ascii=False)

    col_keys = list(display_cols.keys())
    col_names = list(display_cols.values())
    detail_col_names = list(detail_cols.values())

    # 构建 Vue 模板字符串（不用 f-string，直接拼接避免花括号问题）
    vue_template = '''
<div id="detailVueApp">
    <div class="filter-bar" :class="{ 'filter-collapsed': filterCollapsed }">
        <div class="filter-row">
            <div class="filter-group">
                <span class="filter-label">状态</span>
                <el-select v-model="filters.status" placeholder="全部" clearable size="small" style="width: 100px" @change="onFilterChange">
                    <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <span class="filter-label">处理人员</span>
                <el-select v-model="filters.handler" placeholder="全部" clearable size="small" style="width: 120px" @change="onFilterChange">
                    <el-option v-for="h in handlerOptions" :key="h" :label="h" :value="h"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <span class="filter-label">优先级</span>
                <el-select v-model="filters.priority" placeholder="全部" clearable size="small" style="width: 80px" @change="onFilterChange">
                    <el-option v-for="p in priorityOptions" :key="p" :label="p" :value="p"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <span class="filter-label">发现阶段</span>
                <el-select v-model="filters.stage" placeholder="全部" clearable size="small" style="width: 160px" @change="onFilterChange">
                    <el-option v-for="st in stageOptions" :key="st" :label="st" :value="st"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <span class="filter-label">缺陷类型</span>
                <el-select v-model="filters.defectType" placeholder="全部" clearable size="small" style="width: 120px" @change="onFilterChange">
                    <el-option v-for="t in typeOptions" :key="t" :label="t" :value="t"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <span class="filter-label">日期</span>
                <el-select v-model="filters.dateType" size="small" style="width: 90px" @change="onDateTypeChange">
                    <el-option label="登记时间" value="register"></el-option>
                    <el-option label="修复时间" value="modify"></el-option>
                    <el-option label="关闭时间" value="close"></el-option>
                </el-select>
            </div>
            <div class="filter-group">
                <el-date-picker
                    v-model="filters.dateRange"
                    type="daterange"
                    range-separator="~"
                    start-placeholder="开始"
                    end-placeholder="结束"
                    value-format="YYYY-MM-DD"
                    size="small"
                    style="width: 210px"
                    @change="onFilterChange"
                ></el-date-picker>
            </div>
            <el-button size="small" style="border-color: #1C91FD; color: #1C91FD; background: #fff;" @click="resetFilters">重置</el-button>
        </div>
        <div class="filter-row filter-row-extra">
            <span class="filter-stats">共 {{ filteredCount }} 条</span>
            <el-button type="text" size="small" class="filter-toggle" @click="toggleFilter">
                {{ filterCollapsed ? '展开' : '收起' }}
                <span :class="filterCollapsed ? 'arrow-down' : 'arrow-up'"></span>
            </el-button>
        </div>
    </div>

    <div class="detail-table-container">
        <table class="detail-table">
            <thead>
                <tr>
''' + ''.join([f'                    <th class="col-{i}">{name}</th>\n' for i, name in enumerate(col_names)]) + '''
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, idx) in filteredData" :key="idx" @dblclick="showDetail(filteredIndices[idx])">
                    <td v-for="(key, colIdx) in colKeys" :key="colIdx" :class="key === \'缺陷摘要\' ? \'summary-cell\' : \'\'">
                        <span v-if="key === \'缺陷状态\'" :class="\'status-tag status-\' + row[key]">{{ row[key] }}</span>
                        <span v-else-if="key === \'优先级\'" :class="getPriorityClass(row[key])">{{ row[key] }}</span>
                        <span v-else>{{ row[key] }}</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <el-dialog v-model="modalVisible" title="缺陷明细" width="600px" :close-on-click-modal="true" destroy-on-close>
        <div class="modal-body">
            <div v-for="(key, i) in detailKeys" :key="i" class="detail-item">
                <div class="detail-label">{{ detailColNames[i] }}</div>
                <div class="detail-value">
                    <span v-if="key === \'缺陷状态\'" :class="\'status-tag status-\' + detailData[key]">{{ detailData[key] || \'--\' }}</span>
                    <span v-else-if="key === \'优先级\'" :class="getPriorityClass(detailData[key])">{{ detailData[key] || \'--\' }}</span>
                    <span v-else>{{ detailData[key] || \'--\' }}</span>
                </div>
            </div>
        </div>
    </el-dialog>
</div>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/element-plus/dist/index.css">
<style>
    /* Element Plus 样式隔离 - 只在 detailVueApp 内生效 */
    #detailVueApp .filter-bar { background: #fff; border-radius: 12px; padding: 12px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    #detailVueApp .filter-row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
    #detailVueApp .filter-row-extra { margin-top: 10px; justify-content: space-between; padding-top: 10px; border-top: 1px dashed #eee; }
    #detailVueApp .filter-group { display: flex; align-items: center; gap: 6px; }
    #detailVueApp .filter-label { font-family: \'Microsoft YaHei\'; font-size: 13px; color: #555; white-space: nowrap; }
    #detailVueApp .filter-stats { font-family: \'Microsoft YaHei\'; font-size: 13px; color: #1C91FD; }
    #detailVueApp .filter-toggle { font-family: \'Microsoft YaHei\'; font-size: 12px; color: #999; padding: 0; }
    #detailVueApp .filter-toggle:hover { color: #1C91FD; }
    #detailVueApp .arrow-up, #detailVueApp .arrow-down { display: inline-block; width: 0; height: 0; margin-left: 4px; vertical-align: middle; }
    #detailVueApp .arrow-up { border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid currentColor; }
    #detailVueApp .arrow-down { border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid currentColor; }
    #detailVueApp .filter-collapsed .filter-row:not(.filter-row-extra) { max-height: 0; overflow: hidden; margin: 0; padding: 0; }
    #detailVueApp .filter-collapsed .filter-row-extra { margin-top: 0; padding-top: 0; border-top: none; }
    #detailVueApp .detail-table-container { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow-x: auto; }
    #detailVueApp .detail-table { width: 100%; border-collapse: collapse; font-family: \'Microsoft YaHei\'; font-size: 13px; }
    #detailVueApp .detail-table th { background: #f5f5f5; color: #666; padding: 12px 10px; text-align: left; font-weight: normal; white-space: nowrap; border-bottom: 1px solid #eee; }
    #detailVueApp .detail-table th:first-child { border-radius: 8px 0 0 0; }
    #detailVueApp .detail-table th:last-child { border-radius: 0 8px 0 0; }
    #detailVueApp .detail-table tbody tr { transition: all 0.15s; cursor: pointer; }
    #detailVueApp .detail-table tbody tr:hover { background: #fafafa; transform: scale(1.01); }
    #detailVueApp .detail-table td { padding: 10px; border-bottom: 1px solid #f0f0f0; color: #444; }
    #detailVueApp .detail-table tbody tr:last-child td { border-bottom: none; }
    #detailVueApp .detail-table .col-0 { width: 130px; color: #1C91FD; }
    #detailVueApp .detail-table .col-1 { width: 80px; }
    #detailVueApp .detail-table .col-2 { min-width: 180px; }
    #detailVueApp .detail-table .col-3 { width: 60px; }
    #detailVueApp .detail-table .col-4 { width: 70px; }
    #detailVueApp .detail-table .col-5 { width: 90px; }
    #detailVueApp .detail-table .col-6 { width: 80px; }
    #detailVueApp .detail-table td.summary-cell { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 250px; }
    #detailVueApp .detail-table td.summary-cell:hover { white-space: normal; word-break: break-all; background: #fff; box-shadow: 0 2px 8px rgba(170,150,218,0.2); z-index: 10; position: relative; border-radius: 4px; padding: 10px; }
    #detailVueApp .status-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    #detailVueApp .status-New { background: #FFF9C4; color: #F9A825; }
    #detailVueApp .status-Closed { background: #E8F5E9; color: #66BB6A; }
    #detailVueApp .status-Fixed { background: #E0F7FA; color: #4DD0E1; }
    #detailVueApp .status-Pending { background: #F3E5F5; color: #AB47BC; }
    #detailVueApp .status-ReOpen { background: #FFEBEE; color: #EF5350; }
    #detailVueApp .priority-high { color: #EF5350; }
    #detailVueApp .priority-medium { color: #FFA726; }
    #detailVueApp .priority-low { color: #1C91FD; }
    #detailVueApp .modal-body { padding: 10px 0; }
    #detailVueApp .detail-item { display: flex; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; background: #fff; transition: all 0.2s; }
    #detailVueApp .detail-item:hover { background: #fafafa; transform: translateX(6px); }
    #detailVueApp .detail-item:last-child { margin-bottom: 0; }
    #detailVueApp .detail-label { width: 90px; flex-shrink: 0; font-family: \'Microsoft YaHei\'; font-size: 13px; color: #1C91FD; font-weight: bold; }
    #detailVueApp .detail-value { flex: 1; font-family: \'Microsoft YaHei\'; font-size: 13px; color: #333; word-break: break-all; }
    /* el-dialog 毛玻璃背景 */
    .el-overlay { background: rgba(170,150,218,0.15) !important; backdrop-filter: blur(8px) !important; }
    /* el-dialog 弹窗样式 */
    .el-dialog { border-radius: 16px !important; box-shadow: 0 12px 40px rgba(170,150,218,0.25) !important; animation: dialogPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important; }
    @keyframes dialogPop { from { transform: scale(0.8) translateY(-30px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
    .el-dialog__header { background: #f8f9fa !important; border-radius: 16px 16px 0 0 !important; padding: 16px 20px !important; border-bottom: 1px solid #eee !important; display: flex !important; align-items: center !important; justify-content: space-between !important; }
    .el-dialog__title { font-family: \'Microsoft YaHei\' !important; color: #1C91FD !important; font-size: 16px !important; }
    .el-dialog__headerbtn { position: relative !important; top: 0 !important; right: 0 !important; width: 32px !important; height: 32px !important; background: #fff !important; border: 1px solid #eee !important; border-radius: 50% !important; transition: all 0.3s !important; display: flex !important; align-items: center !important; justify-content: center !important; }
    .el-dialog__headerbtn:hover { transform: rotate(90deg); background: #1C91FD !important; border-color: #1C91FD !important; }
    .el-dialog__headerbtn .el-dialog__close { color: #1C91FD !important; font-size: 16px !important; }
    .el-dialog__headerbtn:hover .el-dialog__close { color: #fff !important; }
    .el-dialog__body { padding: 20px !important; max-height: 60vh !important; overflow-y: auto !important; }
    .el-dialog__body::-webkit-scrollbar { width: 4px; }
    .el-dialog__body::-webkit-scrollbar-thumb { background: #1C91FD; border-radius: 2px; }
</style>

<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/element-plus"></script>
<script>
(function() {
    var appData = {
        allData: ''' + rows_js + ''',
        allDetailData: ''' + detail_rows_js + ''',
        colKeys: ''' + json.dumps(col_keys, ensure_ascii=False) + ''',
        detailColNames: ''' + json.dumps(detail_col_names, ensure_ascii=False) + ''',
        registerDates: ''' + register_dates_js + ''',
        modifyDates: ''' + modify_dates_js + ''',
        closeDates: ''' + close_dates_js + ''',
        statusOptions: ''' + json.dumps(status_options, ensure_ascii=False) + ''',
        handlerOptions: ''' + json.dumps(handler_options, ensure_ascii=False) + ''',
        priorityOptions: ''' + json.dumps(priority_options, ensure_ascii=False) + ''',
        stageOptions: ''' + json.dumps(stage_options, ensure_ascii=False) + ''',
        typeOptions: ''' + json.dumps(type_options, ensure_ascii=False) + ''',
        registerRange: ''' + json.dumps(register_range, ensure_ascii=False) + ''',
        modifyRange: ''' + json.dumps(modify_range, ensure_ascii=False) + ''',
        closeRange: ''' + json.dumps(close_range, ensure_ascii=False) + '''
    };

    var detailVueApp = Vue.createApp({
        data() {
            return {
                filters: {
                    status: '',
                    handler: '',
                    priority: '',
                    stage: '',
                    defectType: '',
                    dateType: 'register',
                    dateRange: appData.registerRange
                },
                modalVisible: false,
                detailData: {},
                filterCollapsed: true
            };
        },
        computed: {
            filteredData() {
                var result = [];
                var indices = [];
                for (var idx = 0; idx < appData.allData.length; idx++) {
                    var row = appData.allData[idx];
                    if (this.filters.status && row['缺陷状态'] !== this.filters.status) continue;
                    if (this.filters.handler && row['处理人员'] !== this.filters.handler) continue;
                    if (this.filters.priority && row['优先级'] !== this.filters.priority) continue;
                    if (this.filters.stage && row['发现阶段'] !== this.filters.stage) continue;
                    if (this.filters.defectType && row['缺陷类型'] !== this.filters.defectType) continue;

                    var dateList;
                    if (this.filters.dateType === 'register') {
                        dateList = appData.registerDates;
                    } else if (this.filters.dateType === 'modify') {
                        dateList = appData.modifyDates;
                    } else {
                        dateList = appData.closeDates;
                    }

                    var dateVal = dateList[idx];
                    if (this.filters.dateRange && this.filters.dateRange.length === 2) {
                        if (dateVal && (dateVal < this.filters.dateRange[0] || dateVal > this.filters.dateRange[1])) continue;
                    }

                    result.push(row);
                    indices.push(idx);
                }
                this._filteredIndices = indices;
                return result;
            },
            filteredIndices() {
                return this._filteredIndices || [];
            },
            filteredCount() {
                return this.filteredData.length;
            },
            detailKeys() {
                return Object.keys(appData.allDetailData[0] || {});
            },
            colKeys() { return appData.colKeys; },
            detailColNames() { return appData.detailColNames; },
            statusOptions() { return appData.statusOptions; },
            handlerOptions() { return appData.handlerOptions; },
            priorityOptions() { return appData.priorityOptions; },
            stageOptions() { return appData.stageOptions; },
            typeOptions() { return appData.typeOptions; }
        },
        methods: {
            getPriorityClass(val) {
                if (val === '优先' || val === '高') return 'priority-high';
                if (val === '中') return 'priority-medium';
                return 'priority-low';
            },
            onFilterChange() {},
            onDateTypeChange() {
                if (this.filters.dateType === 'register') {
                    this.filters.dateRange = appData.registerRange;
                } else if (this.filters.dateType === 'modify') {
                    this.filters.dateRange = appData.modifyRange;
                } else {
                    this.filters.dateRange = appData.closeRange;
                }
            },
            resetFilters() {
                this.filters.status = '';
                this.filters.handler = '';
                this.filters.priority = '';
                this.filters.stage = '';
                this.filters.defectType = '';
                this.filters.dateType = 'register';
                this.filters.dateRange = appData.registerRange;
            },
            toggleFilter() {
                this.filterCollapsed = !this.filterCollapsed;
            },
            showDetail(idx) {
                this.detailData = appData.allDetailData[idx] || {};
                this.modalVisible = true;
            }
        }
    });

    detailVueApp.use(ElementPlus);
    detailVueApp.mount('#detailVueApp');
})();
</script>
'''

    return vue_template