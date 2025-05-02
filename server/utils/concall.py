import asyncio
import io
import os
import tiktoken
import httpx
# import pymupdf
import logging
# import openai # Seems unused
import time
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from server.utils.improver import run_sync_in_thread,_sync_extract_text_content,_sync_generate_content,improver,checker
# from concurrent.futures import ThreadPoolExecutor # Not needed with asyncio.to_thread
from server.config import settings
from server.utils.backgound_task import background_pinecone_task

load_dotenv()

import random
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

async def questionans(chunks, retries=2): # Takes list of text chunks
    # Join chunks for the prompt, adjust if needed
    full_text_content = "\n---\n".join(chunks)

    if not full_text_content:
        logging.error("No text provided for question answering (questionans)." )
        return "[ERROR: No text to summarize]"

    # --- PROMPT DEFINITION (UNCHANGED FROM ORIGINAL) --- START --- 
    prompt = (
    "### Instruction:\n"
    "You are a highly advanced financial AI assistant specializing in analyzing company conference calls. "
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
    "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <span style='color:green;'>red text</span>, and negative data should be highlighted in red <span style='color:red;'>red text</span>. Ensure that the output does not use Markdown for color formatting.\n\n"
    "-**Do Not** add any data that is not available such as **DO NOT ADD LINES LIKE *The retrieved data does not lend itself to complex visual representations beyond tables and structured lists. The table above summarizes key financial metrics."
    "## Extracted Segment from the Video:\n"
    "All financial numbers representing money should be expressed only in the **₹ (Indian Rupee)** format. If any data is in a different currency or format, it must be converted to the **₹** format.\n\n"
    "```\n"
    f"{full_text_content}\n"
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
    model_name = "gemini-1.5-flash" # Check model name validity
    response_text = await run_sync_in_thread(_sync_generate_content, model_name, prompt)
    return response_text
            



async def generate_concall_summary(file, url, user_id, background_tasks, retries=2):
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
                report_content = await questionans(chunks)
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