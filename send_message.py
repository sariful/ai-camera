import os
import requests
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(
        text: Optional[str] = None, 
        image_path: Optional[str] = None, 
        chat_id: Optional[str] = None
    ) -> bool:
    
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return False
    
    # Use provided chat_id or fall back to default
    target_chat_id = chat_id or CHAT_ID
    if not target_chat_id:
        print("Error: No chat ID provided or found in environment variables")
        return False

    # If neither text nor image is provided, return False
    if not text and not image_path:
        print("Error: Must provide either text or image_path")
        return False

    try:
        # Send image if provided
        if image_path:
            if not os.path.exists(image_path):
                print(f"Error: Image file not found at {image_path}")
                return False
                
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {'chat_id': target_chat_id}
                
                # Add caption if text is provided
                if text:
                    data['caption'] = text
                    
                response = requests.post(url, data=data, files=files)
        
        # Send text only if no image is provided but text is
        elif text:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            response = requests.post(url, data={
                "chat_id": target_chat_id,
                "text": text
            })
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False
    
if __name__ == "__main__":
    # Example usage
    success = send_telegram_message(text="Hello from AI Camera!", image_path="assets/logo.png")
    print("Message sent successfully" if success else "Failed to send message")