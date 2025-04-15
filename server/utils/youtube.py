from urllib.parse import urlparse, parse_qs
import os
import re
import logging
import asyncio
import random
import time
import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from server.utils.backgound_task import background_pinecone_task # Check if this needs async adaptation

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Gemini API Key Management (Consistent with other files) ---
gemini_keys = [
    "GEMINI_API_KEY_11",
    "GEMINI_API_KEY_12",
    "GEMINI_API_KEY_13",
    "GEMINI_API_KEY_14",
    "GEMINI_API_KEY_15",
    "GEMINI_API_KEY_16",
    "GEMINI_API_KEY_17",
    "GEMINI_API_KEY_18",
    "GEMINI_API_KEY_19",
    "GEMINI_API_KEY_20"
]

def get_random_key_name():
    return random.choice(gemini_keys)

# --- Helper function for running sync code in thread (Consistent) ---
async def run_sync_in_thread(func, *args, **kwargs):
    """Runs a synchronous function in a separate thread."""
    loop = asyncio.get_running_loop()
    from functools import partial
    func_call = partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)

# --- Synchronous helper for Gemini API calls (Consistent) ---
def _sync_generate_content(model_name, prompt_string):
    """Synchronous call to Gemini API."""
    try:
        gemini_ai_key = os.getenv(get_random_key_name())
        if not gemini_ai_key:
            logging.error(f"Gemini API key (tried {get_random_key_name()}) not found in environment.")
            return "[ERROR: API key not configured]"
        genai.configure(api_key=gemini_ai_key)
        model_instance = genai.GenerativeModel(model_name)
        response = model_instance.generate_content(prompt_string)
        if not response.parts:
             feedback = getattr(response, 'prompt_feedback', None)
             block_reason = getattr(feedback, 'block_reason', 'Unknown')
             safety_ratings = getattr(feedback, 'safety_ratings', 'N/A')
             logging.warning(f"Gemini returned no content. Block Reason: {block_reason}, Safety Ratings: {safety_ratings}")
             return f"[ERROR: Gemini generation failed or blocked - Reason: {block_reason}]"
        return response.text
    except Exception as e:
        logging.error(f"Gemini API call failed for model {model_name}: {e}", exc_info=True)
        return f"[ERROR: Gemini API call failed - {e}]"

# --- YouTube Video ID Extraction (kept for potential other uses, but not used by generate_youtube_summary anymore) ---
def extract_video_id(url):
    """Extracts the YouTube video ID from various URL formats."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                return query_params.get("v", [None])[0]
            if parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/embed/')[1]
            if parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/v/')[1]
        return None
    except Exception as e:
        logging.error(f"Error parsing YouTube URL '{url}': {e}")
        return None

# --- Synchronous Transcript Fetching (kept for potential other uses) --- 
def _sync_get_transcript(video_id):
    """Synchronous function to fetch YouTube transcript."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-IN'])
        # Combine transcript parts into a single string
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        logging.error(f"Could not retrieve transcript for video ID {video_id}: {e}")
        # Handle different exception types if needed (e.g., TranscriptsDisabled, NoTranscriptFound)
        return None

# --- Asynchronous Transcript Fetching Wrapper (kept for potential other uses) ---
async def get_transcript_from_youtube(video_id):
    """Asynchronously fetches YouTube transcript text by wrapping the sync call."""
    if not video_id:
        logging.error("No video ID provided to get_transcript_from_youtube.")
        return None
    # Run the synchronous youtube_transcript_api call in a separate thread
    transcript_text = await run_sync_in_thread(_sync_get_transcript, video_id)
    return transcript_text

