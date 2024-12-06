import os
import base64
import anthropic
from PIL import Image
import mimetypes
from transaction import Transaction

class ImagePostProcessing:
    def __init__(self, api_key=None):
        """
        Initialize the ImagePostProcessing class.
        
        Args:
            api_key (str): Anthropic API key. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set in CLAUDE_API_KEY environment variable")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _encode_image(self, image_path):
        """
        Encode image to base64 and get its media type.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (media_type, base64_encoded_data)
        """
        # Get the media type
        media_type, _ = mimetypes.guess_type(image_path)
        if not media_type:
            media_type = 'image/jpeg'  # Default to JPEG if type cannot be determined
            
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
            
        return media_type, encoded_data

    def extract_text_from_image(self, image_path):
        """
        Extract text from the given image using Claude's vision capabilities.

        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Result containing extracted text and status information
        """
        try:
            # Verify file exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Encode image
            media_type, encoded_data = self._encode_image(image_path)

            # Create message using Claude's vision capabilities
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": encoded_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": """
                                        Extract the following information from this receipt and return it in a single line CSV format with these exact columns in order:
                                        1. Date (in YYYY-MM-DD format)
                                        2. Amount (in RM, numbers only without 'RM' prefix)
                                        3. Business Name
                                        4. Transaction Category (choose only one: Food, Transport, Lifestyle & Entertainment, Rent, Utilities, Others)

                                        Example format: 2024-03-15,25.90,Restaurant ABC,food
                                        *** STRICTLY ONE LINE CSV FORMAT ***
                                        *** HIGH ACCURACY IS REQUIRED, PLEASE REVIEW BEFORE RETURN OUTPUT ***
                                        """
                            }
                        ],
                    }
                ],
            )

            # Extract text from response and clean it
            extracted_text = message.content[0].text if message.content else ""
            # Remove any extra whitespace or newlines
            cleaned_text = extracted_text.strip().split('\n')[0] if extracted_text else ""

            result = {
                'text': cleaned_text,
                'success': True,
                'processing_status': 'completed'
            }

            # Try to parse the CSV data
            try:
                # Create a Transaction object from the CSV data
                transaction = Transaction.from_csv_row(cleaned_text)
                result['transaction'] = transaction
                result['parsed_data'] = transaction.to_dict()
            except Exception as e:
                result['parsing_error'] = str(e)

            return result

        except Exception as e:
            error_result = {
                'text': None,
                'success': False,
                'error': str(e),
                'processing_status': 'failed'
            }
            print(f"Error extracting text: {e}")
            return error_result

if __name__ == "__main__":
    # Example usage
    try:
        ipp = ImagePostProcessing()
        result = ipp.extract_text_from_image("test_receipts/receipt_b.jpg")
        
        if result['success']:
            print("\nExtracted Data:")
            print("-" * 50)
            print("CSV Format:")
            print(result['text'])
            
            if 'transaction' in result:
                print("\nTransaction Details:")
                print(result['transaction'])
            elif 'parsing_error' in result:
                print(f"\nWarning: Error parsing transaction: {result['parsing_error']}")
            print("-" * 50)
        else:
            print(f"Failed to extract text: {result['error']}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure you have set the CLAUDE_API_KEY environment variable")
