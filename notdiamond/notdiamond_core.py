from typing import Any

class NotDiamond:
    """Mocked NotDiamond client for demonstration purposes."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    class Chat:
        class Completions:
            @staticmethod
            def create(messages: Any, model: Any, timeout: int, default: str, **kwargs):
                # 模拟 NotDiamond 的响应
                class Provider:
                    def __init__(self, model):
                        self.model = model
                
                result = type('Result', (object,), {'content': "This is a mocked response."})()
                session_id = "mock_session_id"
                provider = Provider(model=model[0])
                return result, session_id, provider

    @property
    def chat(self):
        return self.Chat()
    
    class Feedback:
        @staticmethod
        def create(session_id: str, score: float, feedback_type: str):
            # 模拟反馈提交
            pass 