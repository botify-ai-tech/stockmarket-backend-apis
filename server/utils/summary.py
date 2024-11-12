import asyncio
import io
import os
import requests
import pymupdf
import logging
import openai
import time
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from server.utils.backgound_task import background_pinecone_task

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)


async def split_text_into_chunks(text, max_tokens_per_chunk=2000):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens_per_chunk):
        chunks.append(" ".join(words[i : i + max_tokens_per_chunk]))
    return chunks


async def gpt_summarize(text, retries=2):
    if not text:
        logging.error("No text provided for summarization.")
        return "[ERROR: No text to summarize]"

    # data = {
    #     "model": "gpt-4o-mini",
    #     "messages": [
    #         {
    #             "role": "system",
    #             "content": "Act as an expert in extracting important information in detail for finanacial summary. For that you will be provided will a chunk of financial data, including text, tables, graphs, and images, and have to generate finanacial summary without loosing any piece of important information. The key areas of focus include Financial Performance, covering total revenues, EBITDA, EBIT margins, PAT (Net Profit After Tax), free cash flow, ROCE (Return on Capital Employed), ROE (Return on Equity), future, and changes in net debt. For Segmental Performance, examine revenue breakdown, sales trends, and product launches, etc, informations which are available in chunk of financial data and important for generating financial summaries. Among these mentioned key areas extract thoes information which are available rest avoid.",
    #         },
    #         {"role": "user", "content": f"Financial Data:\n{text}"},
    #     ],
    # }

    for attempt in range(retries):
        try:
            # OPENAI
            # response = openai.chat.completions.create(
            #     model=data["model"],
            #     messages=data["messages"],
            #     temperature=data.get("temperature", 0),
            #     max_tokens=data.get("max_tokens", 500),
            #     frequency_penalty=data.get("frequency_penalty", 0),
            #     presence_penalty=data.get("presence_penalty", 0),
            # )
            # analysis = response.choices[0].message.content

            # GEMINI
            model = genai.GenerativeModel("gemini-1.5-flash")
            analysis = model.generate_content(
                f"""As a seasoned financial analyst with expertise in dissecting financial documents, your assignment is to produce a comprehensive financial summary of the provided document. This document contains a variety of financial information about a specific company. Your challenge lies not only in summarizing but in extracting the most pertinent details in a manner that aids an investor in making well-informed decisions about the company's financial and fundamental standing.\nAssume that the investor has extensive knowledge in financial matters, but has limited time to go through the entire document. Your summary should therefore be clear, concise yet inclusive of all crucial points. Extract key elements such as the company's financial performance over the past few years, its income, expenditures, and debt levels, its assets, liabilities, and equity status, and any significant financial risks or opportunities that are evident. \nFurthermore, delve into the company's fundamental health by examining its market position, competitive advantages, leadership, and strategic direction. Be aware of any contextual or industry-specific factors that may influence the company's financial health. \nThe summary should be balanced, providing both positive and negative aspects, yet maintaining an objective tone. Be sure to cite specific figures, percentages, or trends from the document where necessary for precision and credibility. \nYour task is not just to provide a summary, but also a nuanced interpretation that provides a comprehensive snapshot of the company's overall financial and fundamental health. Remember, the ultimate aim is to facilitate the investor in making an informed decision. \nThe complexity of this task lies in ensuring that the summary is both profound enough to cover all essential aspects, yet concise enough to be easily digestible for the investor. The structure of your summary should be logical and coherent, allowing the reader to quickly grasp the company's financial situation and fundamental health. This task requires a sophisticated understanding of financial analysis, excellent summarizing skills, and the ability to communicate complex information in a clear and accessible manner.\n\nYou have to also extract the following details from the document text without hallucination. I repeat "DO NOT HALLUCINATE". If you don't find following information in the document text then mention "N/A" But, Do not hallucination. \n<<Output>>:\n{{\n "financial_analysis": {{\n "overall_summary": {{\n "summary": "Write a high-level summary of the financial report here in markdown.",\n "key_takeaways": [\n "List key takeaways of the financial report here.",\n "Each takeaway should highlight important findings or trends.",\n "Focus on areas like revenue growth, profitability, cash flow, and market position."\n ]\n }},\n "revenue_and_sales_trends": {{\n "key_observations": "Summarize revenue and sales trends here, including any significant changes or seasonality.",\n "insights": "Describe insights on sales trends, such as growth drivers or demand patterns."\n }},\n "profit_margins": {{\n "gross_margin": {{\n "key_observations": "Detail observations on gross margin, including any increase or decrease.",\n "insights": "Provide insights on what influences gross margin changes, like cost efficiency."\n }},\n "operating_margin": {{\n "key_observations": "Explain key observations on operating margin, particularly changes in operating expenses.",\n "insights": "Provide context for operating margin trends, such as investment in R&D or cost control."\n }},\n "net_margin": {{\n "key_observations": "Write key observations on net margin stability or variability.",\n "insights": "Describe factors impacting net margin, like tax, interest expenses, or cost management."\n }}\n }},\n "expenses_analysis": {{\n "key_observations": "Summarize significant expense trends, focusing on key categories like SG&A, R&D, and COGS.",\n "insights": "Discuss insights into expense management and strategic spending areas."\n }},\n "liquidity_and_cash_flow": {{\n "operating_cash_flow": {{\n "key_observations": "Highlight key observations on cash flow from operations, such as cash generation trends.",\n "insights": "Explain the implications of operational cash flow on liquidity and stability."\n }},\n "investing_cash_flow": {{\n "key_observations": "Summarize key observations on cash flows from investing activities, including capital expenditures.",\n "insights": "Provide insights into how investing activities reflect long-term growth strategies."\n }},\n "financing_cash_flow": {{\n "key_observations": "Describe key observations on financing cash flows, including debt or dividend payments.",\n "insights": "Discuss the impact of financing decisions on financial stability and shareholder returns."\n }}\n }},\n "debt_levels_and_solvency": {{\n "debt_to_equity_ratio": {{\n "key_observations": "Write key observations on debt-to-equity ratio trends and their implications.",\n "insights": "Discuss the company's debt management strategy and financial stability."\n }},\n "interest_coverage_ratio": {{\n "key_observations": "Summarize observations on interest coverage ratio, focusing on the company's ability to cover interest expenses.",\n "insights": "Provide insights into the company's buffer for managing interest obligations."\n }}\n }},\n "assets_and_inventory_management": {{\n "inventory_turnover": {{\n "key_observations": "Detail key observations on inventory turnover rates and potential issues like overstocking.",\n "insights": "Discuss how inventory turnover reflects demand and inventory efficiency."\n }},\n "asset_utilization": {{\n "key_observations": "Summarize asset utilization trends and their implications on operational efficiency.",\n "insights": "Provide insights into asset management and the impact on production capacity."\n }}\n }},\n "eps_and_shareholder_returns": {{\n "eps": {{\n "key_observations": "Summarize EPS trends, noting year-over-year or quarter-over-quarter changes.",\n "insights": "Explain how EPS growth aligns with profitability and benefits shareholders."\n }},\n "shareholder_returns": {{\n "dividends": {{\n "key_observations": "Describe key observations on dividend payouts and changes over time.",\n "insights": "Discuss the impact of dividends on shareholder value and company cash reserves."\n }}\n }}\n }},\n "industry_performance_comparison": {{\n "key_observations": "Summarize how the company's performance compares to industry averages.",\n "insights": "Provide insights on competitive positioning and industry strengths or weaknesses."\n }},\n "future_projections": {{\n "future_goal": {{\n "key_observations": "Write the company's strategic goals, such as expanding market share or launching new products.",\n "insights": "Explain the broader impact of these goals on growth and positioning."\n }},\n "forward_growth": {{\n "key_observations": "Describe the projected growth rate, based on strategic initiatives and market trends.",\n "insights": "Discuss factors driving forward growth, including innovation and market expansion."\n }},\n "forward_eps": {{\n "key_observations": "Write forward EPS projections and the expected impact on shareholder value.",\n "insights": "Provide context for forward EPS, such as profitability trends and cost efficiency."\n }}\n }}\n }}\n}}\n<<input>>:{text}"""
            )
            return analysis
        except Exception as e:
            logging.error(
                f"Gemini AI API error on attempt {attempt + 1}/{retries}: {e}"
            )
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                logging.error("Max retries reached. Returning empty analysis.")
                return "[ERROR: Unable to generate summary]"


