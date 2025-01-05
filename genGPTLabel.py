import base64
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils import save_api_results_to_excel, clean_text

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def run_openai(config):
  ORGANIZATION = config["apis"]["openai"]["organization"]
  API_KEY_GPT = config["apis"]["openai"]["api_key"]
  model = config["apis"]["openai"]["model_OCR"]

  client = OpenAI(
    organization=ORGANIZATION,
    api_key=API_KEY_GPT
  )

  folder_path = config["paths"]["folder_path"]
  output_file = config["paths"]["output_file"]

  process(client, model, folder_path, output_file)
    
def process(client, model, folder_path, output_file):   

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename).replace("\\", "/")
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            try:
                base64_image = encode_image(file_path)
                response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is written (from left to right) in this image (only result, no explanation)?",
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                )
                content = response.choices[0].message.content
                print(content)
                
                # Append the result to the existing Excel file
                save_api_results_to_excel(filename, "GPT API", clean_text(content), output_file)

            except Exception as e:
                print(f"An error occurred with file {filename}: {e}")
        else:
            print(f"Skipped non-image file: {filename}")