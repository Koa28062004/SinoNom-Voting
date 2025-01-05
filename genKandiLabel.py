import json
import requests
import base64
from dotenv import load_dotenv
import pandas as pd
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from utils import save_api_results_to_excel, clean_text

# Load environment variables from the .env file
load_dotenv()

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def dump_to_json(data, output_file):
    """Dumps the data to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def send_ocr_request(
    api_token, 
    email,
    image_path,
    char_ocr=False,
    det_mode="auto",
    image_size=0,
    return_position=False,
    return_choices=False,
):
    """Sends a request to the OCR API to process an ancient book image."""
    # Encode the image
    image_base64 = encode_image_to_base64(image_path)

    # Define the payload
    payload = {
        "token": api_token,
        "email": email,
        "image": image_base64,
        "char_ocr": char_ocr,
        "det_mode": det_mode,
        "image_size": image_size,
        "return_position": return_position,
        "return_choices": return_choices,
    }

    # Define the headers
    headers = {"Content-Type": "application/json"}

    # Send the request to the OCR API
    # response = requests.post(
    #     "https://ocr.kandianguji.com/ocr_api", json=payload, headers=headers
    #     timeout=(10, 30)
    # )

    # # Check the response status and return the result
    # if response.status_code == 200:
    #     return response.json()  # Return the parsed JSON response if successful
    # else:
    #     response.raise_for_status()  # Raise an error if the request failed
    try:
        response = requests.post(
            "https://ocr.kandianguji.com/ocr_api", 
            json=payload, 
            headers=headers,
            timeout=30  # Adjust the timeout value as needed
        )
        response.raise_for_status()
        return response.json()  # Return the parsed JSON response if successful
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again later.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def process(image_folder, output_file, api_token, email):
    for image_file in os.listdir(image_folder):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            image_path = os.path.join(image_folder, image_file)
            print("Processing image:", image_path)
            #Send OCR request and get the response
            response = send_ocr_request(
                api_token, 
                email,
                image_path,
                char_ocr=True,
                det_mode="sp",
                image_size=500,
                return_position=True,
                return_choices=True,
            )
            if response['message'] == 'error':
                print("Error processing image:", image_path)
                break
            labels = response['data']['texts']
            final_label = ""
            for label in labels:
                final_label += label
        
            # Append the result to the existing Excel file
            save_api_results_to_excel(image_file, "Kandi API", clean_text(final_label), output_file)

def run_kandi(config):
  # Read API token and email from environment variables
  api_token = config["apis"]["kandi"]["api_token"]
  email = config["apis"]["kandi"]["email"]

  image_folder = config["paths"]["folder_path"]
  output_file = config["paths"]["output_file"]

  process(image_folder, output_file, api_token, email)
