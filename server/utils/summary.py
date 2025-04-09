import asyncio
import io
import os
import tiktoken
import requests
# import pymupdf
import logging
import openai
import time
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from server.config import settings
from server.utils.backgound_task import background_pinecone_task

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

async def extract_text(file, url):
    try:
        if file:
            input_binary = await file.read()
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logging.critical(f"Failed to retrieve PDF. Status code: {response.status_code}")
                return []
            input_binary = response.content

        with io.BytesIO(input_binary) as pdf_file:
            doc = fitz.open(stream=pdf_file, filetype="pdf")                 
        return doc
        

    except Exception as e:
        logging.critical(f"Unable to open the PDF file: {e}")
        return []
    
async def chunk_text_by_tokens(text, chunk_size=950000):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    total_tokens = len(tokens)
    chunks = []
    for i in range(0, total_tokens, chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    return chunks

async def questionans(chunks,question,retries=2):
    if not chunks:
        logging.error("No text provided for summarization.")
        return "[ERROR: No text to summarize]"

    prompt = (
    "Instruction:\n"
    "You are a highly advanced financial AI assistant specializing in analyzing company performance based on Annual Reports and other financial documents. "
    "Your role is to assist investors, traders, and financial professionals by extracting key insights, trends, and financial metrics. "
    "Your responses must be strictly based on the retrieved document segments provided. "
    "Do not generate information beyond what is given, assume missing data, or provide opinions. "
    "If the retrieved data does not contain sufficient information to answer a question, state: "
    "'The retrieved data does not provide enough information to answer this question.'\n\n"

    "Response Guidelines:\n"
    "- **Detailed and Data-Driven**: Provide numerical insights where applicable.\n"
    "- **Accurate and Fact-Based**: Use only the provided financial data.\n"
    "- **Comparative Analysis**: Compare financial trends, KPIs, and industry benchmarks when relevant.\n"
    "- **Concise and Direct**: Avoid unnecessary wording or small talk.\n\n"
    "- **Can also provide Table formated data if needed for better observations"

    "Extracted segment from the company’s financial report:\n\n"
    f"{chunks}\n\n"

    "Based solely on this segment, analyze and answer the following questions. "
    "If additional financial data is required, specify what is needed.\n\n"

    "**Output Format:**\n"
    "Question1: [Your first question]\n"
    "Answer1: [Your precise, data-backed financial analysis]\n\n"

    f"{question}"
    )

    model = "gemini-2.0-flash-thinking-exp-01-21"
    model_instance = genai.GenerativeModel(model)
    response1 = model_instance.generate_content(prompt)
    return response1.text


async def report_gen(response,retries=2):
    if not response:
        logging.error("No text provided for summarization.")
        return "[ERROR: No text to summarize]"
    prompt2 = (
    "### 🏦 Financial Advisor AI: Company Investment Evaluation\n"
    "**Instruction:**\n"
    "You are a highly skilled financial advisor AI specializing in evaluating companies strictly based on Annual Reports and official financial documents. "
    "Your goal is to provide investors with accurate insights, summaries, financial health evaluations, and predictive insights derived directly from the given data.\n\n"

    "**Guidelines:**\n"
    "- **Objective & Data-Driven:** Use only the retrieved data—no assumptions or guesses. Every insight must be justified with extracted figures.\n"
    "- **Investment-Focused:** Provide key insights relevant for evaluating the company’s financial health, investment potential, and future growth outlook.\n"
    "- **Comprehensive Analysis:** Generate an in-depth company summary, explaining strengths, risks, trends, key financial metrics, and future projections with supporting data points.\n"
    "- **Structured & Visual:** Use tables, bullet points, and structured formatting to enhance clarity and comprehension.\n"
    "- **Predictive Insights:** Where possible, forecast future performance based on historical trends, numerical metrics, and financial patterns. Ensure every prediction is justified with solid reasoning and past data trends.\n"
    "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <span style='color:green;'>green text</span>, and negative data should be highlighted in red <span style='color:red;'>red text</span>. Ensure that the output does not use Markdown for color formatting.\n\n"
    "-**Do Not** add a TABLE IF THE DATA INSIDE IT IS UNAVAILABLE AND EMPTY TABLE MUST NOT BE IN THE FINAL OUTPUT"
    "should not inclue conversational text such as 'Here's a structured company insight report based on the provided financial data'"
    "## Extracted Segment from the Video:\n"
    "**Extracted Financial Data:**\n"
    f"{response}\n\n"

    "**Task:**\n"
    "Based solely on the provided data, generate a detailed company insight report including:\n"
    "1. **Company Overview** – Key highlights from the report, explained with numerical data.\n"
    "2. **Financial Health Evaluation** – Revenue trends, profitability, debt levels, and other critical metrics with clear breakdowns and justifications.\n"
    "3. **Investment Viability** – Strengths, weaknesses, risks, and potential opportunities, all elaborated with evidence from financial statements.\n"
    "4. **Comparative Analysis** – Compare financial performance across different time periods within the company’s own data set, ensuring all comparisons are backed by figures.\n"
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
    "[Analyze financial trends over different time periods within the company’s own financial data. Ensure comparisons are based only on available information without referencing industry standards.]\n\n"

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
    "- **Future Prediction Accuracy:** Ensure forecasts are based on past trends, growth rates, and financial metrics, avoiding unjustified speculation.\n"
    "- **Hardcoded Formatting Rule:** When presenting financial results in a sentence format, do **not** use the backtick (`) symbol. Example:\n"
    "  - ✅ **Correct:** The company turned profitable, reporting a profit after tax of <font color='green'>1,455.36</font> lakhs for FY 2017-18 compared to a loss of <font color='red'>512.01</font> lakhs in FY 2016-17.\n"
    "  - ❌ **Incorrect:** The company turned profitable, reporting a profit after tax of ` <font color='green'>1,455.36</font> ` lakhs for FY 2017-18 compared to a loss of ` <font color='red'>512.01</font> ` lakhs in FY 2016-17.\n"
    )


    model = "gemini-2.0-flash"
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt2)
    return response.text