async def extract_text_tables_images_from_pdf(doc, pdf_path, start_page, end_page):
    extracted_data = ""

    for page_num in range(start_page, end_page):
        try:
            if page_num < doc.page_count:
                page = doc.load_page(page_num)

                text = page.get_text("text")
                extracted_data += text + "\n"

                tables = page.get_text("blocks")
                for table in tables:
                    if len(table[4]) > 0 and any(char.isdigit() for char in table[4]):
                        extracted_data += "[TABLE DATA]\n" + table[4] + "\n"

                images = page.get_images(full=True)
                if images:
                    extracted_data += "[IMAGE/GRAPH DETECTED]\n"
                    for img in images:
                        extracted_data += f"[IMAGE: {img[7]}]\n"
        except Exception as e:
            logging.error(f"Error processing page {page_num} of {pdf_path}: {e}")

    return extracted_data if extracted_data.strip() else None


async def process_page_groups(file, pdf_path, page_group, sequence_number):

    start_page, end_page = page_group
    extracted_data = await extract_text_tables_images_from_pdf(
        file, pdf_path, start_page, end_page
    )

    if extracted_data:
        analysis = await gpt_summarize(extracted_data)
    else:
        logging.warning(
            f"No data extracted from pages {page_group[0]}-{page_group[1]} in {pdf_path}"
        )
        analysis = "[NO DATA AVAILABLE]"

    return {
        "sequence_number": sequence_number,
        "pages": f"{page_group[0]} - {page_group[1]-1}",
        "analysis": analysis,
    }


