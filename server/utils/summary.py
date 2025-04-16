import asyncio
import io
import os
import tiktoken
import httpx
# import pymupdf
import logging
# import openai
import time
import fitz
import google.generativeai as genai
from server.utils.improver import run_sync_in_thread,_sync_extract_text_content,_sync_generate_content,improver,checker,get_random_key_name
from dotenv import load_dotenv
# from concurrent.futures import ThreadPoolExecutor
import random

load_dotenv()








async def extract_text(file, url):
    input_binary = None
    try:
        if file:
            input_binary = await file.read()
        elif url:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, follow_redirects=True, timeout=30.0)
                response.raise_for_status()
                input_binary = response.content
        else:
             logging.warning("extract_text called with no file or URL.")
             return None

        if input_binary:
            # Run synchronous fitz text extraction in a thread
            extracted_text = await run_sync_in_thread(_sync_extract_text_content, input_binary)
            return extracted_text
        else:
            return None

    except httpx.RequestError as e:
        logging.critical(f"HTTP request failed for URL {url}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logging.critical(f"Failed to retrieve PDF from {url}. Status code: {e.response.status_code}")
        return None
    except Exception as e:
        # Catching generic Exception after specific ones
        logging.critical(f"Error during text extraction processing: {e}", exc_info=True)
        return None


async def chunk_text_by_tokens(text, chunk_size=950000):
    # This is CPU-bound but usually fast enough. If it becomes a bottleneck for huge texts,
    # could be wrapped in run_sync_in_thread.
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    total_tokens = len(tokens)
    chunks = []
    for i in range(0, total_tokens, chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks



async def report_gen(chunks, retries=2): # Now takes chunks (list of text) directly
    # Process chunks - joining them here for a single prompt
    full_text_content = "\n---\n".join(chunks)

    if not full_text_content:
        logging.error("No text content provided to report_gen.")
        return "[ERROR: No text to generate report from]"

    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- START --- 
    prompt2 = (
    "### 🏦 Financial Advisor AI: Company Investment Evaluation\n"
    "**Instruction:**\n"
    "You are a highly skilled financial advisor AI specializing in evaluating companies strictly based on Annual Reports and official financial documents. "
    "Your goal is to provide investors with accurate insights, summaries, financial health evaluations, and predictive insights derived directly from the given data.\n\n"

    "**Guidelines:**\n"
    "Strictly No HTML or markdown Code Blocks: Under no circumstances should the output include ```html or any kind of code block formatting. This is strictly prohibited and must be avoided at all costs."
    "- **Objective & Data-Driven:** Use only the retrieved data—no assumptions or guesses. Every insight must be justified with extracted figures.\n"
    "- **Investment-Focused:** Provide key insights relevant for evaluating the company's financial health, investment potential, and future growth outlook.\n"
    "- **Comprehensive Analysis:** Generate an in-depth company summary, explaining strengths, risks, trends, key financial metrics, and future projections with supporting data points.\n"
    "- **Structured & Visual:** Use tables, bullet points, and structured formatting to enhance clarity and comprehension.\n"
    "- **Predictive Insights:** Where possible, forecast future performance based on historical trends, numerical metrics, and financial patterns. Ensure every prediction is justified with solid reasoning and past data trends.\n"
    "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <span style='color:green;'>green text</span>, and negative data should be highlighted in red <span style='color:red;'>red text</span>. Ensure that the output does not use Markdown for color formatting.\n\n"
    "-**Do Not** add a TABLE IF THE DATA INSIDE IT IS UNAVAILABLE AND EMPTY TABLE MUST NOT BE IN THE FINAL OUTPUT"
    "-**DO not Add **```html** tag in the front of the response"
    "should not inclue conversational text such as 'Here's a structured company insight report based on the provided financial data'"
    "## Extracted Segment from the Video:\n"
    "**Extracted Financial Data:**\n"
    "Try to fetch as much as required data possible"
    "All financial numbers representing money should be expressed only in the **₹ (Indian Rupee)** format. If any data is in a different currency or format, it must be converted to the **₹** format.\n\n"
    f"{full_text_content}\n\n"

    "**Task:**\n"
    "Based solely on the provided data, generate a detailed company insight report including:\n"
    "1. **Company Overview** – Key highlights from the report, explained with numerical data.\n"
    "2. **Financial Health Evaluation** – Revenue trends, profitability, debt levels, and other critical metrics with clear breakdowns and justifications.\n"
    "3. **Investment Viability** – Strengths, weaknesses, risks, and potential opportunities, all elaborated with evidence from financial statements.\n"
    "4. **Comparative Analysis** – Compare financial performance across different time periods within the company's own data set, ensuring all comparisons are backed by figures.\n"
    "5. **Key Financial Metrics Table** – Present structured financial data where applicable with detailed explanations.\n"
    "6. **Predictive Analysis** – Forecast future financial performance based on historical data trends, numerical progression, and reasonable assumptions, ensuring every prediction has strong supporting evidence.\n"
    "7. **Visual Financial Representation** – If applicable, structure key financial data in a visually intuitive format.\n\n"

    "Strickly follow this output format if you have all the data required to generate the report\n"
    "If you do not have sufficent data, follow this format\n"
    
    
    "**Output Format:**\n"
    "# 📊 [Company Name]\n Try to fetch name from the document and if name is not available, then leave it as Company information\n"
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
    "- **All financial numbers representing money should be expressed only in the **₹ (Indian Rupee)** format. If any data is in a different currency or format, it must be converted to the **₹** format.**\n\n"
    "- **Future Prediction Accuracy:** Ensure forecasts are based on past trends, growth rates, and financial metrics, avoiding unjustified speculation.\n"
    "- **Hardcoded Formatting Rule:** When presenting financial results in a sentence format, do **not** use the backtick (`) symbol. Example:\n"
    "  - ✅ **Correct:** The company turned profitable, reporting a profit after tax of <font color='green'>1,455.36</font> lakhs for FY 2017-18 compared to a loss of <font color='red'>512.01</font> lakhs in FY 2016-17.\n"
    "  - ❌ **Incorrect:** The company turned profitable, reporting a profit after tax of ` <font color='green'>1,455.36</font> ` lakhs for FY 2017-18 compared to a loss of ` <font color='red'>512.01</font> ` lakhs in FY 2016-17.\n"
    "Strictly No HTML or markdown Code Blocks: Under no circumstances should the output include ```html or any kind of code block formatting. This is strictly prohibited and must be avoided at all costs."
    )

    # Run synchronous Gemini call in a thread
    model_name = "gemini-2.0-flash" # Consider making model name configurable
    response_text = await run_sync_in_thread(_sync_generate_content, model_name, prompt2)
    return response_text


async def generate_financial_summary(file, url, user_id, background_tasks, retries=2):
    attempt = 0
    result_list = [] # Renamed response3 for clarity

    extracted_text = await extract_text(file, url)

    if extracted_text is None:
        # Error is logged within extract_text
        result_list.append({
            "sequence_number": "overall",
            "pages": "Overall Summary",
            "detailed_analysis": "Failed to extract text from the provided source. Please check the file/URL",
            "status": False
        })
        return result_list

    # Optional background task - ensure it's async or wrapped if needed
    # background_tasks.add_task(background_pinecone_task, extracted_text, user_id)

    chunks = await chunk_text_by_tokens(extracted_text, chunk_size=950000)
    if not chunks:
         logging.error("Text extracted but resulted in zero chunks.")
         result_list.append({
             "sequence_number": "overall",
             "pages": "Overall Summary",
             "detailed_analysis": "Failed to process extracted text into meaningful chunks.",
             "status": False
         })
         return result_list

    # The 'questionans' part seems unused/commented out

    try:
        while attempt < retries:
            logging.info(f"Attempt {attempt + 1}/{retries} to generate and check financial summary...")
            try:
                # Generate report asynchronously
                report_content = await report_gen(chunks)
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