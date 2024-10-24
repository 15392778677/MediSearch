# modules/llm_handler.py
import sys
sys.path.append('..')
from models.custom_llm import CustomLLM
from modules.performance_tracker import track_performance
from datetime import datetime

class Res:
    def __init__(self, response: str, outline: str, reference: str, arxiv_reference: str, user_question: list):
        self.response_text = response
        self.outline = outline
        self.reference = reference
        self.arxiv_reference = arxiv_reference
        self.user_question = user_question

class LLMHandler:
    def __init__(self):
        self.llm = CustomLLM()

    @track_performance
    def generate_response(self, prompt: str) -> str:
        """
        使用 LLM 生成响应。
        """
        try:
            resutl = self.llm._call(prompt)
            # print(resutl)
            return resutl
        except Exception as e:
            return f"生成响应失败：{e}"

    def SearchPrompt(self, response: Res) -> str:
        # 获取当前日期和时间
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

        prompt = f"""
        # 助手背景

        你是经方智谷学术搜索引擎，由安果科技有限公司训练的 AI 学术搜索助手。

        # 总体指令

        根据 INITIAL_QUERY 和提供的大纲，撰写准确、详细、全面的回应。
        附加上下文作为 Original Response 和具体问题后的参考。
        回答应基于提供的 "Search results"。

        你的回答必须详细、结构化。优先使用列表、表格和引用来组织内容。
        回答应精准、高质量，使用专业且公正的语气。

        你必须引用最相关的搜索结果。不要提及不相关的结果。
        引用格式：
        - 引用必须始终使用英文格式，无论答案使用何种语言。
        - 每个引用以 [citation:x] 开头，其中 x 是数字。
        - 在对应句子的末尾，用方括号包含引用编号，如 "冰比水轻。[citation:3]" 或 "北京是中国的首都。[citation:5]"
        - 引用和前面的单词之间不加空格，始终使用方括号。

        如果搜索结果为空或无用，请根据现有知识回答问题。

        格式要求：
        - 使用 markdown 格式化段落、列表、表格和引用。
        - 使用四级标题（####）分隔回答的部分，但不要以标题开始回答。
        - 列表使用单换行，段落之间使用双换行。
        - 使用 markdown 渲染搜索结果中给出的图像。
        - 不要写 URL 或链接。

        你必须为学术研究查询提供长而详细的答案。
        回答应格式化为科学写作，使用段落和章节，使用 markdown 和标题。

        # 大纲
        {response.outline}

        以下是搜索结果：
        # 原始响应：
        {response.response_text}

        # 详细参考
        {response.reference}
        # ArXiv 参考文献：
        {response.arxiv_reference}

        你的回答必须使用与用户问题相同的语言。如果用户问题是中文，回答也应是中文。

        今天的日期是 {formatted_time}，以下是 INITIAL_QUERY：
        {response.user_question}
        """
        # print(prompt)
        return prompt

    def Mermaid_Graph_Prompt(self, response: Res) -> str:
        prompt = f"""
        你需要将输入的大纲转换为流程图或思维导图，必须使用 mermaid 语法输出！
        # 大纲：
        {response.outline}
        判断大纲更适合以思维导图还是流程图表示，并以 mermaid 语法输出，不要给出任何多余解释！
        只需输出 mermaid 语法，不能输出其他格式或多余语句！
        请严格按照以下格式输出：
        ```mermaid
        ```
        输出：
        """
        return prompt
    
    def get_query_prompt_from_keywords(self, Question: str,keywords: str) -> str:
        prompt = f"""
        ## role：
        你是一个学术查询语句生成器，你需要根据用户问题和关键词列表生成查询语句，可以使用复杂bool查询语法。
        ## goles：
        你需要理解用户意图，并生成最合适的查询语法!
        ##  action：
        1.首先请检查{keywords}是否是英文，如果不是,先转换为英文,生成KEYWORDS_ENGLISH
        2.根据UER_QUESTION补充更多的KEYWORDS_ENGLISH，你可以进行联想，生成的关键词必须遵循MeSH标准。
        3.KEYWORDS必须简洁没有歧义，不能包含过多的词汇。
        2.根据KEYWORDS_ENGLISH和USER_QUESTION生成查询语句，并使用bool查询语法。
        ## 规则：
        你生成查询语句只能是使用bool运算符(AND, OR, NOT)连接的KEYWORDS_ENGLISH，不能使用其他语法。
        不要生成多余的废话，只需输出查询语句即可。
        生成的查询语句必须遵循MeSH标准。
        MeSH (Medical Subject Headings) 是 PubMed 的受控词汇表，专门用于对生物医学文献进行分类。
        MeSH标准指的是使用[Mesh Terms]和[All Fields]来标记查询语句中的关键词。
        [MeSH Terms]表示医学主题词汇，[All Fields]表示所有领域的词汇。
        输出必须是英文!
        ## example:
        keywords: ["herbal medicine","machine learning","artificial intelligence","research"]
        query_statement: '"herbal medicine"[MeSH Terms] AND (machine learning[All Fields] OR artificial intelligence[All Fields]) AND "research"[MeSH Terms]'
        ## input：
        下面是USER_QUESTION和KEYWORDS：
        USER_QUESTION：{Question}
        KEYWORDS：{keywords}
        输出：

        """
        return prompt
    
    