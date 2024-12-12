import re
from fastapi import HTTPException, status
from server.db.base import SessionLocal
from server.models.ratio import Assessment, Company
import google.generativeai as genai
from dotenv import load_dotenv
from server.config import settings
import logging
import time
from server.utils.prompt import (
    cost_assessment_prompt_green,
    debt_assessment_prompt_green,
    equity_assessment_prompt_green,
    liquidity_assessment_prompt_green,
    management_assessment_prompt_green,
    operational_assessment_prompt_green,
    revenue_assessment_prompt_green,
    risk_assessment_prompt_green,
    summary,
)

load_dotenv()

gemini_ai_key = settings.DHARMIK_GEMINI_AI_KEY
genai.configure(api_key=gemini_ai_key)

import json

session = SessionLocal()

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


def filter_data(data):
    new_data = data.replace("```json\n", "").replace("```", "")
    return json.loads(new_data)


def assessment_green_flag():
    with open("ratio\\nsc.txt", "r", encoding="utf-8") as f:
        shares = f.readlines()
    # Create the model
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.3,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    for share in shares[210:]:
        share = share.strip("\n")
        logging.info(share)
        company = session.query(Company).filter(Company.share_symbol == share).first()
        if not company:
            continue

        company_details = {
            "share_name": company.share_name,
            "share_price": company.share_price,
            "date": company.current_date,
            "market_cap": company.market_cap,
            "high_low": company.high_low,
            "pe_ratio": company.pe_ratio,
            "book_value": company.book_value,
            "dividend_yield": company.dividend_yield,
            "roce": company.roce,
            "roe": company.roe,
            "face_value": company.face_value,
            "sectore": company.sectore,
            "industry": company.industry,
            "bse": company.bse,
            "nce": company.nse,
            "Chart": company.chart,
            "peer_comparison": company.s_peer_comparison,
            "quarterly_results": company.s_quarterly_results,
            "profit_loss": company.s_profit_loss,
            "balance_sheet": company.s_balance_sheet,
            "cash_flows": company.s_cash_flows,
            "ratios": company.s_ratios,
            "shareholding_pattern_quarterly": company.s_shareholding_pattern_quarterly,
            "shareholding_pattern_yearly": company.s_shareholding_pattern_yearly,
        }
        logging.info("Get Company details")

        # management_assessment_analysis
        prompt = management_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        management_analysis = model.generate_content(prompt)
        management_assessment_analysis = filter_data(management_analysis.text)
        logging.info("management assessment analysis")

        time.sleep(4)
        # liquidity_assessment_analysis
        prompt = liquidity_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        liquidity_analysis = model.generate_content(prompt)
        # pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        liquidity_assessment_analysis = filter_data(liquidity_analysis.text)
        logging.info("liquidity assessment analysis")

        time.sleep(4)
        # debt_assessment_analysis
        prompt = debt_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        debt_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        debt_assessment_analysis = filter_data(debt_analysis.text)
        logging.info("debt assessment analysis")

        time.sleep(4)
        # equity_assessment_analysis
        prompt = equity_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        equity_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        equity_assessment_analysis = filter_data(equity_analysis.text)
        logging.info("equity assessment analysis")

        time.sleep(4)
        # revenue_assessment_analysis
        prompt = revenue_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        revenue_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        revenue_assessment_analysis = filter_data(revenue_analysis.text)
        logging.info("revenue assessment analysis")

        time.sleep(4)
        # cost_assessment_analysis
        prompt = cost_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        cost_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        cost_assessment_analysis = filter_data(cost_analysis.text)
        logging.info("cost assessment analysis")

        time.sleep(4)
        # operational_assessment_analysis
        prompt = operational_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        operational_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        operational_assessment_analysis = filter_data(operational_analysis.text)
        logging.info("operational assessment analysis")

        time.sleep(4)
        # risk_assessment_analysis
        prompt = risk_assessment_prompt_green(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        risk_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        risk_assessment_analysis = filter_data(risk_analysis.text)
        logging.info("risk assessment analysis")

        assessment_details = {
            "management_assessment": management_assessment_analysis,
            "liquidity_assessment": liquidity_assessment_analysis,
            "debt_assessment": debt_assessment_analysis,
            "equity_assessment": equity_assessment_analysis,
            "revenue_assessment": revenue_assessment_analysis,
            "cost_assessment": cost_assessment_analysis,
            "operational_assessment": operational_assessment_analysis,
            "risk_assessment": risk_assessment_analysis,
        }

        time.sleep(4)
        prompt = summary(assessment_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        summary_details = model.generate_content(prompt)
        logging.info("risk assessment analysis")

        exist_data = (
            session.query(Assessment)
            .filter(Assessment.flag == "green", Assessment.share_symbol == share)
            .first()
        )
        if exist_data:
            exist_data.management_assessment = management_assessment_analysis
            exist_data.liquidity_assessment = liquidity_assessment_analysis
            exist_data.debt_assessment = debt_assessment_analysis
            exist_data.equity_assessment = equity_assessment_analysis
            exist_data.revenue_assessment = revenue_assessment_analysis
            exist_data.cost_assessment = cost_assessment_analysis
            exist_data.operational_assessment = operational_assessment_analysis
            exist_data.risk_assessment = risk_assessment_analysis
            exist_data.summary = summary_details.text

            session.commit()
            logging.info("Updated Data in DB")

        else:

            assessment_entry = Assessment(
                company_id=company.id,
                share_symbol=share,
                management_assessment=management_assessment_analysis,
                liquidity_assessment=liquidity_assessment_analysis,
                debt_assessment=debt_assessment_analysis,
                equity_assessment=equity_assessment_analysis,
                revenue_assessment=revenue_assessment_analysis,
                cost_assessment=cost_assessment_analysis,
                operational_assessment=operational_assessment_analysis,
                risk_assessment=risk_assessment_analysis,
                flag="green",
                summary=summary_details.text,
            )

            session.add(assessment_entry)
            session.commit()
            logging.info(" Data Stored in DB")


if __name__ == "__main__":
    assessment_green_flag()
