from googleapiclient.discovery import build
import json
import pandas as pd
import requests
import os

def save_api_results_to_excel(filename, api_name, api_data, excel_file="output.xlsx"):
    """
    Save API results to an Excel file in append/update mode.

    Parameters:
        filename (str): The filename associated with the API results.
        api_name (str): The column name for the API.
        api_data (str): The result from the API.
        excel_file (str): Path to the Excel file.
    """
    # Check if the Excel file exists
    if os.path.exists(excel_file):
        # Load the existing Excel file
        df = pd.read_excel(excel_file, engine="openpyxl")
    else:
        # Create an empty DataFrame with necessary columns
        df = pd.DataFrame(columns=["Filename", "GPT API", "CLC API", "Vision API", "Kandi API", "Gemini API"])

    # Check if the filename already exists in the file
    if filename in df["Filename"].values:
        # Update the row for the filename
        df.loc[df["Filename"] == filename, api_name] = api_data
    else:
        # Add a new row for the filename with the API result
        new_row = {"Filename": filename, api_name: api_data}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the DataFrame back to the Excel file
    df.to_excel(excel_file, index=False, engine="openpyxl")
    print(f"Saved data for {filename} to column {api_name} in {excel_file}")
def saving_to_json(data, output_file):

    if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
        old_data = []
    else:
        try:
            with open(output_file, "r", encoding="utf-8") as file:
                old_data = json.load(file)
        except json.JSONDecodeError:
            old_data = []
    old_data.append(data)
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(old_data, file, indent=4, ensure_ascii=False)

def is_nom_or_chinese(char):
    """Check if a character is in the Nom or Chinese Unicode range."""
    codepoint = ord(char)
    return (
        (0x4E00 <= codepoint <= 0x9FFF) or  # CJK Unified Ideographs
        (0x3400 <= codepoint <= 0x4DBF) or  # CJK Unified Ideographs Extension A
        (0x20000 <= codepoint <= 0x2A6DF) or  # CJK Unified Ideographs Extension B
        (0x2A700 <= codepoint <= 0x2B81F) or  # CJK Unified Ideographs Extensions C-G
        (0xF900 <= codepoint <= 0xFAFF) or  # CJK Compatibility Ideographs
        (0x2FF0 <= codepoint <= 0x2FFF) or  # Ideographic Description Characters
        (0x31C0 <= codepoint <= 0x31EF)  # CJK Strokes
    )

def clean_text(input_text):
    """Filter input text to include only Nom or Chinese characters."""
    return ''.join(char for char in input_text if is_nom_or_chinese(char))
def transliteration(input_text):
    domain = "https://tools.clc.hcmus.edu.vn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    ocr_url = f"{domain}/api/web/clc-sinonom/sinonom-transliteration"
    payload = {
        "text": input_text 
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
    if input_text == "nan":
        input_text = ""
        combined_text = ""
    return combined_text

def validateByGoogle(api_search, cse_id, query, filename):
    results, isCorrect = google_search(query, api_search, cse_id, num=5)
    if (isCorrect):
        extracted_results = {
            'filename': filename,
            'label': query,
            'isCorrect': isCorrect,
            'results': []
        }
        contents = []
        print(f"Results for query: {query}")
        for result in results:
            content = {
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "og:title": result["pagemap"]["metatags"][0].get("og:title") if "pagemap" in result and "metatags" in result["pagemap"] else None,
                "og:description": result["pagemap"]["metatags"][0].get("og:description") if "pagemap" in result and "metatags" in result["pagemap"] else None,
                "og:image": result["pagemap"]["metatags"][0].get("og:image") if "pagemap" in result and "metatags" in result["pagemap"] else None,
            }
            contents.append(content)
        extracted_results['results'] = contents
        return extracted_results, isCorrect
    else:
        return None, isCorrect
        
def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    query = str(search_term).replace('&', '*').replace('%', '*').replace("?", '*')
    checkQuery = query.replace(' ', '')
    if checkQuery.count('*') == len(checkQuery):
        return None, False
    query = f'"{query}"'
    
    # Include num argument in the API call if provided in kwargs
    num = kwargs.get("num", 5)  # Default to 10 if num is not provided
    res = service.cse().list(q=query, cx=cse_id, **kwargs).execute()
    
    if 'items' not in res:
        return None, False
    return res['items'], True


