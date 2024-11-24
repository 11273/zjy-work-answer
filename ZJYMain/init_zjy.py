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

from ZJYMain.verify import start_verify

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = 'https://sso.icve.com.cn/prod-api'

# 登录
LOGIN_SYSTEM_URL = BASE_URL + '/data/userLoginV2'
# 获取access_token
GET_TOKEN = 'https://zjy2.icve.com.cn/prod-api/auth/passLogin'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}

session = requests.session()


def login(username, password, img_code=None):  # 0.登录
    data = {
        "userName": username,
        "password": password,
        "type": 1
    }
    if img_code:
        data['imgCode'] = img_code
    post = session.post(url=LOGIN_SYSTEM_URL, json=data, headers=HEADERS)
    post_json = post.json()
    if post.ok and post_json['code'] == 200:
        logger.info(f"登录成功: {username}")
        token = post_json['data']['token']
        post = session.get(url=GET_TOKEN, params={'token': token}, headers=HEADERS)
        token_json = post.json()
        access_token = token_json['data']['access_token']
        session.access_token = access_token
        session.headers['Authorization'] = f'Bearer {access_token}'
        return session
    else:
        logger.info(f"登录失败: {username} msg: {post_json['msg']}")
        if post_json['code'] == 500 and "请滑动滑块验证码" in post_json['msg'] or "验证码验证失败" in post_json['msg']:
            data['imgCode'] = start_verify()
            return login(username, password, img_code=data['imgCode'])
        if post_json['code'] == 500 and "账号被锁定10分钟" in post_json['msg']:
            time.sleep(10 * 60)
            return login(username, password, img_code)
