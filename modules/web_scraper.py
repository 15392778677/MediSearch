'''
Date: 2024-10-13 16:53:30
LastEditors: yangyehan 1958944515@qq.com
LastEditTime: 2024-10-13 18:33:54
FilePath: /MediSearch/Users/mac/Documents/jingfangzhigu/jingfangzhigu_mutiple_agents-main/jingfangzhigu_1.0/MediSearch/modules/web_scraper.py
Description: 用于处理网页抓取任务的模块，增加了可复用性。
'''
import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup

class WebScraper:
    def fetch_and_parse_single_url(self, url: str) -> str:
        """
        获取单个 URL 的所有非 HTML 文本内容。

        参数：
        - url (str): 要获取的 URL。

        返回值：
        - str: URL 的所有非 HTML 文本内容。
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text(separator=' ', strip=True)
                return text_content
            else:
                return "加载内容失败。"
        except Exception as e:
            return f"加载内容时出错：{e}"
