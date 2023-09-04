# Import libraries
from PIL import ImageGrab
from dotenv import load_dotenv
from gui import *
import pytesseract
import openai
import sys
import os

# Initialize
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def perform_ocr(image, lang):
    text = pytesseract.image_to_string(image, lang=lang)
    return text

def translate_text(text, source_lang="English", target_lang="Chinese", debug=False):
    # Implement translation with GPT-4

    # Give GPT-4 a system prompt
    GPT_SYS_PROMPT = f'''You will get {source_lang} text from the OCR, 
    you job is to translate the text into {target_lang}.'''

    if debug:
        print(f"Input: {text}")
        print(f"Prompt: {GPT_SYS_PROMPT}")

    conversation = [
        {"role": "system", "content": GPT_SYS_PROMPT},
        {"role": "user", "content": text}
    ]
    
    response = openai.ChatCompletion.create(
        model = "gpt-4-0613",
        messages = conversation,
        max_tokens = 100,
        temperature = 0.5,
    )

    if debug:
        print(f"Response: {response}")
        print(f"conversation: {conversation}")
    
    if response['choices']:
        message = response['choices'][0]['message']['content']
        return message
    else:
        return "Translation failed."
    
# deprecated PIL implementation of screen capture
# coordinates are not converted properly
# def capture_screen(region):
#     # Implement screen capture
#     if region is None:
#         image = ImageGrab.grab()
#     else:
#         image = ImageGrab.grab(bbox=region)
#     # Save the image to a temporary file for debugging
#     image.save("temp.png")
#     return image


def map_to_tesseract_lang_code(human_readable_language):
    mapping = {
        "Japanese": "jpn",
        "English": "eng",
        "Chinese": "chi_sim",
        "Russian": "rus",
        "German": "deu",
    }
    return mapping.get(human_readable_language, "eng") # default to English

# Main loop
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()