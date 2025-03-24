import os
import json
from typing import List, Dict, Any
from .base_model import BaseAIModel
from llama_cpp import Llama

class LlamaCppModel(BaseAIModel):
    """
    Implementation of BaseAIModel that uses llama.cpp for local language models.
    
    This class enables running local LLM models through the llama.cpp library,
    which provides efficient CPU/GPU inference for various models like Llama, Mistral,
    and other compatible architectures.
    """
    
    def __init__(self):
        self.model = None
        
        # Default to Qwen2.5-7B model if not specified
        default_model = "Qwen2.5-7B.Q2_K.gguf"
        self.model_path = os.environ.get("LLAMA_MODEL_PATH", default_model)
        
        # Set default parameters optimized for Qwen2.5 model
        self.context_size = int(os.environ.get("LLAMA_CONTEXT_SIZE", "4096"))
        self.n_gpu_layers = int(os.environ.get("LLAMA_GPU_LAYERS", "-1"))
        self.seed = int(os.environ.get("LLAMA_SEED", "42"))
        self.n_threads = int(os.environ.get("LLAMA_THREADS", "4"))
        self.temperature = float(os.environ.get("LLAMA_TEMPERATURE", "0.1"))  # Lower temperature for Qwen
        self.top_p = float(os.environ.get("LLAMA_TOP_P", "0.95"))
        self.max_tokens = int(os.environ.get("LLAMA_MAX_TOKENS", "2048"))
        
        # Qwen model specific parameters
        self.repeat_penalty = float(os.environ.get("LLAMA_REPEAT_PENALTY", "1.1"))
        self.use_qwen = True  # Flag to indicate we're using Qwen by default
        
    def configure(self):
        """
        Configure the llama.cpp model with the specified parameters.
        
        Loads the model from the specified path and configures it with the
        appropriate settings for code review tasks.
        
        Raises:
            ValueError: If the model path is not specified or the model cannot be loaded
        """
        # Check if the model file exists locally, if not, download it
        if not os.path.exists(self.model_path):
            print(f"Model file not found at {self.model_path}")
            print("Downloading Qwen2.5-7B model...")
            self._download_qwen_model()
            
        print(f"Loading model from {self.model_path}")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_gpu_layers=self.n_gpu_layers,
                seed=self.seed,
                n_threads=self.n_threads
            )
            print("Model loaded successfully")
        except Exception as e:
            raise ValueError(f"Failed to load model: {str(e)}")
    
    def _download_qwen_model(self):
        """Download the Qwen2.5-7B model from Hugging Face if not present."""
        import requests
        import os
        
        model_url = "https://huggingface.co/QuantFactory/Qwen2.5-7B-GGUF/resolve/main/Qwen2.5-7B.Q2_K.gguf?download=true"
        model_dir = os.path.dirname(self.model_path) or "."
        model_filename = os.path.basename(self.model_path)
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            
        full_path = os.path.join(model_dir, model_filename)
        
        print(f"Downloading model to {full_path}")
        with requests.get(model_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    downloaded += len(chunk)
                    f.write(chunk)
                    # Print progress
                    if total_size > 0:
                        percent = int(100 * downloaded / total_size)
                        print(f"\rDownloading: {percent}% [{downloaded} / {total_size} bytes]", end="")
            
            print("\nDownload complete!")
        
        self.model_path = full_path
    
    def get_response_from_model(self, prompt: str) -> List[Dict[str, str]]:
        """
        Send prompt to the local LLM and process the response for code review.
        
        Args:
            prompt: A string containing the code review prompt
            
        Returns:
            A list of dictionaries with lineNumber and reviewComment keys
            
        Raises:
            RuntimeError: If the model is not configured
        """
        if self.model is None:
            raise RuntimeError("Model not configured. Call configure() first.")
        
        # Format system prompt based on Qwen model's expected format
        if self.use_qwen:
            system_prompt = """<|im_start|>system
You are a code review assistant. Analyze the code and provide specific, actionable feedback.
Your response should be a valid JSON array with objects containing 'lineNumber' and 'reviewComment' fields.
Example: [{"lineNumber": 42, "reviewComment": "This loop could be optimized."}]
Only include issues worth mentioning - don't add comments if the code looks good.
<|im_end|>"""
            
            full_prompt = f"{system_prompt}\n<|im_start|>user\n{prompt}\n<|im_end|>\n<|im_start|>assistant\n"
        else:
            # Generic format for other models
            system_prompt = """You are a code review assistant. 
            Analyze the code and provide specific, actionable feedback.
            Format your response as a JSON array with objects containing 'lineNumber' and 'reviewComment' fields.
            Example: [{"lineNumber": 42, "reviewComment": "This loop could be optimized."}]
            Only include issues worth mentioning - don't add comments if the code looks good."""
            
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = self.model.create_completion(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                repeat_penalty=self.repeat_penalty,
                echo=False,
                stop=["<|im_end|>", "```"] if self.use_qwen else ["```"],
            )
            
            # Extract the text from the response
            response_text = response["choices"][0]["text"].strip()
            
            # Try to parse as JSON, handling various response formats
            try:
                # Look for JSON array in the response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    parsed_response = json.loads(json_str)
                    
                    # Validate the expected format
                    valid_comments = []
                    for item in parsed_response:
                        if isinstance(item, dict) and 'lineNumber' in item and 'reviewComment' in item:
                            valid_comments.append(item)
                    
                    return valid_comments
                else:
                    # If no JSON array is found
                    print("Warning: Unable to find JSON array in response")
                    return []
                
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract information manually
                print("Warning: JSON parsing failed, attempting to process text manually")
                lines = response_text.split('\n')
                comments = []
                
                current_line = None
                current_comment = []
                
                for line in lines:
                    # Look for patterns like "Line 42:" or "Line: 42"
                    if line.lower().startswith("line") and ":" in line:
                        # If we were building a previous comment, save it
                        if current_line is not None and current_comment:
                            comments.append({
                                "lineNumber": current_line,
                                "reviewComment": " ".join(current_comment).strip()
                            })
                        
                        # Start a new comment
                        parts = line.split(":", 1)
                        try:
                            # Extract line number
                            line_text = parts[0].lower().replace("line", "").strip()
                            current_line = int(line_text)
                            current_comment = [parts[1].strip()] if len(parts) > 1 else []
                        except (ValueError, IndexError):
                            current_line = None
                            current_comment = []
                    elif current_line is not None:
                        # Continue building the current comment
                        current_comment.append(line.strip())
                
                # Don't forget the last comment
                if current_line is not None and current_comment:
                    comments.append({
                        "lineNumber": current_line,
                        "reviewComment": " ".join(current_comment).strip()
                    })
                
                return comments
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return [] 