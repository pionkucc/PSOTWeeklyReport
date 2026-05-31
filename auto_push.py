# -*- coding: utf-8 -*-
"""
自动推送脚本（双平台版）
支持推送到 GitHub 和 GitLab（极狐）
"""

import subprocess
import sys
import os

# 远程仓库配置
REMOTES = {
    'github': {
        'name': 'GitHub',
        'url': 'https://github.com/pionkucc/PSOTWeeklyReport.git',
        'pipeline_url': 'https://github.com/pionkucc/PSOTWeeklyReport/actions',
        'pages_url': 'https://pionkucc.github.io/PSOTWeeklyReport'
    },
    'gitlab': {
        'name': 'GitLab（极狐）',
        'url': 'https://jihulab.com/psot-qc/weekly-report-project.git',
        'pipeline_url': 'https://jihulab.com/psot-qc/weekly-report-project/-/pipelines',
        'pages_url': 'https://psot-qc.pages.jihulab.com/weekly-report-project'
    }
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

def setup_remotes():
    """配置远程仓库"""
    print("\n[配置] 检查远程仓库...")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    current_remotes = result.stdout

    for key, config in REMOTES.items():
        if key not in current_remotes:
            print(f"[新增] 添加远程仓库: {key} -> {config['url']}")
            subprocess.run(f"git remote add {key} {config['url']}", shell=True)
        else:
            print(f"[已存在] 远程仓库: {key}")

def push_to_remote(remote_key):
    """推送到指定远程仓库"""
    config = REMOTES[remote_key]
    print(f"\n{'=' * 50}")
    print(f"[推送] 推送到 {config['name']}...")
    print(f"{'=' * 50}")

    if not run_command(f"git push {remote_key}", f"git push {remote_key}"):
        return False

    print(f"\n[完成] {config['name']} 推送成功！")
    print(f"[CI/CD] {config['pipeline_url']}")
    print(f"[Pages] {config['pages_url']}")
    return True

def main():
    print("=" * 50)
    print("PSOT Weekly Report 自动推送脚本")
    print("（双平台版：GitHub + GitLab）")
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
    setup_remotes()

    # 6. 选择推送平台
    print("\n" + "=" * 50)
    print("[选择] 请选择推送平台:")
    print("  1 - 仅推送到 GitHub")
    print("  2 - 仅推送到 GitLab（极狐）")
    print("  3 - 同时推送到 GitHub 和 GitLab")
    print("=" * 50)

    choice = input("请输入选项 (1/2/3，默认为1): ").strip() or '1'

    success = True
    if choice == '1':
        success = push_to_remote('github')
    elif choice == '2':
        success = push_to_remote('gitlab')
    elif choice == '3':
        success_github = push_to_remote('github')
        success_gitlab = push_to_remote('gitlab')
        success = success_github and success_gitlab
    else:
        print("[错误] 无效选项，默认推送到 GitHub")
        success = push_to_remote('github')

    if not success:
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[全部完成] 推送成功！")
    print("=" * 50)

if __name__ == "__main__":
    main()
