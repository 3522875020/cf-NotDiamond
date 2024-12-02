from typing import List, Dict, Optional, Any
from openai import OpenAI
from notdiamond import NotDiamond
import logging
import time

from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Model configuration class"""
    provider: str
    model: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0
    presence_penalty: float = 0

class NotDiamondOpenAIAdapter:
    """Adapter to route requests between NotDiamond and OpenAI"""
    
    def __init__(
        self,
        notdiamond_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        default_model: str = "openai/gpt-3.5-turbo",
        timeout: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the adapter with API keys and configs"""
        self.nd_client = NotDiamond(api_key=notdiamond_api_key)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.default_model = default_model
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)

        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _get_model_config(self, model: str) -> ModelConfig:
        """Get model configuration based on model name"""
        # Add model specific configurations here
        return ModelConfig(
            provider="openai",
            model=model,
            max_tokens=4096,
            temperature=0.7
        )

    async def route_request(
        self,
        messages: List[Dict[str, str]],
        model_candidates: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Route the request to appropriate model using NotDiamond"""
        start_time = time.time()
        
        try:
            # Use default models if none specified
            if not model_candidates:
                model_candidates = [
                    "openai/gpt-4-turbo-preview",
                    "openai/gpt-3.5-turbo",
                    "anthropic/claude-3-sonnet-20240229"
                ]

            # Get model recommendation from NotDiamond
            result, session_id, provider = self.nd_client.chat.completions.create(
                messages=messages,
                model=model_candidates,
                timeout=self.timeout,
                default=self.default_model,
                **kwargs
            )

            self.logger.info(
                f"NotDiamond recommended model: {provider.model} (session_id: {session_id})"
            )

            # Format response
            response = {
                "id": session_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": provider.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.content
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": None,  # Would need token counting implementation
                    "completion_tokens": None,
                    "total_tokens": None
                },
                "system_fingerprint": None,
                "_routing_time": time.time() - start_time
            }

            return response

        except Exception as e:
            self.logger.error(f"Error routing request: {str(e)}")
            # Fallback to default model
            self.logger.info(f"Falling back to default model: {self.default_model}")
            
            completion = self.openai_client.chat.completions.create(
                model=self.default_model.split('/')[-1],
                messages=messages,
                **kwargs
            )
            
            return completion.model_dump()

    def submit_feedback(
        self,
        session_id: str,
        score: float,
        feedback_type: str = "quality"
    ) -> None:
        """Submit feedback to NotDiamond for continuous learning"""
        try:
            self.nd_client.feedback.create(
                session_id=session_id,
                score=score,
                feedback_type=feedback_type
            )
            self.logger.info(f"Feedback submitted for session {session_id}")
        except Exception as e:
            self.logger.error(f"Error submitting feedback: {str(e)}")

def create_adapter(
    notdiamond_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    **kwargs
) -> NotDiamondOpenAIAdapter:
    """Factory function to create adapter instance"""
    return NotDiamondOpenAIAdapter(
        notdiamond_api_key=notdiamond_api_key or os.getenv("NOTDIAMOND_API_KEY"),
        openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
        **kwargs
    ) 