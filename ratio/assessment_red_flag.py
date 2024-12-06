import json
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
    liquidity_assessment_prompt_red,
    debt_assessment_prompt_red,
    equity_assessment_prompt_red,
    asset_management_and_efficiency_prompt_red,
    profitability_assessment_prompt_red,
    cost_assessment_prompt_red,
    capital_expenditures_assessment_prompt_red,
    dividend_assessment_prompt_red,
    earnings_assessment_prompt_red,
    receivables_assessment_prompt_red,
    summary,
    valuation_assessment_prompt_red,
    miscellaneous_assessment_prompt_red,
    other_assessment_prompt_red,
)

load_dotenv()

gemini_ai_key = settings.GEMINI_AI_KEY
genai.configure(api_key=gemini_ai_key)


session = SessionLocal()

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

def filter_data(data):
    new_data = data.replace("```json\n", "").replace("```", "")
    return json.loads(new_data)

def assessment_red_flag():
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
    for share in shares[1:10]:
        share = share.strip("\n")
        logging.info(share)
        company = session.query(Company).filter(Company.share_symbol == share).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no company details found",
            )

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
        prompt = liquidity_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        liquidity_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        liquidity_assessment_analysis = filter_data(liquidity_analysis.text)
        logging.info("liquidity assessment analysis")

        time.sleep(4)
        # liquidity_assessment_analysis
        prompt = debt_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        debt_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        debt_assessment_analysis = filter_data(debt_analysis.text)
        logging.info("debt assessment analysis")

        time.sleep(4)
        # debt_assessment_analysis
        prompt = equity_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        equity_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        equity_assessment_analysis = filter_data(equity_analysis.text)
        logging.info("equity assessment analysis")

        time.sleep(4)
        # efficiency_assessment_analysis
        prompt = asset_management_and_efficiency_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        efficiency_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        management_assessment_analysis = filter_data(efficiency_analysis.text)
        logging.info("efficiency assessment analysis")

        time.sleep(4)
        # profitability_assessment_analysis
        prompt = profitability_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        profitability_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        revenue_assessment_analysis = filter_data(profitability_analysis.text)
        logging.info("profitability assessment analysis")

        time.sleep(4)
        # cost_assessment_analysis
        prompt = cost_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        cost_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        cost_assessment_analysis = filter_data(cost_analysis.text)
        logging.info("cost assessment analysis")

        time.sleep(4)
        # capital_assessment_analysis
        prompt = capital_expenditures_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        capital_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        capital_assessment_analysis = filter_data(capital_analysis.text)
        logging.info("capital assessment analysis")

        time.sleep(4)
        # dividend_assessment_analysis
        prompt = dividend_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        dividend_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        dividend_assessment_analysis = filter_data(dividend_analysis.text)
        logging.info("dividend assessment analysis")

        prompt = earnings_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        earnings_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        earnings_assessment_analysis = filter_data(earnings_analysis.text)
        logging.info("earnings assessment analysis")

        prompt = receivables_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        receivables_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        receivables_assessment_analysis = filter_data(receivables_analysis.text)
        logging.info("receivables assessment analysis")

        prompt = valuation_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        valuation_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        valuation_assessment_analysis = filter_data(valuation_analysis.text)
        logging.info("valuation assessment analysis")

        prompt = miscellaneous_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        miscellaneous_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        miscellaneous_assessment_analysis = filter_data(miscellaneous_analysis.text)
        logging.info("miscellaneous assessment analysis")

        prompt = other_assessment_prompt_red(company_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        other_analysis = model.generate_content(prompt)
        pattern = re.compile(r"\[(.*?)\]", re.DOTALL)
        other_assessment_analysis = filter_data(other_analysis.text)
        logging.info("other assessment analysis")

        assessment_details = {
            "liquidity_assessment": liquidity_assessment_analysis,
            "debt_assessment": debt_assessment_analysis,
            "equity_assessment": equity_assessment_analysis,
            "management_assessment": management_assessment_analysis,
            "revenue_assessment": revenue_assessment_analysis,
            "cost_assessment": cost_assessment_analysis,
            "capital_assessment": capital_assessment_analysis,
            "dividend_assessment": dividend_assessment_analysis,
            "earnings_assessment": earnings_assessment_analysis,
            "receivables_assessment": receivables_assessment_analysis,
            "valuation_assessment": valuation_assessment_analysis,
            "miscellaneous_assessment ": miscellaneous_assessment_analysis,
            "other_assessment ": other_assessment_analysis,
        }

        prompt = summary(assessment_details)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        summary_details = model.generate_content(prompt)
        logging.info("Summary generated")

        assessment_entry = Assessment(
            company_id=company.id,
            share_symbol=share,
            liquidity_assessment=liquidity_assessment_analysis,
            debt_assessment=debt_assessment_analysis,
            equity_assessment=equity_assessment_analysis,
            management_assessment=management_assessment_analysis,
            revenue_assessment=revenue_assessment_analysis,
            cost_assessment=cost_assessment_analysis,
            capital_assessment=capital_assessment_analysis,
            dividend_assessment=dividend_assessment_analysis,
            earnings_assessment=earnings_assessment_analysis,
            receivables_assessment=receivables_assessment_analysis,
            valuation_assessment=valuation_assessment_analysis,
            miscellaneous_assessment=miscellaneous_assessment_analysis,
            other_assessment=other_assessment_analysis,
            flag="red",
            summary=summary_details.text,
        )
        logging.info(" Data Stored in DB")

        session.add(assessment_entry)
        session.commit()


if __name__ == "__main__":
    assessment_red_flag()
