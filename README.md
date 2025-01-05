# OCR Corpus and Voting Algorithm Documentation

## Corpus File Explanation

- **GPT API**: The OCR result from ChatGPT.
- **Gemini API**: The OCR result from Gemini.
- **Vision API**: The OCR result from Vision Cloud API.
- **Kandi API**: The OCR result from Kandianguji.
- **CLC API**: The OCR result from CLC Lab Tools.
- **Voted_Result**: The voted result after majority voting of the 5 OCR results.
- **Voting_Fill**: The result after filling `?` in the `Voted_Result` using ChatGPT:
  - `&`: Only one character available or empty in set of character.
  - `%`: ChatGPT cannot decide.
- **Voted_Result_Without_Gemini**: The voted result after majority voting of 4 OCR results (excluding Gemini).
- **Voting_Fill_Without_Gemini**: The result after filling `?` in the `Voted_Result_Without_Gemini` using ChatGPT:
  - `&`: Only one character available or empty in set of character.
  - `%`: ChatGPT cannot decide.
- **Voting_Fill_GG**: Validation of `Voting_Fill` using Google Custom Search JSON API.
- **Voting_Fill_Without_Gemini_GG**: Validation of `Voting_Fill_Without_Gemini` using Google Custom Search JSON API.
- **Check**: Manual validation of `Voting_Fill` and `Voting_Fill_Without_Gemini`:
  - `f`: All characters are correct.
  - `m`: At least one character in the sequence is correct. All recognized characters must be correct in terms of position and shape.
- **Remark**: Additional notes or comments.

---

## Voting Algorithm

### 2.1 Choosing the Base String
1. **Criteria**: Select the base string with the longest length among the candidates.
2. **Tie-Breaker**: If multiple strings share the maximum length, calculate a similarity score (e.g., using `SequenceMatcher`) to determine the most representative base string.

---

### 2.2 Filling `*` Characters Using Minimum Edit Distance
1. Using the chosen base string as the reference, apply the **Minimum Edit Distance (MED)** algorithm.
2. Align all candidate strings to the base string to fill the `*` characters.

---

### 2.3 Character-Level Voting
1. Iterate through each character position `i` in the base string:
   - Tally the characters from all candidate strings at position `i`.
   - A character is chosen as the **winner** if it appears in at least **half** of the candidate strings.
2. **Tie Case**: 
   - If multiple characters have the same highest frequency at position `i` and the tie includes characters other than `*`, mark the result at that position as `?` (indicating no clear winner).

---

### 2.4 Enhancing Voting Results Using LLM (ChatGPT)
1. At each character position `i` in the base string:
   - Collect the set of characters from all candidate strings at position `i`, excluding `*` if possible.
   - Send the collected character set and the intermediate voting result (from Step 3) to a **Large Language Model (LLM)** like ChatGPT.
2. The LLM evaluates the context and provides an appropriate character to fill in the voting result.
3. This step ensures that ambiguous or unclear cases are resolved intelligently.