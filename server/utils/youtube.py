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
from server.utils.improver import run_sync_in_thread,_sync_extract_text_content,_sync_generate_content,improver,checker,get_random_key_name
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
    "If the provided data does not contain an annual report or any relevant company financial information, respond only with: The provided document does not contain an transcript of concall or company-specific financial information. Do not include any additional text, formatting, or output."
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

    try:
        while attempt < retries:
            logging.info(f"Attempt {attempt + 1}/{retries} to generate and check financial summary...")
            try:
                # Generate report asynchronously
                report_content = await transcript_summary(transcript_text)
                improve_content = await improver(report_content)
                # Check report asynchronously
                checker_result = await checker(improve_content)

                logging.info(f"Checker result (attempt {attempt + 1}): '{checker_result}'")

                # More robust check for 'WRONG', handling potential None/errors from checker itself
                is_wrong = isinstance(checker_result, str) and 'wrong' in checker_result.lower()
                is_error = isinstance(checker_result, str) and '[error' in checker_result.lower()

                if not is_wrong and not is_error and checker_result: # Ensure it's not None/empty and not wrong/error
                    result_list.append({
                        "sequence_number": "overall",
                        "pages": "Overall Summary",
                        "detailed_analysis": improve_content,
                        "status": True
                    })
                    logging.info("Report generation and validation successful.")
                    return result_list
                else:
                    logging.warning(f"Attempt {attempt + 1} failed validation. Checker result: '{checker_result}'. Retrying...")
                    attempt += 1
                    await asyncio.sleep(random.uniform(0.5, 2.0)) # Delay before retry
                    continue # Move to next attempt

            except Exception as e:
                # Catch errors during the generation/checking process within the loop
                error_msg = str(e)
                logging.error(f"Exception during report generation/checking (attempt {attempt + 1}): {error_msg}", exc_info=True)
                # Check for specific rate limit errors (adjust based on actual Gemini error details)
                # Use lower() for case-insensitive matching
                if ("429" in error_msg or 
                    "quota" in error_msg.lower() or 
                    "resource has been exhausted" in error_msg.lower() or
                    "rate limit" in error_msg.lower()):
                    logging.warning(f"Quota/Rate limit error detected (attempt {attempt + 1}). Retrying after longer delay...")
                    attempt += 1
                    await asyncio.sleep(random.uniform(3, 7)) # Longer delay for rate limits
                    continue
                else:
                    # For other unexpected errors within the loop, stop retrying for this request
                    logging.critical(f"Non-retryable exception during report generation loop: {e}", exc_info=True)
                    result_list.append({
                        "sequence_number": "overall",
                        "pages": "Overall Summary",
                        "detailed_analysis": f"An unexpected error occurred during report generation: {e}",
                        "status": False
                    })
                    return result_list

    except Exception as e:
        # This catches errors outside the while loop (e.g., initial setup before retries)
        logging.critical(f"Unhandled exception in generate_financial_summary: {e}", exc_info=True)
        # Ensure a failure response is sent back
        if not result_list: # Avoid adding duplicate failure messages
             result_list.append({
                "sequence_number": "overall",
                "pages": "Overall Summary",
                "detailed_analysis": f"A critical error occurred: {e}",
                "status": False
            })
        return result_list

    logging.error(f"Report generation failed validation after {retries} attempts.")
    result_list.append({
        "sequence_number": "overall",
        "pages": "Overall Summary",
        "detailed_analysis": "this document doesn't contain required financial information",
        "status": False
    })
    return result_list