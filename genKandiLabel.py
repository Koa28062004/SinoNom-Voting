import json
import requests
import base64
from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

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

def draw_bounding_boxes(image_path, response_data):
    """Draws bounding boxes on the image based on the OCR response data in a JSON file."""
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    height = response_data.get("data", {}).get("height")
    width = response_data.get("data", {}).get("width")
    scaleHeight = image.height / height
    scaleWidth = image.width / width

    # Loop through each line in the response and draw the bounding box for the line and each word
    for line in response_data.get("data", {}).get("text_lines", []):
        # Draw bounding box for the entire line
        line_points = line["position"]
        x_values = [point[0] for point in line_points]
        y_values = [point[1] for point in line_points]
        x1, y1, x2, y2 = min(x_values)*scaleWidth, min(y_values)*scaleHeight, max(x_values)*scaleWidth, max(y_values)*scaleHeight

        # Draw bounding box for each word within the line
        for word in line["words"]:
            word_x1, word_y1, word_x2, word_y2 = word["position"]
            draw.rectangle([word_x1*scaleWidth, word_y1*scaleHeight, word_x2*scaleWidth, word_y2*scaleHeight], outline="red", width=2)  # Word bounding box in red

    # Display the image with bounding boxes
    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    plt.axis("off")
    plt.show()

    # Save the image with bounding boxes if needed
    image.save("output_with_bounding_boxes.jpg")

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
    response = requests.post(
        "https://ocr.kandianguji.com/ocr_api", json=payload, headers=headers
    )

    # Check the response status and return the result
    if response.status_code == 200:
        return response.json()  # Return the parsed JSON response if successful
    else:
        response.raise_for_status()  # Raise an error if the request failed

def process(image_folder, output_folder, api_token, email):
  with open(output_folder, 'a', encoding='utf-8') as file:
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
              file.write(image_path + '\t' + final_label + '\n')

def run_kandi(config):
  # Read API token and email from environment variables
  api_token = config["apis"]["kandi"]["api_token"]
  email = config["apis"]["kandi"]["email"]

  image_folder = config["paths"]["folder_path"]
  output_folder = config["paths"]["output_file"]

  process(image_folder, output_folder, api_token, email)
