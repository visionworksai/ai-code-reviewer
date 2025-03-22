from .base_model import BaseAIModel
from .gemini_model import GeminiModel
from .openai_model import OpenAIModel

def get_ai_model(model_type: str = "gemini") -> BaseAIModel:
    """
    Factory function to create and return the appropriate AI model instance.
    
    Args:
        model_type: String identifier for the AI model to use
        
    Returns:
        An instance of a BaseAIModel implementation
        
    Raises:
        ValueError: If the requested model type is not supported
    """
    if model_type.lower() == "gemini":
        return GeminiModel()
    elif model_type.lower() == "openai":
        return OpenAIModel()
    else:
        raise ValueError(f"Unsupported AI model type: {model_type}") 