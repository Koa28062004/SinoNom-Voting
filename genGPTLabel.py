import base64
import pandas as pd
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def run_openai(config):
  ORGANIZATION = config["apis"]["openai"]["organization"]
  API_KEY_GPT = config["apis"]["openai"]["api_key"]

  client = OpenAI(
    organization=ORGANIZATION,
    api_key=API_KEY_GPT
  )

  folder_path = config["paths"]["folder_path"]
  output_file = config["paths"]["output_file"]

  process(client, folder_path, output_file)

    
def process(client, folder_path, output_file):   
  if not os.path.exists(output_file):
      # Create a new DataFrame and save an empty Excel file with the correct structure
      df = pd.DataFrame(columns=["Filename", "GPT API"])
      df.to_excel(output_file, index=False)

  for filename in os.listdir(folder_path):
      file_path = os.path.join(folder_path, filename).replace("\\", "/")
      
      if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
          try:
              base64_image = encode_image(file_path)
              response = client.chat.completions.create(
              model="gpt-4o",
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
              new_row = pd.DataFrame({"Filename": [filename], "GPT API": [content]})
              existing_data = pd.read_excel(output_file)
              updated_data = pd.concat([existing_data, new_row], ignore_index=True)
              updated_data.to_excel(output_file, index=False)
              print(f"Result for {filename} saved to {output_file}")

          except Exception as e:
              print(f"An error occurred with file {filename}: {e}")
      else:
          print(f"Skipped non-image file: {filename}")