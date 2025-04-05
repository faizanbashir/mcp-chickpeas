import logging
import os
import sys
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from mcp.server.fastmcp import FastMCP

# Configure logging with a detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Gemini AI Server")

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.error("GEMINI_API_KEY environment variable is not set")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=API_KEY)

# Available Gemini models
MODELS = {
    "gemini-1.5-flash": "Fast and versatile performance across a diverse variety of tasks",
    "gemini-2.0-flash-litegemini-2.0-flash-lite": "Cost efficiency and low latency",
    "gemini-2.5-pro-preview-03-25": "Enhanced thinking and reasoning, multimodal understanding",
    "gemini-2.0-flash": "Fast and efficient model for quick responses"
}

class GeminiError(Exception):
    """Custom exception for Gemini API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def initialize_model(model_name: str = "gemini-2.0-flash"):
    """Initialize a Gemini model with error handling"""
    try:
        logger.info(f"Initializing Gemini model: {model_name}")
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        logger.error(f"Failed to initialize model {model_name}: {str(e)}")
        raise GeminiError(f"Model initialization failed: {str(e)}")

@mcp.tool()
async def generate_content(prompt: str, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    """
    Generate content using Gemini AI
    
    Args:
        prompt: The input prompt for the AI
        model_name: The Gemini model to use (default: gemini-2.0-flash)
    
    Returns:
        Dict containing generated content and metadata
    """
    try:
        logger.info(f"Generating content with {model_name}")
        logger.debug(f"Prompt: {prompt}")
        
        model = initialize_model(model_name)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        
        logger.info("Content generated successfully")
        return {
            "content": response.text,
            "model": model_name,
            "prompt_tokens": len(prompt.split()),
            "timestamp": response.prompt_feedback.timestamp.isoformat() if response.prompt_feedback else None
        }
        
    except google_exceptions.GoogleAPIError as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise GeminiError(f"API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise GeminiError(f"Generation failed: {str(e)}")

@mcp.tool()
async def list_models() -> Dict[str, str]:
    """
    Get a list of available Gemini models and their descriptions
    
    Returns:
        Dict mapping model names to their descriptions
    """
    logger.info("Listing available models")
    return MODELS

@mcp.tool()
async def analyze_text(text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
    """
    Analyze text using Gemini AI
    
    Args:
        text: The text to analyze
        analysis_type: Type of analysis (sentiment, entities, classification)
    
    Returns:
        Dict containing analysis results
    """
    try:
        logger.info(f"Performing {analysis_type} analysis")
        model = initialize_model("gemini-2.0-flash")
        
        prompts = {
            "sentiment": f"Analyze the sentiment of this text and return a label (positive, negative, or neutral) with a confidence score: {text}",
            "entities": f"Extract the main entities (people, organizations, locations) from this text: {text}",
            "classification": f"Classify this text into relevant categories: {text}"
        }
        
        if analysis_type not in prompts:
            raise ValueError(f"Invalid analysis type: {analysis_type}")
            
        response = model.generate_content(prompts[analysis_type])
        
        logger.info(f"Analysis completed: {analysis_type}")
        return {
            "analysis_type": analysis_type,
            "result": response.text,
            "text_length": len(text),
            "timestamp": response.prompt_feedback.timestamp.isoformat() if response.prompt_feedback else None
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise GeminiError(f"Analysis failed: {str(e)}")

@mcp.tool()
async def chat_stream(messages: List[Dict[str, str]], model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
    """
    Start a chat session with Gemini AI
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model_name: The Gemini model to use
    
    Returns:
        Dict containing chat response and metadata
    """
    try:
        logger.info(f"Starting chat session with {model_name}")
        model = initialize_model(model_name)
        chat = model.start_chat(history=[])
        
        for msg in messages:
            if msg["role"] == "user":
                response = chat.send_message(msg["content"])
        
        logger.info("Chat session completed")
        return {
            "response": response.text,
            "model": model_name,
            "message_count": len(messages),
            "timestamp": response.prompt_feedback.timestamp.isoformat() if response.prompt_feedback else None
        }
        
    except Exception as e:
        logger.error(f"Chat session failed: {str(e)}")
        raise GeminiError(f"Chat failed: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Gemini AI Server")
    mcp.run("stdio")