# --- Transcript Summarization (using Gemini) --- 
async def transcript_summary(transcript_text): # Takes transcript text
    """Generates a summary for the given transcript text using Gemini asynchronously."""
    if not transcript_text:
        logging.error("No transcript text provided for summarization.")
        return "[ERROR: No transcript text to summarize]"

    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- START --- 
    prompt = (
    "### Instruction:\n"
    "You are a highly advanced financial AI assistant specializing in analyzing company information from YouTube video transcripts. "
    "You will be provided with a transcript from a YouTube video. Extract **all relevant financial insights** and company data without omission. "
    "Your role is to assist investors, traders, and financial professionals by identifying crucial financial metrics, trends, and strategies.\n\n"

    "**Response Constraints:**\n"
    "- Use only the retrieved document segments.\n"
    "- Do **not** generate information beyond what is given, assume missing data, or provide opinions.\n"
    "- If the retrieved data is insufficient, state: *'The retrieved data does not provide enough information to answer this question.'*\n"
    "- **Do not** add introductions, summaries, or unnecessary commentary—only structured financial insights.\n\n"
    "-**Do Not** add any data that is not available such as **DO NOT ADD LINES LIKE *The retrieved data does not lend itself to complex visual representations beyond tables and structured lists. The table above summarizes key financial metrics."

    "**Guidelines:**\n"
    "- **Transcript guidelines: IF the transcripts are not related to finance **DO NOT FOLLOW OUTPUT FORMAR** simply write that **GIVEN LINK DOESN'T CONTAIN ANY FINANCIAL INFORMATION** in markdown format"
    "- **Objective & Data-Driven:** Use only the retrieved data—no assumptions or guesses. Every insight must be justified with extracted figures.\n"
    "- **Investment-Focused:** Provide key insights relevant for evaluating the company's financial health, investment potential, and future growth outlook.\n"
    "- **Comprehensive Analysis:** Generate an in-depth company summary, explaining strengths, risks, trends, key financial metrics, and future projections with supporting data points.\n"
    "- **Comparative Evaluation:** Compare financial ratios, growth trends, and industry benchmarks where applicable, ensuring all comparisons are backed by figures.\n"
    "- **Structured & Visual:** Use tables, bullet points, and structured formatting to enhance clarity and comprehension.\n"
    "- **Predictive Insights:** Where possible, forecast future performance based on historical trends, numerical metrics, and financial patterns. Ensure every prediction is justified with solid reasoning and past data trends.\n"
    "- Hard Rule: Do not add the ```html tag or any code block formatting such as triple backticks (```) before the output. The response must start directly with the header (e.g., # 📊 [Company Name] Overview) without any code block wrapping."
    "-**DO NOT** Add **```markdown** tag in the front of the response"
    "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <span style='color:green;'>green text</span>, and negative data should be highlighted in red <span style='color:red;'>red text</span>. Ensure that the output does not use Markdown for color formatting.\n\n"
    "-**Do Not** add any data that is not available such as **DO NOT ADD LINES LIKE *The retrieved data does not lend itself to complex visual representations beyond tables and structured lists. The table above summarizes key financial metrics."
    "## Extracted Segment from the Video:\n"
    "All financial numbers representing money should be expressed only in the **₹ (Indian Rupee)** format. If any data is in a different currency or format, it must be converted to the **₹** format.\n\n"
    "```\n"
    f"{transcript_text}\n"
    "```\n\n"


    "**Task:**\n"
    "Based solely on the provided data, generate a detailed company insight report including:\n"
    "1. **Company Overview** – Key highlights from the report, explained with numerical data.\n"
    "2. **Financial Health Evaluation** – Revenue trends, profitability, debt levels, and other critical metrics with clear breakdowns and justifications.\n"
    "3. **Investment Viability** – Strengths, weaknesses, risks, and potential opportunities, all elaborated with evidence from financial statements.\n"
    "4. **Comparative Analysis** – Performance trends against industry standards where data allows, supported by benchmarks and figures.\n"
    "5. **Key Financial Metrics Table** – Present structured financial data where applicable with detailed explanations.\n"
    "6. **Predictive Analysis** – Forecast future financial performance based on historical data trends, numerical progression, and reasonable assumptions, ensuring every prediction has strong supporting evidence.\n"
    "7. **Visual Financial Representation** – If applicable, structure key financial data in a visually intuitive format.\n\n"

    "**Output Format:**\n"
    "# 📊 [Company Name] Overview\n"
    "## 💰 Summary\n"
    "[Provide a concise but data-driven summary in bullet points, ensuring all key points are backed by financial figures.]\n\n"

    "## 💰 Financial Health\n"
    "[Provide a detailed breakdown of financial strength, profitability, risks, and trends, explaining every insight with extracted data.]\n\n"

    "## 📈 Investment Insights\n"
    "[Discuss potential opportunities & risks for investors with clear financial justifications.]\n\n"

    "## 📊 Key Financial Metrics\n"
    "| 📌 Metric | 📉 Value | 📋 Explanation |\n"
    "|----------|---------|---------------|\n"
    "[Provide a structured table with explanations for each metric.]\n\n"

    "## 📊 Comparative Analysis\n"
    "[Analyze financial trends over different time periods within the company's own financial data. Ensure comparisons are based only on available information without referencing industry standards.]\n\n"

    "## 🔮 Predictive Analysis\n"
    "| 🔍 Metric | 📈 Last Reported Value | 📊 Forecasted Next Value | 🔎 Prediction Rationale |\n"
    "|----------|----------------------|----------------------|----------------------|\n"
    "[For each available financial metric (e.g., revenue, net profit, EPS, debt levels, and all possible predictions), predict the next logical data point based on historical trends, growth patterns, and financial ratios. Provide a detailed explanation for each prediction.]\n\n"
    "add the following line at the end of each report 'This report is for informational purposes only and should not be considered as investment advice. Investors should conduct their own research and consult with a financial advisor before making investment decisions'"

    "**Additional Instructions:**\n"
    "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <font color='green'> Text </font>, and negative data should be highlighted in <font color='red'> Text </font>.\n"
    "- **Avoid Speculation:** Stick to the provided data; do not infer or speculate beyond the given information.\n"
    "- **Ensure Clarity:** Present insights in a structured and easy-to-read format.\n"
    "- **Use Strong Justifications:** Every claim or insight must be directly backed by numerical data from the report.\n"
    "- **All financial numbers representing money should be expressed only in the **₹ (Indian Rupee)** format. If any data is in a different currency or format, it must be converted to the **₹** format.**\n\n"
    "- **Future Prediction Accuracy:** Ensure forecasts are based on past trends, growth rates, and financial metrics, avoiding unjustified speculation.\n"
    "- **Hardcoded Formatting Rule:** When presenting financial results in a sentence format, do **not** use the backtick (`) symbol. Example:\n"
    
    "  - ✅ **Correct:** The company turned profitable, reporting a profit after tax of <font color='green'>1,455.36</font> lakhs for FY 2017-18 compared to a loss of <font color='red'>512.01</font> lakhs in FY 2016-17.\n"
    "  - ❌ **Incorrect:** The company turned profitable, reporting a profit after tax of ` <font color='green'>1,455.36</font> ` lakhs for FY 2017-18 compared to a loss of ` <font color='red'>512.01</font> ` lakhs in FY 2016-17.\n"
    "- Hard Rule: Do not add the ```html tag or any code block formatting such as triple backticks (```) before the output. The response must start directly with the header (e.g., # 📊 [Company Name] Overview) without any code block wrapping."
    "-**DO NOT** Add **```markdown** tag in the front of the response"
    )
    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- END ---

    model_name = "gemini-2.0-flash" # Check model name
    # Run synchronous Gemini call in a thread
    summary_text = await run_sync_in_thread(_sync_generate_content, model_name, prompt)
    return summary_text

