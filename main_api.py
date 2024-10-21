# api_service.py
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from concurrent.futures import ThreadPoolExecutor

from modules.mediator import Mediator
from modules.summarizer import Summarizer
from modules.web_scraper import WebScraper
from modules.arxiv_search import ArxivSearch
from modules.performance_tracker import track_performance
from modules.llm_handler import LLMHandler, Res
from modules.flowchat import MermaidToImageUploader
from modules.Markdown import render_markdown_image, parse_mermaid_syntax
from config import API_KEY

app = FastAPI()

# 允许所有源访问（根据需要进行限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wrap_text(text, width):
    import textwrap
    return textwrap.wrap(text, width)

@track_performance
def convert_to_markdown(arxiv_reference):
    markdown  = "| Title | URL | Keywords | Summary |\n"
    markdown += "|-------|-----|----------|---------|\n"
    for ref in arxiv_reference:
        title = ref['title'].replace('\n', ' ')
        url = ref['url']
        keywords = ', '.join(ref['keywords'])
        summary = ref['summary'].replace('\n', ' ')
        markdown += f"| {title} | [Link]({url}) | {keywords} | {summary} |\n"
    return markdown

@track_performance
def conver_to_chinese(markdown: str):
    prompt = f"""
    请将以下 markdown 表格翻译为中文，并以 markdown 格式输出：
    注意只能输出翻译后的表格，不要添加多余内容！
    原始表格：
    {markdown}
    输出：
    """

    llm_handler = LLMHandler()
    result = llm_handler.generate_response(prompt)
    return result

@track_performance
async def generate_detailed_response(result, conversation_history, executor):
    response = result.get('response', '')
    outline = result.get('outline', '')
    reference = result.get('reference', [])
    arxiv_reference = result.get('arxiv_reference', [])

    reference_text = "\n\n".join([
        f"Title: {ref['title']}\nURL: {ref['url']}\nSummary: {ref['summary']}"
        for ref in reference
    ])

    arxiv_reference_text = "\n\n".join([
        f"Title: {ref['title']}\nURL: {ref['url']}\nKeywords: {', '.join(ref['keywords'])}\nSummary: {ref['summary']}"
        for ref in arxiv_reference
    ])

    res = Res(response, outline, reference_text, arxiv_reference_text, conversation_history)
    llm_handler = LLMHandler()

    # 使用线程池并行执行 LLM 调用
    detailed_response_future = asyncio.get_event_loop().run_in_executor(
        executor, llm_handler.generate_response, llm_handler.SearchPrompt(res)
    )
    print("detailed response future created")

    # 并发获取图表和转换 markdown
    graph_and_markdown = await asyncio.gather(
        get_Graph(res, executor),
        asyncio.get_event_loop().run_in_executor(executor, convert_to_markdown, arxiv_reference)
    )
    print("graph and markdown future created")

    detailed_response = await detailed_response_future

    graph_result, reference_table_english = graph_and_markdown

    # 生成图表
    if graph_result['stateCode'] == 200:
        detailed_response += f"\n\n{render_markdown_image(graph_result['image_url'])}\n\n"

    # 添加参考文献表格
    reference_table_chinese = await asyncio.get_event_loop().run_in_executor(
        executor, conver_to_chinese, reference_table_english
    )
    print("reference table future created")

    detailed_response += "\n\n### 相关论文整理表格 (英文)\n"
    detailed_response += reference_table_english
    detailed_response += "\n\n### 相关论文整理表格 (中文)\n"
    detailed_response += reference_table_chinese

    return detailed_response

@track_performance
async def get_Graph(res: Res, executor) -> dict:
    llm_handler = LLMHandler()
    prompt = llm_handler.Mermaid_Graph_Prompt(res)
    # 使用线程池执行 generate_response
    result = await asyncio.get_event_loop().run_in_executor(
        executor, llm_handler.generate_response, prompt
    )
    mermaid_code = parse_mermaid_syntax(result)
    uploader = MermaidToImageUploader()
    image_url, error = await uploader.get_image_url(mermaid_code)
    if image_url:
        return {"stateCode": 200, "image_url": image_url}
    else:
        return {"stateCode": 500, "image_url": None, "error": error}

@track_performance
async def MediSearch(conversation_history, send_update):
    mediator = Mediator(api_key=API_KEY)
    summarizer = Summarizer()
    web_scraper = WebScraper()
    arxiv_search = ArxivSearch()

    # 获取医学建议
    advice_response = mediator.fetch_medicine_advice_with_history(conversation_history)
    if advice_response['last_text_event']:
        conversation_history.append(advice_response['last_text_event'])

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=10)

    try:
        # 开始任务

        # 生成大纲
        outline_future = asyncio.get_event_loop().run_in_executor(
            executor, summarizer.generate_outline, conversation_history
        )

        # 获取 arXiv 文章
        def fetch_arxiv():
            keywords = arxiv_search.fetch_keywords_from_conversation(conversation_history)
            arxiv_response = arxiv_search.search_arxiv_papers(keywords)
            arxiv_articles = arxiv_search.parse_arxiv_response(arxiv_response)
            return arxiv_articles

        arxiv_future = asyncio.get_event_loop().run_in_executor(
            executor, fetch_arxiv
        )

        # 发送初始结果
        async def send_initial_results():
            outline = await outline_future
            await send_update(json.dumps({"type": "outline", "data": outline}))

            arxiv_articles = await arxiv_future
            await send_update(json.dumps({"type": "arxiv_reference", "data": arxiv_articles}))

        initial_results_task = asyncio.create_task(send_initial_results())

        # 获取并总结文章
        def fetch_and_summarize(article):
            html_content = web_scraper.fetch_and_parse_single_url(article.get('url', ''))
            summary = summarizer.summarize_html_content(article.get('title', ''), html_content)
            print("summary finished")
            return {
                'title': article.get('title', 'N/A'),
                'url': article.get('url', 'N/A'),
                'summary': summary
            }

        # 使用线程池并发处理文章
        article_futures = [
            asyncio.get_event_loop().run_in_executor(
                executor, fetch_and_summarize, article
            ) for article in advice_response['articles']
        ]
        articles_info = await asyncio.gather(*article_futures)

        # 等待初始结果发送完成
        await initial_results_task
        print("initial results sent")

        # 准备最终结果
        result = {
            "response": advice_response['last_text_event'],
            "outline": await outline_future,
            "reference": articles_info,
            "arxiv_reference": await arxiv_future
        }

        # 生成详细响应
        detailed_result = await generate_detailed_response(result, conversation_history, executor)
        print("detailed result generated")
        result['response'] = detailed_result

        # 发送详细响应
        await send_update(json.dumps({"type": "result", "data": result}))

    finally:
        # 关闭线程池
        executor.shutdown()

@app.post("/medisearch")
async def medisearch_endpoint(query: dict):
    """
    MediSearch 接口，接受 'conversation_history' 字段。
    在数据生成后以流的方式返回给客户端。
    """
    conversation_history = query.get('conversation_history', [])

    async def event_generator():
        queue = asyncio.Queue()

        async def send_update(message):
            await queue.put(message)

        medisearch_task = asyncio.create_task(MediSearch(conversation_history, send_update))

        while True:
            message = await queue.get()
            yield f"data: {message}\n\n"

            if medisearch_task.done() and queue.empty():
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")