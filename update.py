import logging
import webbrowser

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
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            logger.warning("获取更新过于频繁，请稍后重试。")
        else:
            logger.warning(f"HTTP error occurred: {e}")
        return None
    except requests.RequestException as e:
        logger.warning(f"获取发布信息时出错: {e.response}")
        return None


def open_download_url(asset_url):
    """打开默认浏览器以下载新版本。"""
    webbrowser.open(asset_url)
    logger.debug(f"浏览器已打开: {asset_url}。")


def _ask_for_update(asset_url):
    """
    询问用户是否下载新版本。

    tkinter 属于可选的 GUI 依赖，精简版 Python、无桌面环境的 Linux
    以及 Homebrew 默认安装的 Python 都不带它，因此延迟到使用时再导入，
    缺少 tkinter 时降级为命令行提示。

    :param asset_url: 新版本下载地址
    :return: 是否需要打开下载页面
    """
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        logger.warning("当前环境不支持图形界面，改为命令行提示。")
        logger.warning("新版本下载地址: %s", asset_url)
        try:
            answer = input("检测到新版本，是否前往下载？(y/N): ")
        except (EOFError, OSError):
            return False
        return answer.strip().lower() == "y"

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    try:
        return messagebox.askyesno("更新可用", "检测到新版本，是否前往下载？")
    finally:
        root.destroy()


def show_update_prompt(asset_url):
    """显示更新提示（有图形界面时弹窗，否则使用命令行）。"""
    if _ask_for_update(asset_url):
        open_download_url(asset_url)


def check_for_updates(app_version):
    try:
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
    except Exception as e:
        logger.exception("检查更新时出错: %s", e)
    finally:
        logger.info("更新检查完成。")