async def gpt_overall_summarize(text, detailed=False, retries=2):
    if not text:
        logging.error("No text provided for overall summarization.")
        return "[ERROR: No text to summarize]"

    if detailed:
        prompt = f"You are an expert financial analyst tasked with generating a financial summary for a company for a specific financial year. Your task is to generate detailed financial summary. Below are the key questions and areas of focus that you need to cover in your summary. Ensure that the summary is comprehensive, accurate, and provides insights into the company’s financial health, segmental performance, sustainability efforts, risk management, and future outlook.\n\nAreas of Focus:\n\n\n1. Financial Performance:\n- What were the total revenues for the year compared to previous years?\n- Discuss EBITDA, EBIT margins, net profit (PAT), free cash flow, and key financial ratios (ROCE, ROE).\n- How did the company’s net debt change during the year?\n\n2. Segmental Performance:\n- Break down revenue contributions from key business segments.\n- Analyze sales volume trends, key product launches, and market share in relevant markets.\n\n3. Cost and Investment Analysis:\n- How was the cost structure managed in response to market conditions?\n- Detail total investment spending, particularly in R&D and other significant areas.\n\n4.Sustainability and ESG Performance:\n- What were the key sustainability initiatives and progress toward achieving environmental goals?\n- Provide an overview of the company’s ESG ratings and achievements in renewable energy and resource conservation.\n\n5. Risk Management and Future Outlook:\n- Identify key risks and the strategies for mitigating them.\n- Discuss the company’s outlook for the upcoming year, including growth opportunities, challenges, regulatory navigation, and strategic initiatives.\n\n6. Corporate Governance:\n- Introduce key Board members and any changes during the year.\n- What is the dividend policy, and what dividends were declared for the year?\n- The summary should be clear, concise, and provide an integrated analysis of the company’s financial health, operational efficiency, strategic initiatives, and future prospects. Also give Advantages, disadvantages and neutrals in term of impactness. \nNote: Do not add extra infromation from your side, use only those information which are available.\nFinancial Data:\n{text}"
    else:
        prompt = f"You are an expert financial analyst tasked with generating a concise financial summary for a company for a specific financial year. Your task is to generate point wise summary. Below are the key questions and areas of focus that you need to cover in your summary. Ensure that the summary is comprehensive, accurate, and provides insights into the company’s financial health, segmental performance, sustainability efforts, risk management, and future outlook.\n\nAreas of Focus:\n\n\n1. Financial Performance:\n- What were the total revenues for the year compared to previous years?\n- Discuss EBITDA, EBIT margins, net profit (PAT), free cash flow, and key financial ratios (ROCE, ROE).\n- How did the company’s net debt change during the year?\n\n2. Segmental Performance:\n- Break down revenue contributions from key business segments.\n- Analyze sales volume trends, key product launches, and market share in relevant markets.\n\n3. Cost and Investment Analysis:\n- How was the cost structure managed in response to market conditions?\n- Detail total investment spending, particularly in R&D and other significant areas.\n\n4.Sustainability and ESG Performance:\n- What were the key sustainability initiatives and progress toward achieving environmental goals?\n- Provide an overview of the company’s ESG ratings and achievements in renewable energy and resource conservation.\n\n5. Risk Management and Future Outlook:\n- Identify key risks and the strategies for mitigating them.\n- Discuss the company’s outlook for the upcoming year, including growth opportunities, challenges, regulatory navigation, and strategic initiatives.\n\n6. Corporate Governance:\n- Introduce key Board members and any changes during the year.\n- What is the dividend policy, and what dividends were declared for the year?\n- The summary should be clear, concise, and provide an integrated analysis of the company’s financial health, operational efficiency, strategic initiatives, and future prospects. Also give Advantages, disadvantages and neutrals in term of impactness. \nNote: Do not add extra infromation from your side, use only those information which are available.Financial Data:\n{text}"

    # data = {
    #     "model": "gpt-4o-mini",
    #     "messages": [
    #         {"role": "system", "content": prompt},
    #         {"role": "user", "content": f"Financial Data:\n{text}"},
    #     ],
    # }
    for attempt in range(retries):
        try:
            # response = openai.chat.completions.create(
            #     model=data["model"],
            #     messages=data["messages"],
            #     temperature=data.get("temperature", 0),
            #     max_tokens=data.get("max_tokens", 2000),
            #     frequency_penalty=data.get("frequency_penalty", 0),
            #     presence_penalty=data.get("presence_penalty", 0),
            # )
            # analysis = response.choices[0].message.content

            # GEMINI
            model = genai.GenerativeModel("gemini-1.5-flash")
            analysis = model.generate_content(prompt)
            return analysis
        except Exception as e:
            logging.error(
                f"Gemini AI API error on attempt {attempt + 1}/{retries}: {e}"
            )
            if attempt < retries - 1:
                time.sleep(2)
            else:
                logging.error("Max retries reached. Returning empty analysis.")
                return "[ERROR: Unable to generate summary]"


