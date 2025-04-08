from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from dotenv import load_dotenv
import os
import time
import asyncio
import google.generativeai as genai
load_dotenv()
import logging

genai.configure(api_key=os.getenv("GEMINI_API_KEY_TEN"))


async def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path.lstrip('/')
    return None

async def get_available_languages(youtube_url):
    video_id = await get_video_id(youtube_url)
    if not video_id:
        return "Invalid YouTube URL."

    try:
        # Run the API call in a separate thread since it's blocking
        transcript_list = await asyncio.to_thread(YouTubeTranscriptApi.list_transcripts, video_id)
        
        languages = [transcript.language_code for transcript in transcript_list]  # Use `.language_code`
        return languages  # Return the full list of available languages
    except Exception as e:
        return f"Error fetching available languages: {e}"

async def get_transcript(video_url):
    video_id = await get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."

    try:
        available_languages = await get_available_languages(video_url)

        if isinstance(available_languages, str):  # If an error string is returned
            return available_languages

        if "en" in available_languages:  # Correctly check if English is available
            transcript = await asyncio.to_thread(YouTubeTranscriptApi.get_transcript, video_id, languages=["en"])
            text = "\n".join([entry['text'] for entry in transcript])
            return text
        else:
            return "Transcript not available in English."
    except Exception as e:
        return f"Error: {e}"


async def report_gen(text,retries=2):
    if not text:
        text.error("No text provided for summarization.")
        return "[ERROR: No text to summarize]"
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
    "- **Investment-Focused:** Provide key insights relevant for evaluating the company’s financial health, investment potential, and future growth outlook.\n"
    "- **Comprehensive Analysis:** Generate an in-depth company summary, explaining strengths, risks, trends, key financial metrics, and future projections with supporting data points.\n"
    "- **Comparative Evaluation:** Compare financial ratios, growth trends, and industry benchmarks where applicable, ensuring all comparisons are backed by figures.\n"
    "- **Structured & Visual:** Use tables, bullet points, and structured formatting to enhance clarity and comprehension.\n"
    "- **Predictive Insights:** Where possible, forecast future performance based on historical trends, numerical metrics, and financial patterns. Ensure every prediction is justified with solid reasoning and past data trends.\n"
   "- **Coloring Scheme:** Positive numerical data should be highlighted in green as <span style='color:green;'>red text</span>, and negative data should be highlighted in red <span style='color:red;'>red text</span>. Ensure that the output does not use Markdown for color formatting.\n\n"
    "-**Do Not** add any data that is not available such as **DO NOT ADD LINES LIKE *The retrieved data does not lend itself to complex visual representations beyond tables and structured lists. The table above summarizes key financial metrics."
    "-**Do Not** add a TABLE IF THE DATA INSIDE IT IS UNAVAILABLE AND EMPTY TABLE MUST NOT BE IN THE FINAL OUTPUT"
    "## Extracted Segment from the Video:\n"
    "```\n"
    f"{text}\n"
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


    "**Task:**\n"
    "Based solely on the provided data, generate a detailed company insight report including:\n"
    "1. **Company Overview** – Key highlights from the report, explained with numerical data.\n"
    "2. **Financial Health Evaluation** – Revenue trends, profitability, debt levels, and other critical metrics with clear breakdowns and justifications.\n"
    "3. **Investment Viability** – Strengths, weaknesses, risks, and potential opportunities, all elaborated with evidence from financial statements.\n"
    "4. **Comparative Analysis** – Compare financial performance across different time periods within the company’s own data set, ensuring all comparisons are backed by figures.\n"
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
    model = "gemini-2.0-flash-thinking-exp-01-21"
    model_instance = genai.GenerativeModel(model)
    response1 = model_instance.generate_content(prompt)
    return response1.text

def checker(input):
    prompt3 = (
        "You are a Checker LLM. You will receive an output from another LLM which will be related to Finance or financial summary and you must respond with only one word: either 'RIGHT' or 'WRONG'. "
        "Do not include any additional words, explanations, or punctuation. "
        "If the input contains error messages, apologies, or phrases like 'Unable to generate', 'I am unable to', '[ERROR]', or indicates missing data, respond with 'WRONG'. "
        "If the input contains conversational language such as 'Okay now I understand', 'Sure! Here’s an improved version', 'Let me know if', 'Sure! Here’s the grammatically correct version','here is the generated summary','gibberish such as fmhgbdlmbhdf' or similar assistant-style or interactive phrases, respond with 'WRONG'. "
        "If the input is complete, accurate, and valid financial content, respond with 'RIGHT'.\n\n"
        f"Here is the original report:\n{input}"
    )
    model = "gemini-2.0-flash"
    model_instance = genai.GenerativeModel(model)
    response = model_instance.generate_content(prompt3)
    return response.text           

async def generate_youtube_summary(url,user_id, background_tasks):
    attempt = 0
    response3 = []
    while attempt < 2:
        response2 = await report_gen(url)
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

