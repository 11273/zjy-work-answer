import logging
import tkinter as tk
import webbrowser
from tkinter import messagebox

import requests


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
REPO = "11273/zjy-work-answer"


def version_greater_than(v1, v2):
    # 去除版本号中的前缀 'v'
    v1_parts = map(int, v1.lstrip('v').split('.'))
    v2_parts = map(int, v2.lstrip('v').split('.'))

    # 使用 zip_longest 以确保处理不同长度的版本号
    from itertools import zip_longest
    for v1_part, v2_part in zip_longest(v1_parts, v2_parts, fillvalue=0):
        if v1_part > v2_part:
            return True
        elif v1_part < v2_part:
            return False

    return False


def get_latest_release(repo):
    """从 GitHub API 获取最新发布信息。"""
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.warning(f"获取发布信息时出错: {e}")
        return None


def open_download_url(asset_url):
    """打开默认浏览器以下载新版本。"""
    webbrowser.open(asset_url)
    logger.debug(f"浏览器已打开: {asset_url}。")


def show_update_prompt(asset_url):
    """显示更新提示弹窗。"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    if messagebox.askyesno("更新可用", "检测到新版本，是否下载？"):
        open_download_url(asset_url)

    root.destroy()


def check_for_updates(app_version):
    if app_version == 'dev':
        logger.debug("开发环境，不检查更新。")
        return

    logger.info("检查更新中，请稍后...")
    release_info = get_latest_release(REPO)
    if not release_info:
        return

    latest_version = release_info['tag_name']
    asset_html_url = release_info['html_url']

    if version_greater_than(latest_version, app_version):
        show_update_prompt(asset_html_url)
    else:
        logger.info("当前已是最新版本。")