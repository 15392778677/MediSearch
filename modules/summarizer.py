# modules/summarizer.py
import sys
sys.path.append('..')
from modules.llm_handler import LLMHandler
from modules.performance_tracker import track_performance
import html2text

class Summarizer:
    def __init__(self):
        self.llm_handler = LLMHandler()

    @track_performance
    def html_to_markdown(self, html_content: str) -> str:
        """
        将 HTML 内容转换为 Markdown 格式。
        """
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        markdown_content = converter.handle(html_content)
        return markdown_content

    @track_performance
    def summarize_html_content(self, article_title: str, html_content: str) -> str:
        """
        总结 HTML 内容，生成简短摘要。
        """
        markdown_content = self.html_to_markdown(html_content)
        content = f"""
        请以简单易懂的方式解释以下 Markdown 内容中提到的治疗方法，特别是与“{article_title}”相关的信息。
        不要使用任何插件或工具，只需使用提供的 Markdown 内容。
        忽略文中的 HTML 标签、广告和不相关的链接，仅关注医疗信息。
        尝试在50字以内用中文概括，让没有医学背景的人也能理解。
        解释为什么采用这种治疗方式，并突出其关键好处。
        输出只需保留答案形式的文本内容，不包含任何 HTML 标签或 Markdown 的网页链接。
        如果出现 page not found 或其他错误情况，返回“网络出现异常，请稍后再试。”
        以下是 Markdown 内容：
        {markdown_content}
        """
        return self.llm_handler.generate_response(content)

    @track_performance
    def generate_outline(self, conversation_history: list) -> str:
        """
        根据对话历史生成结构化大纲。
        """
        advice_text = " ".join(conversation_history)
        prompt = f"""
        根据以下对话内容生成一个结构化大纲。
        不需要精确到具体细节。
        请尽量简明扼要，便于理解。使用 Markdown 格式。
        只需提供大纲内容，不需要额外说明。
        {advice_text}
        """
        return self.llm_handler.generate_response(prompt)