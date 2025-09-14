# -*- coding: utf-8 -*-
# @Time : 2022/3/31 9:34
# @Author : Melon
# @Site :
# @Note :
# @File : init_zjy.py
# @Software: PyCharm
import logging
import time

import requests
from ZJYMain.oauth_login import oauth_login

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://sso.icve.com.cn/prod-api"

# 登录
LOGIN_SYSTEM_URL = BASE_URL + "/data/userLoginV2"
# 获取access_token
GET_TOKEN = "https://zjy2.icve.com.cn/prod-api/auth/passLogin"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
}

session = requests.session()


def login(username, password, img_code=None):  # 0.登录
    data = {"userName": username, "password": password, "type": 1}
    if img_code:
        data["imgCode"] = img_code
    post = session.post(url=LOGIN_SYSTEM_URL, json=data, headers=HEADERS)
    post_json = post.json()
    if post.ok and post_json["code"] == 200:
        logger.info(f"登录成功: {username}")
        token = post_json["data"]["token"]
        post = session.get(url=GET_TOKEN, params={"token": token}, headers=HEADERS)
        token_json = post.json()
        access_token = token_json["data"]["access_token"]
        session.access_token = access_token
        session.headers["Authorization"] = f"Bearer {access_token}"
        return session
    else:
        logger.info(f"登录失败: {username} msg: {post_json['msg']}")
        input("程序结束，如遇错误请重新运行，多次重复错误请提交Github...")


def login_with_oauth(timeout=300, preferred_port=None):
    """
    使用OAuth方式登录

    Args:
        timeout: 超时时间（秒）
        preferred_port: 首选端口，如果为None则随机选择

    Returns:
        成功返回session对象，失败返回None
    """
    logger.info("🔐 开始OAuth登录流程...")

    # 获取OAuth token
    token = oauth_login(timeout, preferred_port)

    if not token:
        logger.error("❌ OAuth登录失败")
        return None

    # 使用token获取access_token
    try:
        post = session.get(url=GET_TOKEN, params={"token": token}, headers=HEADERS)
        token_json = post.json()

        if post.ok and token_json.get("code") == 200:
            access_token = token_json["data"]["access_token"]
            session.access_token = access_token
            session.headers["Authorization"] = f"Bearer {access_token}"
            logger.info("✅ OAuth登录成功")
            return session
        else:
            logger.error(f"❌ 获取access_token失败: {token_json}")
            return None

    except Exception as e:
        logger.error(f"❌ OAuth登录过程中发生异常: {e}")
        return None


def login_interactive():
    """
    交互式登录，支持用户选择登录方式

    Returns:
        成功返回session对象，失败返回None
    """
    logger.info("=" * 60)
    logger.info("🚀 ZJY助手登录服务")
    logger.info("=" * 60)
    logger.info("请选择登录方式：")
    logger.info("1. 用户名密码登录（传统方式）")
    logger.info("2. OAuth浏览器登录（推荐）")
    logger.info("=" * 60)

    while True:
        choice = input("请输入选择 (1/2): ").strip()

        if choice == "1":
            # 传统登录
            username = input("请输入用户名: ").strip()
            password = input("请输入密码: ").strip()
            return login(username, password)

        elif choice == "2":
            # OAuth登录
            return login_with_oauth()

        else:
            logger.warning("⚠️ 无效选择，请输入 1 或 2")
            continue