async def generate_overall_summary(chunk_summaries, max_tokens_per_chunk=2000):
    """
    Generate overall concise and detailed summaries from chunk summaries.

    Parameters:
        chunk_summaries (list): List of chunk summaries containing analysis.
        max_tokens_per_chunk (int): Maximum tokens for each chunk.

    Returns:
        tuple: A tuple containing the overall concise summary and detailed summary.
    """
    chunk_summaries = await asyncio.gather(*chunk_summaries)

    numeric_chunks = [
        chunk for chunk in chunk_summaries if isinstance(chunk["sequence_number"], int)
    ]
    non_numeric_chunks = [
        chunk for chunk in chunk_summaries if isinstance(chunk["sequence_number"], str)
    ]

    numeric_chunks_sorted = sorted(numeric_chunks, key=lambda x: x["sequence_number"])

    combined_summary_text = " ".join(
        chunk["analysis"].text
        for chunk in numeric_chunks_sorted
        if hasattr(chunk["analysis"], "text")
    )

    text_chunks = await split_text_into_chunks(
        combined_summary_text, max_tokens_per_chunk=max_tokens_per_chunk
    )

    final_concise_summary_parts = []
    final_detailed_summary_parts = []

    for chunk in text_chunks:
        try:
            concise_summary_part = await gpt_overall_summarize(chunk, detailed=False)
            detailed_summary_part = await gpt_overall_summarize(chunk, detailed=True)
            final_concise_summary_parts.append(str(concise_summary_part))
            final_detailed_summary_parts.append(str(detailed_summary_part))
        except Exception as e:
            logging.error(f"Error generating summary for chunk: {chunk} - {e}")

    final_concise_overall_summary = " ".join(final_concise_summary_parts)
    final_detailed_overall_summary = " ".join(final_detailed_summary_parts)

    return final_concise_overall_summary, final_detailed_overall_summary


async def generate_financial_summary(
    file, url, user_id, background_tasks, chunk_size=50, overlap=2
):
    try:
        if file:
            input_binary = await file.read()
            with io.BytesIO(input_binary) as pdf_file:
                doc = fitz.open(stream=pdf_file, filetype="pdf")
        else:
            response = requests.get(url)
            if response.status_code == 200:
                input_binary = response.content
                with io.BytesIO(input_binary) as pdf_file:
                    doc = fitz.open(stream=pdf_file, filetype="pdf")
            else:
                print(f"Failed to retrieve PDF. Status code: {response.status_code}")

    except Exception as e:
        logging.critical(f"Unable to open the PDF file: {e}")
        return []

    # backgound process
    background_tasks.add_task(background_pinecone_task, doc, user_id)

    total_pages = doc.page_count
    # Check and print page groups to debug
    page_groups = [
        (i, min(i + chunk_size, total_pages))
        for i in range(0, total_pages, chunk_size - overlap)
    ]
    print("Generated page groups:", page_groups)
    if file:
        pdf_path = file.file
    else:
        pdf_path = url
    results = []
    # with ThreadPoolExecutor() as executor:
    #     future_to_page_group = {
    #         executor.submit(process_page_groups, doc, pdf_path, page_group, seq_num): seq_num
    #         for seq_num, page_group in enumerate(page_groups)
    #     }
    #     for future in as_completed(future_to_page_group):
    #         try:
    #             result = future.result()
    #             print(result)
    #             results.append(result)
    #         except Exception as e:
    #             logging.error(f"Error in processing a page group: {e}")
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(
                executor, process_page_groups, doc, pdf_path, page_group, seq_num
            )
            for seq_num, page_group in enumerate(page_groups)
        ]

        # Gather results from all tasks
        for task in tasks:
            result = await task  # Await each task to get its result
            results.append(result)

    if not results:
        logging.critical("No valid results were generated. Exiting.")
        return []

    concise_summary, detailed_summary = await generate_overall_summary(results)

    response = []
    response.append(
        {
            "sequence_number": "overall",
            "pages": "Overall Summary",
            "concise_analysis": concise_summary,
            "detailed_analysis": detailed_summary,
        }
    )

    return response
