# -*- coding: utf-8 -*-
"""
自动推送脚本
一键生成报告并推送到GitHub
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并打印结果"""
    print(f"\n[执行] {description}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[错误] {result.stderr}")
        return False
    print(f"[成功] {result.stdout.strip() if result.stdout.strip() else '完成'}")
    return True

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

    # 3. 添加所有变更
    print("\n[步骤3] 添加文件到暂存区...")
    if not run_command("git add .", "git add"):
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

    # 5. 推送
    print("\n[步骤5] 推送到GitHub...")
    if not run_command("git push", "git push"):
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[完成] 推送成功！")
    print("GitHub Actions 将自动部署，几分钟后可访问:")
    print("https://github.com/pionkucc/PSOTWeeklyReport/actions")
    print("=" * 50)

if __name__ == "__main__":
    main()