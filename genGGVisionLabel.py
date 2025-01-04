import os
from google.cloud import vision

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

# processedList = []
# with open('/Volumes/WD/Part3/go_cropped_reorder.txt','r',encoding='utf-8') as f:
#     lines = f.readlines()
#     for line in lines:
#         line = line.strip()
#         if line == '':
#             continue
#         file = line.split('\t')[0]
#         processedList.append(file)

# for file in fileList:
#     if file in processedList:
#         print(f"File {file} already processed")
#         fileList.remove(file)
        
def run_ggvision(config):
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config["apis"]["ggVision"]["google_credentials"]
  path = config["paths"]["folder_path"]
  path_label = config["paths"]["path_label"]
  fileList = os.listdir(path)
  
  with open(path_label, 'w',encoding='utf-8') as f:
    for file in fileList:
        text = detect_text(path+file)
        if text is None:
            continue
        text = text.replace('\n','')
        f.write(file+'\t'+text+'\n')