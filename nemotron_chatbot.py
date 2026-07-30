import os
import requests
import json
from typing import List, Dict, Any

class NemotronChatBot:
    def __init__(self, api_key: str = None, model: str = "nemotron-3-ultra"):
        """
        Initialize the Nemotron 3 Ultra chat bot.
        
        Args:
            api_key: NVIDIA API key. If not provided, will try to get from environment variable NVIDIA_API_KEY
            model: Model name to use (default: nemotron-3-ultra)
        """
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Provide it as argument or set NVIDIA_API_KEY environment variable.")
        
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_system_prompt(self, system_prompt: str):
        """Add a system prompt to the conversation history."""
        self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
    
    def chat(self, user_message: str, temperature: float = 0.7, max_tokens: int = 1024, top_p: float = 0.9) -> str:
        """
        Send a message to the chat bot and get a response.
        
        Args:
            user_message: The user's message
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            top_p: Top-p sampling parameter
            
        Returns:
            The bot's response as a string
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare the request payload
        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            bot_response = result["choices"][0]["message"]["content"]
            
            # Add bot response to history
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
            raise Exception(error_msg)
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected response format: {str(e)}")
    
    def clear_history(self, keep_system_prompt: bool = True):
        """Clear conversation history, optionally keeping the system prompt."""
        if keep_system_prompt and self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_prompt = self.conversation_history[0]
            self.conversation_history = [system_prompt]
        else:
            self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()


def main():
    # Your API key (in production, use environment variable instead)
    API_KEY = "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"
    
    # Initialize the chat bot
    bot = NemotronChatBot(api_key=API_KEY)
    
    # Optional: Add a system prompt
    bot.add_system_prompt("You are a helpful, harmless, and honest AI assistant named Nemotron 3 Ultra.")
    
    print("Nemotron 3 Ultra Chat Bot")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'clear' to clear conversation history.")
    print("Type 'history' to see conversation history.")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                bot.clear_history()
                print("Conversation history cleared.")
                continue
            
            if user_input.lower() == 'history':
                history = bot.get_history()
                print("\nConversation History:")
                for msg in history:
                    role = msg["role"].capitalize()
                    content = msg["content"][:100] + ("..." if len(msg["content"]) > 100 else "")
                    print(f"  {role}: {content}")
                continue
            
            print("\nNemotron: ", end="", flush=True)
            response = bot.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
