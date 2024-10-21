'''
Date: 2024-10-14 15:31:49
LastEditors: yangyehan 1958944515@qq.com
LastEditTime: 2024-10-18 16:55:37
FilePath: /MediSearch/modules/Markdown.py
Description: 
'''
def render_markdown_image(url):
    """
    将给定的图片 URL 转换为适配屏幕大小的 Markdown 语法，并使图片可点击查看大图。
    """
    html_markdown = f'''
<div style="text-align: center;">
    <a href="{url}" target="_blank">
        <img src="{url}"  style="max-width: 100%; height: auto;">
    </a>
</div>
'''
    return html_markdown

def parse_mermaid_syntax(mermaid_str):
    """
    解析给定的 Mermaid 语法字符串，返回其内容。
    如果输入字符串包含以 ```mermaid 开头并以 ``` 结束的部分，则提取并解析。
    如果不包含，则返回原始字符串。
    """
    # 查找是否存在 ```mermaid 开头和 ``` 结尾的部分
    start_tag = "```mermaid"
    end_tag = "```"

    # 检查是否包含合法的 mermaid 语法代码块
    start_index = mermaid_str.find(start_tag)
    end_index = mermaid_str.rfind(end_tag)

    # 如果找到合法的 mermaid 代码块，提取中间内容
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # 提取 mermaid 代码块部分
        mermaid_code = mermaid_str[start_index + len(start_tag):end_index].strip()
        return mermaid_code

    # 如果不是合法的 Mermaid 代码块，则返回原始内容
    return mermaid_str