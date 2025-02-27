"""
gemini_model.py - Google Generative AI (Gemini) model adapter for SmolaGents
"""

import os
import uuid
import logging
from typing import Any, Dict, List, Optional, Union

from smolagents.models import Model, ChatMessage, ChatMessageToolCall, ChatMessageToolCallDefinition, MessageRole

# Configure logging
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI package not installed. Install with: pip install google-generativeai")


class GeminiModel(Model):
    """
    Adapter for Google's Generative AI models (Gemini) to work with SmolaGents.
    
    This model adapter allows using Google's Gemini models with the SmolaGents framework,
    providing proper handling of tool calls, message formatting, and response parsing.
    
    Args:
        model_id (str, optional): The Gemini model to use. Defaults to "gemini-1.5-pro".
        api_key (str, optional): API key for Gemini. If not provided, will look for GOOGLE_API_KEY environment variable.
        temperature (float, optional): Controls randomness in generation. Defaults to 0.7.
        max_tokens (int, optional): Maximum tokens to generate. Defaults to 8192.
        **kwargs: Additional arguments passed to the base Model class.
    
    Example:
        ```python
        from gemini_model import GeminiModel
        from smolagents import CodeAgent
        
        model = GeminiModel(model_id="gemini-1.5-pro")
        agent = CodeAgent(tools=[], model=model)
        agent.run("Write a function to calculate prime numbers")
        ```
    """
    
    def __init__(
        self,
        model_id: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        **kwargs
    ):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai")
        
        super().__init__(**kwargs)
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize the Gemini API
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("API key is required. Set GOOGLE_API_KEY environment variable or pass api_key.")
            
        self.client = genai.Client(api_key=api_key)
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_id)
        self.last_input_token_count = 0
        self.last_output_token_count = 0
    
    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List] = None,
        **kwargs
    ) -> ChatMessage:
        """
        Process the input messages and return the model's response.
        
        Args:
            messages (List[Dict[str, str]]): List of messages to send to the model.
            stop_sequences (Optional[List[str]], optional): Sequences to stop generation. Defaults to None.
            grammar (Optional[str], optional): Grammar specification for the output. Defaults to None.
            tools_to_call_from (Optional[List], optional): Tools the model can use. Defaults to None.
            **kwargs: Additional parameters to pass to the model.
            
        Returns:
            ChatMessage: The model's response as a ChatMessage object.
        """
        # Prepare completion kwargs and convert to Gemini format
        completion_kwargs = self._prepare_completion_kwargs(
            messages=messages,
            stop_sequences=stop_sequences,
            grammar=grammar,
            tools_to_call_from=tools_to_call_from,
            convert_images_to_image_urls=True,
            **kwargs
        )
        
        # Convert messages to Gemini's format
        gemini_messages = self._convert_messages_to_gemini_format(completion_kwargs["messages"])
        
        # Generate response
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=gemini_messages,
            config=types.GenerateContentConfig(
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.95),
                top_k=kwargs.get("top_k", 40),
                max_output_tokens=kwargs.get("max_tokens", 8192),
                stop_sequences=stop_sequences,
            ),
            tools=tool_configs if tools_to_call_from else None,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ) if tools_to_call_from else None,
        )
        
        # Process response
        return self._process_gemini_response(response, tools_to_call_from)
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert messages to Gemini's format."""
        gemini_messages = []
        
        for message in messages:
            role = "user" if message["role"] == MessageRole.USER else "model"
            
            if isinstance(message["content"], list):
                # Handle multimodal content
                parts = []
                for content_item in message["content"]:
                    if content_item["type"] == "text":
                        parts.append({"text": content_item["text"]})
                    elif content_item["type"] == "image_url":
                        url = content_item["image_url"]["url"]
                        if url.startswith("data:image"):
                            # Handle base64 encoded images
                            parts.append({
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": url.split(",")[1]
                                }
                            })
                        else:
                            parts.append({"image_url": url})
                
                gemini_messages.append({"role": role, "parts": parts})
            else:
                # Simple text content
                gemini_messages.append({
                    "role": role,
                    "parts": [{"text": message["content"]}]
                })
        
        return gemini_messages
    
    def _generate_gemini_response(
        self,
        gemini_messages: List[Dict[str, Any]],
        stop_sequences: Optional[List[str]],
        tools_to_call_from: Optional[List],
        completion_kwargs: Dict[str, Any]
    ) -> Any:
        """Generate a response from Gemini API."""
        # Create generation config
        generation_config = genai.GenerationConfig(
            temperature=completion_kwargs.get("temperature", self.temperature),
            top_p=completion_kwargs.get("top_p", 0.95),
            top_k=completion_kwargs.get("top_k", 40),
            max_output_tokens=completion_kwargs.get("max_tokens", self.max_tokens),
            stop_sequences=stop_sequences,
        )
        
        if tools_to_call_from:
            # Configure tools for Gemini
            tool_configs = self._prepare_tool_configs(tools_to_call_from)
            
            try:
                # Generate response with tools
                response = self.model.generate_content(
                    gemini_messages,
                    generation_config=generation_config,
                    tools=tool_configs,
                    tool_config={"function_calling_config": {"mode": "auto"}},
                )
            except Exception as e:
                logger.error(f"Error generating content with tools: {str(e)}")
                # Fallback to standard generation
                response = self.model.generate_content(
                    gemini_messages,
                    generation_config=generation_config,
                )
        else:
            # Standard generation without tools
            response = self.model.generate_content(
                gemini_messages,
                generation_config=generation_config,
            )
        
        return response
    
    def _prepare_tool_configs(self, tools_to_call_from):
        """Prepare tool configurations for Gemini."""
        tool_configs = []
        
        for tool in tools_to_call_from:
            tool_config = types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={},
                            required=[]
                        )
                    )
                ]
            )
            
            # Add parameters
            for param_name, param_details in tool.inputs.items():
                param_type = param_details["type"]
                if param_type == "any":
                    param_type = "string"  # Gemini doesn't support 'any' type
                
                tool_config["function_declarations"][0]["parameters"]["properties"][param_name] = {
                    "type": param_type,
                    "description": param_details.get("description", "")
                }
                
                # Add required parameters
                if not param_details.get("nullable", False):
                    tool_config["function_declarations"][0]["parameters"]["required"].append(param_name)
            
            tool_configs.append(tool_config)
        
        return tool_configs
    
    def _process_gemini_response(self, response, tools_to_call_from):
        """Process Gemini response into ChatMessage format."""
        # Extract token counts if available
        if hasattr(response, "usage_metadata"):
            self.last_input_token_count = getattr(response.usage_metadata, "prompt_token_count", 0)
            self.last_output_token_count = getattr(response.usage_metadata, "candidates_token_count", 0)
        
        # Initialize content and tool_calls
        content = ""
        tool_calls = None
        
        # Extract text content
        if hasattr(response, "text"):
            content = response.text
        elif hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                if hasattr(candidate.content, "text"):
                    content = candidate.content.text
                elif hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "text"):
                            content += part.text
        
        # Check for function calls
        if tools_to_call_from and hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                if hasattr(candidate.content, "parts") and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "function_call"):
                            if tool_calls is None:
                                tool_calls = []
                            
                            # Create a tool call from the function call
                            function_call = part.function_call
                            tool_calls.append(
                                ChatMessageToolCall(
                                    id=str(uuid.uuid4()),
                                    type="function",
                                    function=ChatMessageToolCallDefinition(
                                        name=function_call.name,
                                        arguments=function_call.args,
                                    )
                                )
                            )
        
        # Create and return a ChatMessage
        return ChatMessage(
            role="assistant",
            content=content if not tool_calls else None,
            tool_calls=tool_calls,
            raw=response
        )

    def to_dict(self) -> Dict:
        """Convert model to dictionary representation."""
        return {
            **super().to_dict(),
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeminiModel":
        """Create a model instance from a dictionary."""
        return cls(
            model_id=data.get("model_id", "gemini-1.5-pro"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 8192),
        )