# --- Checker Function (Similar to other files) --- 
async def checker(input_text):
    """Validates the generated summary using Gemini asynchronously."""
    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- START ---
    prompt3 = (
    "You are a Checker LLM. Your task is to evaluate the output from another LLM related to Finance or financial summaries. "
    "Respond strictly with one word: either 'RIGHT' or 'WRONG'. Do not include any additional words, explanations, or punctuation.\n\n"

    "Respond with 'WRONG' if any of the following are true:\n"
    "- The input contains error messages, apologies, or phrases like 'Unable to generate', 'I am unable to', '[ERROR]', or indicates missing data.\n"
    "- The input includes conversational or assistant-style language such as:\n"
    "  'Okay now I understand', 'Sure! Here's an improved version', 'Let me know if', 'Here is the generated summary', "
    "'Sure! Here's the grammatically correct version', or any similar interactive phrases.\n"
    "- The input contains gibberish like 'fmhgbdlmbhdf' or similar non-sensical strings.\n"
    "- The input includes the backtick character (`), such as in (`<font color='green'>1,455.36</font>`).\n\n"
    "Respond with 'RIGHT' only if the input is a complete, accurate, and valid financial summary with no conversational tone or formatting issues.\n"
    "For example, (<font color='green'>1,455.36</font>) is acceptable and should be marked as 'RIGHT'.\n\n"
    "If Input has too much of an empty space such as multiple blank lines, it should be marked as 'WRONG'.\n\n"
    "- **Avoid Multiple empty lines:** Do not print multiple empty lines and not also  ----------------------------------------- lines like this if it is in inpur return WRONG\n"

    "Try to generate whole as given below format and **if it is half generated or not in proper markdown response will be 'WRONG'** \n\n"
    "**Output Format:**\n"
    "# 📊 [Company Name] Overview\n"
    "## 💰 Summary\n"
   
    "## 💰 Financial Health\n"
    
    "## 📈 Investment Insights\n"
   
    "## 📊 Key Financial Metrics\n"
    "| 📌 Metric | 📉 Value | 📋 Explanation |\n"
    "|----------|---------|---------------|\n"
    
    "## 📊 Comparative Analysis\n"
    
    "## 🔮 Predictive Analysis\n"
    "| 🔍 Metric | 📈 Last Reported Value | 📊 Forecasted Next Value | 🔎 Prediction Rationale |\n"
    "|----------|----------------------|----------------------|----------------------|\n"
    "[For each available financial metric (e.g., revenue, net profit, EPS, debt levels, and all possible predictions), predict the next logical data point based on historical trends, growth patterns, and financial ratios. Provide a detailed explanation for each prediction.]\n\n"
    "add the following line at the end of each report 'This report is for informational purposes only and should not be considered as investment advice. Investors should conduct their own research and consult with a financial advisor before making investment decisions'"

    f"Here is the original report:\n{input_text}"
    )
    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- END ---

    model_name = "gemini-2.0-flash"
    # Run synchronous Gemini call in a thread
    check_result = await run_sync_in_thread(_sync_generate_content, model_name, prompt3)
    return check_result

