import pandas as pd
import openpyxl
import difflib
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv
from utils import transliteration, validateByGoogle, saving_to_json
import yaml

load_dotenv()

def save_row_to_excel(file_path, row, headers):
    try:
        with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
            row_df = pd.DataFrame([row], columns=headers)
            row_df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

    except Exception as e:
        print(f"Error saving row to Excel: {e}")
# Function to find the best sequence among longest ones
def find_best_sequence(max_sequences, sequences):
    best_sequence = None
    best_score = float("-inf")
    for seq in max_sequences:
        score = sum(
            difflib.SequenceMatcher(None, seq, other).ratio()
            for other in sequences if seq != other
        )
        if score > best_score:
            best_sequence = seq
            best_score = score
    return best_sequence

# Function to pad strings using a base sequence
def chatGPTsemantic(client, model, string, listChar):
    new_string = list(string)
    for index, char in enumerate(string):
        if char == '?':
            chars_list = [char for char in listChar.pop(0) if char != '*']
            # Remove duplicates while preserving the order
            seen = set()
            unique_chars_list = [char for char in chars_list if not (char in seen or seen.add(char))]
            if (len(chars_list) <= 1):
                new_string[index] = '&'
                continue
            response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Fill in the first ? in the sequence '" + "".join(new_string) + "' from the options: " + ", ".join(unique_chars_list) + " Don't generate new characters. Print 'No appropriate option' if there are no options that fit best semantically. Otherwise print only the chosen character. Don't give explanations.",
                            },
                        ],
                    }
                ],
            )
            content = response.choices[0].message.content
            if (content == 'No appropriate option' or content == 'No appropriate option.'):
                new_string[index] = '%'
            else:
                if (len(content) == 1):
                    new_string[index] = content
    return "".join(new_string)

