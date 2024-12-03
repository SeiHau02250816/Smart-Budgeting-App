import os
import sys
import anthropic

class ClaudeClient:
    def __init__(self, api_key, model="claude-3-5-haiku-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def send_message(self, message):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,    
                temperature=0,
                system="You are a world-class poet. Respond only with short poems.",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": message
                            }
                        ]
                    }
                ]
            )
            return response.content[0]
        except Exception as e:
            return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        raise EnvironmentError("Error: CLAUDE_API_KEY environment variable is not set.")

    client = ClaudeClient(api_key)
    response = client.send_message("Hello, Claude!")
    print("Response from Claude:\n", response.text)