# --- Main Orchestration Function --- 
async def generate_youtube_summary(url: str, user_id, background_tasks, retries=2): # Takes 'url' which contains transcript text
    attempt = 0
    result_list = []

    # The 'url' parameter now directly contains the transcript text
    transcript_text = url 

    if not transcript_text:
        # logging.error("No URL provided to generate_youtube_summary.") # Log message changed
        logging.error("No transcript text provided (via 'url' parameter) to generate_youtube_summary.")
        result_list.append({
            "sequence_number": "overall",
            "pages": "Overall Summary",
            # "detailed_analysis": "No YouTube URL was provided.", # Message changed
            "detailed_analysis": "No transcript text was provided.",
            "status": False
        })
        return result_list

    # --- Removed Video ID extraction and Transcript Fetching --- 
    # video_id = extract_video_id(url) 
    # if not video_id:
    #     # ... (error handling removed) ...
    #     return result_list
    # logging.info(f"Extracted video ID: {video_id}")
    # transcript_text = await get_transcript_from_youtube(video_id)
    # if transcript_text is None:
    #     # ... (error handling removed) ...
    #     return result_list
    # --- End of Removed Section ---
    
    # Optional background task (ensure it's async or wrapped properly)
    # Ensure background_pinecone_task can handle raw text if used
    # background_tasks.add_task(background_pinecone_task, transcript_text, user_id) 

    try:
        while attempt < retries:
            # logging.info(f"Attempt {attempt + 1}/{retries} to generate and check YouTube summary (from provided text)...") # Removed this log
            try:
                # Generate summary asynchronously using the provided text
                summary_content = await transcript_summary(transcript_text)

                # Check summary asynchronously
                checker_result = await checker(summary_content)

                # logging.info(f"YouTube Checker result (attempt {attempt + 1}): '{checker_result}'") # Removed this log

                is_wrong = isinstance(checker_result, str) and 'wrong' in checker_result.lower()
                is_error = isinstance(checker_result, str) and '[error' in summary_content.lower() # Check original summary for errors too

                if not is_wrong and not is_error and checker_result:
                    result_list.append({
                        "sequence_number": "overall",
                        "pages": "Overall Summary",
                        "detailed_analysis": summary_content,
                        "status": True
                    })
                    # logging.info("YouTube summary generation and validation successful.") # Removed this log
                    return result_list
                else:
                    logging.warning(f"Attempt {attempt + 1} failed YouTube validation. Checker: '{checker_result}'. Summary: '{summary_content[:100]}...'. Retrying...")
                    attempt += 1
                    await asyncio.sleep(random.uniform(0.5, 2.0))
                    continue

            except Exception as e:
                error_msg = str(e)
                logging.error(f"Exception during YouTube summary generation/checking (attempt {attempt + 1}): {error_msg}", exc_info=True)
                if ("429" in error_msg or
                    "quota" in error_msg.lower() or
                    "resource has been exhausted" in error_msg.lower() or
                    "rate limit" in error_msg.lower()):
                    logging.warning(f"Quota/Rate limit error detected (attempt {attempt + 1}). Retrying after delay...")
                    attempt += 1
                    await asyncio.sleep(random.uniform(3, 7))
                    continue
                else:
                    logging.critical(f"Non-retryable exception during YouTube summary generation loop: {e}", exc_info=True)
                    result_list.append({
                        "sequence_number": "overall",
                        "pages": "Overall Summary",
                        "detailed_analysis": f"An unexpected error occurred during YouTube summary generation: {e}",
                        "status": False
                    })
                    return result_list

    except Exception as e:
        logging.critical(f"Unhandled exception in generate_youtube_summary: {e}", exc_info=True)
        if not result_list:
             result_list.append({
                "sequence_number": "overall",
                "pages": "Overall Summary",
                "detailed_analysis": f"A critical error occurred in YouTube summary processing: {e}",
                "status": False
            })
        return result_list

    # If all retries failed
    logging.error(f"YouTube summary generation failed validation after {retries} attempts.")
    result_list.append({
        "sequence_number": "overall",
        "pages": "Overall Summary",
        "detailed_analysis": "YouTube summary generation failed after multiple validation attempts. Please try again later.",
        "status": False
    })
    return result_list

