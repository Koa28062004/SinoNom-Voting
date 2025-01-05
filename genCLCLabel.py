import os
import requests
import pandas as pd
import json
import time
from PIL import Image
from utils import save_api_results_to_excel, clean_text


## Also call API CLC but takes image folder as input

domain = "https://tools.clc.hcmus.edu.vn"

# Headers for API
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Function to check if image width is larger than height
def is_width_larger_than_height(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width > height
    except Exception as e:
        print(f"Error checking dimensions for {image_path}: {e}")
        return False

def run_clc(config):
  image_folder = config["paths"]["folder_path"]
  output_file = config["paths"]["output_file"]

  process(image_folder, output_file)

def process(image_folder, output_file):
    for image in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image)
        if not image_path.lower().endswith((".jpg", ".jpeg", ".png")):
            continue  # Skip non-image files

        print(f"Processing image: {image_path}")

        # Step 1: Upload the image
        try:
            with open(image_path, 'rb') as image_file:
                # Set up the files parameter for the POST request
                files = {'image_file': image_file}

                # Send the POST request to upload the image
                upload_url = f"{domain}/api/web/clc-sinonom/image-upload"
                upload_response = requests.post(upload_url, headers=headers, files=files)

                # Check if upload was successful
                if upload_response.status_code == 200:
                    upload_data = upload_response.json()
                    if upload_data.get("is_success") and upload_data["data"].get("file_name"):
                        ocr_file_name = upload_data["data"]["file_name"]
                    else:
                        print(f"Error: {upload_data.get('message', 'No message provided')}")
                        time.sleep(65)
                        image_file.seek(0)
                        upload_response = requests.post(upload_url, headers=headers, files=files)
                        if upload_response.status_code == 200:
                            upload_data = upload_response.json()
                            if upload_data.get("is_success") and upload_data["data"].get("file_name"):
                                ocr_file_name = upload_data["data"]["file_name"]
                            else:
                                print(f"Error: {upload_data.get('message', 'No message provided')}")
                                exit()
                        else:
                            print(f"Error uploading image: {upload_response.status_code} - {upload_response.text}")
                            exit()
                else:
                    print(f"Error uploading image: {upload_response.status_code} - {upload_response.text}")
                    exit()
        except FileNotFoundError:
            print(f"File not found: {image_path}")
            exit()

        # Step 2: Perform OCR on the uploaded image
        ocr_url = f"{domain}/api/web/clc-sinonom/image-ocr"
        ocr_payload = {
            "ocr_id": 3,
            "file_name": ocr_file_name
        }

        ocr_response = requests.post(ocr_url, headers=headers, json=ocr_payload)
        if ocr_response.status_code == 200:
            ocr_data = ocr_response.json()
            if ocr_data.get("is_success") and ocr_data["data"].get("result_ocr_text"):
                result_ocr_text = ocr_data["data"]["result_ocr_text"]
                combined_text = "".join(result_ocr_text)

                # Reverse text if width is larger than height
                if is_width_larger_than_height(image_path) and combined_text != "No result OCR":
                    combined_text = combined_text[::-1]  # Reverse the text
                
                # Write the updated line to the output file
                save_api_results_to_excel(image, "CLC API", clean_text(combined_text), output_file)
            else:
                print(f"Error in OCR response: {ocr_data.get('message', 'No message provided')}" )
        else:
            print(f"Error performing OCR: {ocr_response.status_code} - {ocr_response.text}")

    print("Processing complete. Updated file written to:", output_file)