import asyncio
import requests
from playwright.async_api import async_playwright

class MermaidToImageUploader:
    def __init__(self):
        pass

    async def render_mermaid(self, mermaid_code):
        # HTML 模板，包含 Mermaid 的初始化和错误处理
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <title>Mermaid Diagram</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <script>
                mermaid.parseError = function(err, hash) {{
                    document.body.innerHTML = '<div id="error">' + err + '</div>';
                }};
                mermaid.initialize({{ startOnLoad: true }});
            </script>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
        </body>
        </html>
        """

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html_content)

            # 等待 Mermaid 图表渲染完成
            try:
                await page.wait_for_selector('.mermaid > svg', timeout=5000)
            except Exception as e:
                # 检查是否有错误信息
                error_element = await page.query_selector('#error')
                if error_element:
                    error_text = await error_element.text_content()
                    print("Mermaid 语法错误:", error_text)
                    await browser.close()
                    return None, error_text
                else:
                    print("渲染过程中发生未知错误。")
                    await browser.close()
                    return None, "渲染过程中发生未知错误。"

            # 选择 Mermaid 元素
            element = await page.query_selector('.mermaid')

            # 截图并获取二进制数据
            image_data = await element.screenshot(type='png')

            await browser.close()

        return image_data, None

    async def upload_image(self, image_data):
        # 上传图片并获取在线链接
        upload_url = "https://wx.jfzgai.com/api/wx/file/post-image-no-auth"

        files = {
            'file': ('mermaid_diagram.png', image_data, 'image/png')
        }
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)'
        }

        response = requests.post(upload_url, headers=headers, files=files)
        # 打印服务器的响应内容
        print("Upload response:", response.text)

        # 解析返回的 JSON，获取图片的 URL
        if response.status_code == 200:
            try:
                json_response = response.json()
                # 根据实际的返回结构，提取图片 URL
                image_url = json_response.get('data', {}).get('url')
                if image_url:
                    return image_url, None
                else:
                    return None, "未能从响应中获取图片 URL。"
            except ValueError:
                return None, "响应不是有效的 JSON 格式。"
        else:
            return None, f"图片上传失败，状态码：{response.status_code}"

    async def get_image_url(self, mermaid_code):
        image_data, error = await self.render_mermaid(mermaid_code)
        if image_data is None:
            return None, error
        else:
            image_url, upload_error = await self.upload_image(image_data)
            if image_url is None:
                return None, upload_error
            else:
                return image_url, None