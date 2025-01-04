import os
import time
import google.generativeai as genai

def process_image(filepath):
    """
    Process a single image file using Gemini API and extract transcription.
    """
    try:
        # Upload file and perform OCR
        sample_file = genai.upload_file(path=filepath)
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp")
        text = "OCR this image and provide only the transcription of visible characters."
        response = model.generate_content([text, sample_file])
        return response.text.strip()  # Return only the transcription
    except Exception as e:
        return f"Error processing {filepath}: {str(e)}"

def process_dataset(folder_path, output_file, api_key):
    """
    Process all images in the dataset folder and write results to a file.
    """
    genai.configure(api_key=api_key)
    if not os.path.exists(folder_path):
        print("Dataset folder not found.")
        return

    results = {}
    request_count = 0  # Initialize request counter

    with open(output_file, 'w') as f:
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                print(f"Processing {filename}...")
                result = process_image(filepath)
                results[filename] = result
                f.write(f"{filename}\t{result}\n")  # Write results in the desired format

                request_count += 1
                # Wait for 30 seconds after every 5 requests
                if request_count % 5 == 0:
                    print("Pausing for 30 seconds...")
                    time.sleep(30)

    print("\nProcessing complete. Results written to res.txt")

def run_gemini(config):
    api_key = config["apis"]["gemini"]["api_key"]
    folder_path = config["paths"]["folder_path"]
    output_file = config["paths"]["output_file"]
    process_dataset(folder_path, output_file, api_key)