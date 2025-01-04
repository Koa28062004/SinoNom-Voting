from googleapiclient.discovery import build
import json
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


my_api_key=API_KEY_GG # Your API key
my_cse_id=CSE_ID_GG # Your search engine ID

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

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    query = str(search_term).replace('&','*').replace('%','*').replace("?",'*')
    checkQuery = query.replace(' ','')
    if (checkQuery.count('*') == len(checkQuery)):
        return None, False
    query = f'"{query}"'
    res = service.cse().list(q=query, cx=cse_id, **kwargs).execute()
    if 'items' not in res:
        return None, False
    return res['items'], True
def save_row_to_excel(file_path, row, headers):
    try:
        if not os.path.exists(file_path):
            row_df = pd.DataFrame([row], columns=headers)
            row_df.to_excel(file_path, index=False, header=True)  # Write with headers
            print(f"File created and row saved: {file_path}")
        else:
            # If file exists, append the row
            with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                row_df = pd.DataFrame([row], columns=headers)
                startrow = writer.sheets['Sheet1'].max_row
                row_df.to_excel(writer, index=False, header=False, startrow=startrow)
            print(f"Row appended to file: {file_path}")

    except Exception as e:
        print(f"Error saving row to Excel: {e}")

def validateGoogle(input_file, output_file_excel, output_folder_json, listColumn):
    df = pd.read_excel(input_file)
    output_file = {}
    for column in listColumn:
        if ('Phien am' in column):
            new_column_name = column.replace(' Phien am', '') + '_GG Phien am'
        else:
            new_column_name = column + '_GG'

        if new_column_name not in df.columns:
            df[new_column_name] = None
        output_file[column] = output_folder_json + '/voting_checkGG_' + column + '.json'

    for idx, row in df.iterrows():
        filename = row['Filename']
        correctList = {}
        for column in listColumn:
            correctList[column] = False

        for column in listColumn:
            name_column = column.replace(' Phien am', '') + '_GG Phien am' if ('Phien am' in column) else column + '_GG'
            if (correctList['Voting_Fill Phien am'] == True and column == 'Voting_Fill'):
                df.at[idx, name_column] = ''
                row[name_column] = ''
                continue
            if (correctList['Voting_Fill_Without_Gemini Phien am'] == True and column == 'Voting_Fill_Without_Gemini'):
                df.at[idx, name_column] = ''
                row[name_column] = ''
                continue

            query = row[column]
            if query is None or pd.isna(query):  # Explicitly handle both None and NaN
                df.at[idx, name_column] = ''
                row[name_column] = ''
                continue

            results, isCorrect = google_search(query, my_api_key, my_cse_id, num=5)
            df.at[idx, name_column] = 'Correct' if isCorrect else 'Unknown'
            row[name_column] = 'Correct' if isCorrect else 'Unknown'
            if (results == None or isCorrect == False):
                print(f"No results found: {query}")
                continue
            correctList[column] = isCorrect
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
            saving_to_json(extracted_results, output_file[column])
        save_row_to_excel(output_file_excel, row, list(df.columns))


# Read the input Excel file
input_file = "label/thayDien_1_result.xlsx"
output_file_excel = "label/thayDien_1_result_checkbyGG.xlsx"
output_folder_json = "part1"
listColumn = ['Voting_Fill Phien am', 'Voting_Fill_Without_Gemini Phien am', 'Voting_Fill', 'Voting_Fill_Without_Gemini']
validateGoogle(input_file, output_file_excel, output_folder_json, listColumn)