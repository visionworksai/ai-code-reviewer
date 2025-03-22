from .base_model import BaseAIModel
from .gemini_model import GeminiModel

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
    # Add other models here when implemented
    # elif model_type.lower() == "openai":
    #     return OpenAIModel()
    else:
        raise ValueError(f"Unsupported AI model type: {model_type}") 