from .base_model import BaseAIModel
from .gemini_model import GeminiModel
from .openai_model import OpenAIModel
from .claude_model import ClaudeModel
from .llama_cpp_model import LlamaCppModel

def get_ai_model(model_type: str):
    """
    Factory method to get the appropriate AI model based on configuration.
    
    Args:
        model_type: Type of AI model to use ("gemini", "openai", "claude", or "llama")
        
    Returns:
        An instance of BaseAIModel
        
    Raises:
        ValueError: If the specified model type is not supported
    """
    if model_type.lower() == "gemini":
        return GeminiModel()
    elif model_type.lower() == "openai":
        return OpenAIModel()
    elif model_type.lower() == "claude":
        return ClaudeModel()
    elif model_type.lower() in ["llama", "llamacpp", "llama-cpp"]:
        return LlamaCppModel()
    else:
        raise ValueError(f"Unsupported AI model type: {model_type}") 