def checker(input):
    prompt3 = (
    "You are a Checker LLM. Your task is to evaluate the output from another LLM related to Finance or financial summaries. "
    "Respond strictly with one word: either 'RIGHT' or 'WRONG'. Do not include any additional words, explanations, or punctuation.\n\n"

    "Respond with 'WRONG' if any of the following are true:\n"
    "- The input contains error messages, apologies, or phrases like 'Unable to generate', 'I am unable to', '[ERROR]', or indicates missing data.\n"
    "- The input includes conversational or assistant-style language such as:\n"
    "  'Okay now I understand', 'Sure! Here’s an improved version', 'Let me know if', 'Here is the generated summary', "
    "'Sure! Here’s the grammatically correct version', or any similar interactive phrases.\n"
    "- The input contains gibberish like 'fmhgbdlmbhdf' or similar non-sensical strings.\n"
    "- The input includes the backtick character (`), such as in (`<font color='green'>1,455.36</font>`).\n\n"

    "Respond with 'RIGHT' only if the input is a complete, accurate, and valid financial summary with no conversational tone or formatting issues.\n"
    "For example, (<font color='green'>1,455.36</font>) is acceptable and should be marked as 'RIGHT'.\n\n"

    f"Here is the original report:\n{input}"
    )
    model = "gemini-2.0-flash"
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt3)
    return response.text


async def generate_financial_summary(file, url, user_id, background_tasks):
    attempt = 0
    response3 = []

    doc = await extract_text(file, url)

    if not doc:
        response3.append(
            {
                "sequence_number": "overall",
                "pages": "Overall Summary",
                "detailed_analysis": "PDF parsing failed. Please try again."
            }
        )
        return response3  

    text = "\n".join([page.get_text("text") for page in doc])

    # Optional background task, uncomment if needed
    # background_tasks.add_task(background_pinecone_task, doc, user_id)

    chunks = await chunk_text_by_tokens(text, chunk_size=950000)

    with open("server/utils/final_questions.txt", "r", encoding="utf-8") as file:
        question = file.read()

    response = await questionans(chunks, question)

    while attempt < 2:
        response2 = await report_gen(response)
        res = checker(response2)

        if "wrong" not in res.lower():
            response3.append(
                {
                    "sequence_number": "overall",
                    "pages": "Overall Summary",
                    "detailed_analysis": response2
                }
            )
            return response3

        attempt += 1

    response3.append(
        {
            "sequence_number": "overall",
            "pages": "Overall Summary",
            "detailed_analysis": "Response generation failed. Please try again."
        }
    )
    return response3



