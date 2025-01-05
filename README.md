# SinoNom-Voting
1. **Corpus file explanation:**
  - GPT API: The OCR result of ChatGPT
  - Gemini API: The OCR result of Gemini
  - Vision API: The OCR result of Vision Cloud API
  - Kandi API: The OCR result of Kandianguji
  - CLC API: The OCR result of CLC Lab Tools
  - Voted_Result: The voted result after majority voting of 5 OCR results
  - Voting_Fill: Filling in ? in the **Voted_Result** using ChatGPT (&: only 1 char available, %: ChatGPT cannot decide)
  - Voted_Result_Without_Gemini: The voted result after majority voting of 4 OCR results (excluding Gemini)
  - Voting_Fill_Without_Gemini: Filling in ? in the **Voted_Result_Without_Gemini** using ChatGPT ((&: only 1 char available, %: ChatGPT cannot decide)
  - Voting_Fill_GG: Validating **Voting_Fill** automatically using Google Custom Search JSON API 
  - Voting_Fill_Without_Gemini_GG: Validating **Voting_Fill_Without_Gemini** automatically using Google Custom Search JSON API 
  - Check: Manually validating  **Voting_Fill** and **Voting_Fill_Without_Gemini** (f: all chars are correct, m: >=1 char(s) in the sequence, all chars recoginsed must be correct in terms of position and shape).
  - Remark: Noting if needed
2. **Explanation Voting ALgorithm**
2.1 **Choosing the Base String**
- **Criteria**: Select the string (label) with the longest length among the candidates.
- **Tie-Breaker**: If multiple strings share the maximum length, calculate a similarity score (using SequenceMatcher) to determine the most representative base string.
2.2 **Filling * Characters Using Minimum Edit Distance**
- Using the chosen base string as the reference, apply the **Minimum Edit Distance (MED)** algorithm to fill the * characters in other strings by aligning them with the base string.
2.3 **Character-Level Voting**
- Iterate through each character position in the base string:
+ For each position *i*, tally the characters from all candidate strings at that position.
+ A character is chosen as the winner if it appears in at least half of the candidate strings.
+ Tie Case: If multiple characters have the same highest frequency at position *i*, and the tie includes characters other than *, mark the result at that position as ? (indicating no clear winner).
2.4 **Enhancing Voting Results Using LLM (ChatGPT)**
- At each position *i* in the base string:
+ Collect the set of characters from all candidate strings at position i, excluding * if possible.
+ Send the collected character set and the intermediate voting result (from Step 3) to a Large Language Model (LLM) like ChatGPT.
+ The LLM will evaluate the context and provide an appropriate character to fill in the voting result. This step ensures that ambiguous or unclear cases are resolved more intelligently.