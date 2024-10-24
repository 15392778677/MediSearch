'''
Date: 2024-10-13 17:48:43
LastEditors: yangyehan 1958944515@qq.com
LastEditTime: 2024-10-23 17:06:37
FilePath: /MediSearch_SSE/models/custom_llm.py
Description: 
'''
# models/custom_llm.py
import sys
import asyncio
from typing import Any, List, Dict, Mapping, Optional
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from openai import OpenAI

class CustomLLM(LLM):
    logging: bool = False
    output_keys: List[str] = ["output"]
    llm_type: str = "gpt-4o-mini-2024-07-18"
    history: List[Mapping[str, str]] = []

    @property
    def _llm_type(self) -> str:
        return self.llm_type

    def log(self, log_str):
        if self.logging:
            print(log_str)

    def add_history(self, role: str, content: str):
        """添加历史对话到history列表中。"""
        self.history.append({"role": role, "content": content})

    def add_multiple_histories(self, histories: List[Dict[str, str]]):
        """一次性添加多条历史对话到history列表中。"""
        self.history.extend(histories)
    
    def check_history(self) -> List[Mapping[str, str]]:
        """返回当前的历史对话记录。"""
        return self.history.copy()

    def clear_history(self):
        """清空历史对话。"""
        self.history.clear()

    async def _call_async(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        return await asyncio.to_thread(self._call, prompt)
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        self.log('----------' + self._llm_type + '----------> llm._call()')
        self.log(prompt)

        # 先将用户的输入添加到history中
        self.add_history("user", prompt)

        # 然后直接使用更新后的history赋值给messages
        messages = self.history.copy() 

        try:
            client = OpenAI(
                api_key='sk-fMSbNiWFQUfXBoWnF433CcE88f1245F8BcBcAe2bBdA30d72',  # 请确保使用安全的方式存储API密钥
                base_url='https://api.gpt.ge/v1/'
            )
            response = client.chat.completions.create(
                messages=messages,
                model="gpt-4o-mini-2024-07-18",
            )
            
        except Exception as e:
            print("发生错误:", e)
            response = None

        if response is None:
            response_content = ""
        else:
            response_content = response.choices[0].message.content
            self.add_history("assistant", response_content)  # 将系统回复作为历史记录添加

        return response_content

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"n": 10}

if __name__ == "__main__":
    llm = CustomLLM()
    result = asyncio.run(llm._call_async("你是什么模型？"))
    print(result)