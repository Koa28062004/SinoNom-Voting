import os
import requests

input_file = "GPT_part1.txt"
output_file = "GPT_part1_trans.txt"

start_index = 2118

domain = "https://tools.clc.hcmus.edu.vn"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

with open(input_file,"r",encoding="utf-8") as infile:
    lines = infile.readlines()

with open(output_file,'a',encoding="utf-8") as outfile:
    for idx, line in enumerate(lines[start_index:], start=start_index):
        # Split the line into picture name and content
        print(f'Processing line number {idx}:')
        parts = line.strip().split("\t")
        if len(parts) != 2:
            outfile.write(line)  # Write invalid lines as-is
            continue
        image_path, text = parts
        #print(text)
        ocr_url = f"{domain}/api/web/clc-sinonom/sinonom-transliteration"
        payload = {
            "text": text 
        }

        ocr_response = requests.post(ocr_url, headers=headers, json=payload)
        if ocr_response.status_code == 200:
            ocr_data = ocr_response.json()
            if ocr_data.get("is_success") and ocr_data["data"].get("result_text_transcription"):
                result_text = ocr_data["data"]["result_text_transcription"]
                combined_text = "".join(result_text)
            else:
                print(f"Error in OCR response: {ocr_data.get('message', 'No message provided')}")
                exit()
        else:
            print(f"Error performing OCR: {ocr_response.status_code} - {ocr_response.text}")
            exit()
        if text == "nan":
            text = ""
            combined_text = ""
        print(combined_text)
        
        # Write the updated line to the output file
        outfile.write(f"{image_path}\t{text}\t{combined_text}\n")