def minimum_edit_distance_with_actions(base, target):
    """
    Computes the minimum edit distance and prints the actions to transform the target string into the base string.

    :param base: The base string.
    :param target: The target string.
    :return: The minimum edit distance and the sequence of actions.
    """
    m, n = len(base), len(target)

    # Initialize a matrix for storing distances
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill the base cases for deletions and insertions
    for i in range(m + 1):
        dp[i][0] = i  # Deletions
    for j in range(n + 1):
        dp[0][j] = j  # Insertions

    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if base[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # Characters match
            else:
                dp[i][j] = min(
                    dp[i - 1][j],      # Deletion
                    dp[i][j - 1],      # Insertion
                    dp[i - 1][j - 1]   # Substitution
                ) + 1

    # Backtrack to find actions
    actions = []
    i, j = m, n
    new_string = ""
    while i > 0 or j > 0:
        if i > 0 and j > 0 and base[i - 1] == target[j - 1]:
            # No action needed for matching characters
            actions.append(f"Keep '{base[i - 1]}'")
            new_string += base[i - 1]
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            # Substitution
            actions.append(f"Substitute '{target[j - 1]}' with '{base[i - 1]}'")
            new_string += base[i - 1]
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            # Deletion
            actions.append(f"Delete '{base[i - 1]}'")
            i -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            # Insertion
            actions.append(f"Insert '{target[j - 1]}'")
            new_string += '*'
            j -= 1
    return new_string[::-1]

# Voting algorithm
def voting_algorithm(client, model, row):
    # Extract non-empty entries
    
    entries = [str(value) if pd.notna(value) and str(value).strip() else "" for value in row]
    if not entries:
        return ""  # Return empty if there are no valid entries
    # Find the longest sequences
    max_length = max(len(entry) for entry in entries)
    longest_sequences = [entry for entry in entries if len(entry) == max_length]
    # Choose the best sequence as the base
    base_sequence = find_best_sequence(longest_sequences, entries)

    # Pad all entries to match the base sequence
    padded_sequences = [minimum_edit_distance_with_actions(entry, base_sequence) for entry in entries]
    # Perform voting
    result = []
    chars_list = []
    vote_number = len(entries) // 2 if len(entries) % 2 == 0 else (len(entries) // 2) + 1
    for i in range(len(base_sequence)):
        chars = [seq[i] for seq in padded_sequences]
        counter = Counter(chars)
        most_common = counter.most_common(2)
        if (most_common[0][1] >= vote_number):
            if (len(most_common) > 1):
                if (most_common[0][1] == most_common[1][1]):
                    if (most_common[0][0] != '*' and most_common[1][0] != '*'):
                        result.append('?')
                        chars_list.append(chars)
                    else:
                        if (most_common[0][0] != '*'):
                            result.append(most_common[0][0])
                        else:
                            result.append(most_common[1][0])
                else:
                    if (most_common[0][0] == '*'):
                        result.append('?')
                        chars_list.append(chars)
                    else:
                        result.append(most_common[0][0])
            else:
                result.append(most_common[0][0])
        else:
            result.append('?')
            chars_list.append(chars)

    voted_string = ''.join(result)
    if (voted_string.count('?') == len(voted_string)):
        return voted_string, voted_string.replace('?', '&')
    
    LLM_voting = chatGPTsemantic(client, model, voted_string, chars_list)
    return voted_string, LLM_voting
def process_data_immediate_save(client, model, api_search, cse_id,  data, output_file, folder_json, listCol, withoutGemini):
    headers = list(data.columns) + (['Voted_Result', 'Voting_Fill', 'Voting_Fill Phien am', 'Voting_Fill_GG', 'Voting_Fill_GG Phien am'] if (not withoutGemini) else ['Voted_Result_Without_Gemini', 'Voting_Fill_Without_Gemini', 'Voting_Fill_Without_Gemini Phien am', 'Voting_Fill_Without_Gemini_GG', 'Voting_Fill_Without_Gemini_GG Phien am'])
    if withoutGemini:
        listCol.remove('Gemini API')
        data[['Voted_Result_Without_Gemini', 'Voting_Fill_Without_Gemini', 'Voting_Fill_Without_Gemini Phien am', 'Voting_Fill_Without_Gemini_GG', 'Voting_Fill_Without_Gemini_GG Phien am']] = ''
    else:
        data[['Voted_Result', 'Voting_Fill', 'Voting_Fill Phien am', 'Voting_Fill_GG', 'Voting_Fill_GG Phien am']] = ''
    data.iloc[:0].to_excel(output_file, index=False)

    for idx, row in data.iloc[0:].iterrows():
        try:
            print('Voting row:', row.iloc[0])
            row_values = [row[col] for col in listCol if col in row]
            voting, LLM_voting = voting_algorithm(client, model, row_values)
            if withoutGemini:
                row['Voted_Result_Without_Gemini'] = voting
                row['Voting_Fill_Without_Gemini'] = LLM_voting
                row['Voting_Fill_Without_Gemini Phien am'] = transliteration(LLM_voting)
                results, isCorrect = validateByGoogle(api_search, cse_id, row['Voting_Fill_Without_Gemini Phien am'], row.iloc[0])
                row['Voting_Fill_Without_Gemini_GG Phien am'] = 'Correct' if isCorrect else 'Unknown'
                if (isCorrect == True):
                    saving_to_json(results, folder_json + '/voting_checkGG_Voting_Fill_Without_Gemini_Trans.json')
                else:
                    resultsOCR, isCorrectOCR = validateByGoogle(api_search, cse_id, row['Voting_Fill_Without_Gemini'], row.iloc[0])
                    row['Voting_Fill_Without_Gemini_GG'] = 'Correct' if isCorrectOCR else 'Unknown'
                    if (isCorrectOCR == True):
                        saving_to_json(resultsOCR, folder_json + '/voting_checkGG_Voting_Fill_Without_Gemini.json')
    
            else:
                row['Voted_Result'] = voting
                row['Voting_Fill'] = LLM_voting
                row['Voting_Fill Phien am'] = transliteration(voting)
                
                results, isCorrect = validateByGoogle(api_search, cse_id, row['Voting_Fill Phien am'], row.iloc[0])
                row['Voting_Fill_GG Phien am'] = 'Correct' if isCorrect else 'Unknown'
                if (isCorrect == True):
                    saving_to_json(results, folder_json + '/voting_checkGG_Voting_Fill_Trans.json')
                else:
                    resultsOCR, isCorrectOCR = validateByGoogle(api_search, cse_id, row['Voting_Fill'], row.iloc[0])
                    row['Voting_Fill_GG'] = 'Correct' if isCorrectOCR else 'Unknown'
                    if (isCorrectOCR == True):
                        saving_to_json(resultsOCR, folder_json + '/voting_checkGG_Voting_Fill.json')
            
            save_row_to_excel(output_file, row, headers)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            print("Halting process.")
            return False

    return True

def process(client, model, api_search, cse_id, input_file, output_file, folder_json, withoutGemini):
    listAPI = ['GPT API', 'Kandi API', 'Vision API', 'CLC API', 'Gemini API'] # List of columns to consider for voting
    try:
        data = pd.read_excel(input_file)
        if not process_data_immediate_save(client, model, api_search, cse_id, data, output_file, folder_json, listAPI, withoutGemini):
            print("Process terminated due to an error.")
        else:
            print(f"Voting results saved to: {output_file}")
    except Exception as e:
        print(f"Critical error loading file or processing data: {e}")

def run_voting(config, withoutGemini=False):
  ORGANIZATION = config["apis"]["openai"]["organization"]
  API_KEY_GPT = config["apis"]["openai"]["api_key"]
  api_search = config["apis"]["ggSearch"]["api_key"]
  cse_id = config["apis"]["ggSearch"]["cse_id"]
  model = config["apis"]["openai"]["model_Voting"]

  client = OpenAI(
    organization=ORGANIZATION,
    api_key=API_KEY_GPT
  )

  input_file = config["paths"]["output_file"] # File label by 5 APIs
  output_file = config["paths"]["output_file_voting"] # File save voting result
  folder_json = config["paths"]["folder_json_path"]
  process(client, model, api_search, cse_id, input_file, output_file, folder_json, withoutGemini)

CONFIG_FILE = "apiConfig.yaml"

def load_config():
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = load_config()
    run_voting(config)