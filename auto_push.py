# -*- coding: utf-8 -*-
"""
自动推送脚本
推送到 GitHub，自动部署到 GitHub Pages
"""

import subprocess
import sys

# GitHub 远程仓库配置
REMOTE = {
    'name': 'GitHub',
    'key': 'github',
    'url': 'https://github.com/pionkucc/PSOTWeeklyReport.git',
    'pipeline_url': 'https://github.com/pionkucc/PSOTWeeklyReport/actions',
    'pages_url': 'https://pionkucc.github.io/PSOTWeeklyReport/PSOT_Weekly_Report.html'
}

def run_command(cmd, description):
    """运行命令并打印结果"""
    print(f"\n[执行] {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return False
    print(f"[成功] {result.stdout.strip() if result.stdout.strip() else '完成'}")
    return True

def setup_remote():
    """配置远程仓库"""
    print("\n[配置] 检查远程仓库...")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    current_remotes = result.stdout

    if REMOTE['key'] not in current_remotes:
        print(f"[新增] 添加远程仓库: {REMOTE['key']} -> {REMOTE['url']}")
        subprocess.run(f"git remote add {REMOTE['key']} {REMOTE['url']}", shell=True)
    else:
        print(f"[已存在] 远程仓库: {REMOTE['key']}")

    # 移除gitlab远程仓库（如果存在）
    if 'gitlab' in current_remotes:
        print("[清理] 移除GitLab远程仓库...")
        subprocess.run("git remote remove gitlab", shell=True)

def main():
    print("=" * 50)
    print("PSOT Weekly Report 自动推送脚本")
    print("=" * 50)

    # 1. 生成报告
    print("\n[步骤1] 生成HTML报告...")
    if not run_command("python defect_quality_report.py", "运行报告生成脚本"):
        sys.exit(1)

    # 2. 检查是否有变更
    print("\n[步骤2] 检查文件变更...")
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    changes = result.stdout.strip()

    if not changes:
        print("[提示] 没有文件变更，无需推送")
        sys.exit(0)

    print(f"[发现] 变更文件:\n{changes}")

    # 3. 添加所有变更（排除auto_push.py自身）
    print("\n[步骤3] 添加文件到暂存区...")
    if not run_command("git add . && git reset HEAD auto_push.py", "git add"):
        sys.exit(1)

    # 4. 提交
    print("\n[步骤4] 创建提交...")

    # 获取变更的HTML文件名
    html_files = [line.split()[-1] for line in changes.split('\n') if '.html' in line]

    if html_files:
        commit_msg = f"更新报告: {', '.join(html_files)}"
    else:
        commit_msg = "更新数据和配置"

    if not run_command(f'git commit -m "{commit_msg}"', "git commit"):
        sys.exit(1)

    # 5. 配置远程仓库
    setup_remote()

    # 6. 推送到GitHub
    print(f"\n{'=' * 50}")
    print(f"[推送] 推送到 {REMOTE['name']}...")
    print(f"{'=' * 50}")

    if not run_command(f"git push {REMOTE['key']} main", f"git push {REMOTE['key']}"):
        sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"[全部完成] 推送成功！")
    print(f"[CI/CD] {REMOTE['pipeline_url']}")
    print(f"[Pages] {REMOTE['pages_url']}")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
