# modules/mediator.py
import sys
sys.path.append('..')
from medisearch_client import MediSearchClient
import uuid
from modules.performance_tracker import track_performance
from config import API_KEY

class Mediator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @track_performance
    def fetch_medicine_advice_with_history(self, conversation_history: list) -> dict:
        """
        使用 MediSearchClient 获取医学建议。
        """
        conversation_id = str(uuid.uuid4())
        client = MediSearchClient(api_key=self.api_key)

        responses = client.send_user_message(conversation=conversation_history,
                                             conversation_id=conversation_id,
                                             should_stream_response=True,
                                             language="Chinese")
        last_text_event = None
        all_articles_events = []

        for response in responses:
            if response['event'] == 'llm_response':
                last_text_event = response['text']
            elif response['event'] == 'articles':
                all_articles_events.extend(response['articles'])

        return {
            "last_text_event": last_text_event,
            "articles": all_articles_events
        }