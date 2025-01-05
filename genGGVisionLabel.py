import os
from google.cloud import vision
import pandas as pd
from utils import save_api_results_to_excel, clean_text

def detect_text(path):
  client = vision.ImageAnnotatorClient()
  with open(path, "rb") as image_file:
      content = image_file.read()
  image = vision.Image(content=content)

  try:
      response = client.text_detection(image=image)
      texts = response.text_annotations
      ocr_text = []
      for text in texts:
          ocr_text.append(f"\r\n{text.description}")
      if response.error.message:
          raise Exception(
              "{}\nFor more info on error messages, check: "
              "https://cloud.google.com/apis/design/errors".format(response.error.message)
          )
  except Exception as e:
      print(f"Error processing image {path}: {e}")
      return None
  
  if not texts:
      print(f"No text detected in the image: {path}")
      return None
  return texts[0].description
        
def run_ggvision(config):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config["apis"]["ggVision"]["google_credentials"]
    path = config["paths"]["folder_path"]
    output_file = config["paths"]["output_file"]
    fileList = os.listdir(path)
  
    for file in fileList:
        path_file = os.path.join(path, file)
        text = detect_text(path_file)
        if text is None:
            continue
        text = text.replace('\n','')
        
        # Append the result to the existing Excel file
        save_api_results_to_excel(file, "Vision API", clean_text(text), output_file)