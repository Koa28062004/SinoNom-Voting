# SinoNom-Voting
1. Corpus file explanation:
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
3. 
