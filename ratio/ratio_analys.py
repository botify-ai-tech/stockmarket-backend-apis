import json
import time
from server.db.base import SessionLocal
from server.models.ratio import CalculateRatio, Company, Ratio
import google.generativeai as genai
from dotenv import load_dotenv
from server.config import settings
import logging

from fastapi import HTTPException, status

from server.utils.prompt import (
    coverage_ratio_prompt,
    efficiency_ratio_prompt,
    financial_ratio_prompt,
    growth_ratio_prompt,
    liquidity_ratios_prompt,
    profitability_ratio_prompt,
    solvency_ratio_prompt,
    valuation_ratios_prompt,
)

load_dotenv()

gemini_ai_key = settings.GEMINI_AI_KEY
genai.configure(api_key=gemini_ai_key)
from sqlalchemy import func

session = SessionLocal()

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


def filter_data(data):
    new_data = data.replace("```json\n", "").replace("```", "")
    return json.loads(new_data)


def ratio_analys():
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
    for share in shares[15:]:
        share = share.strip("\n")

        logging.info(share)

        # if session.query(Ratio).filter(Ratio.share_symbol == share).first():
        #     print("skip data")
        #     continue

        ratios = (
            session.query(CalculateRatio)
            .filter(CalculateRatio.share_symbol == share)
            .first()
        )

        if not ratios:
            with open("not_calculate_ratio.txt", "a") as f:
                f.write(share + "\n")
            continue

        liquidity_ratio = ratios.liquidity_ratio
        solvency_ratio = ratios.solvency_ratio
        efficiency_ratio = ratios.efficiency_ratio
        growth_ratio = ratios.growth_ratio
        coverage_ratio = ratios.coverage_ratio
        financial_ratio = ratios.financial_ratio
        profitability_ratio = ratios.profitability_ratio
        valuation_ratios = ratios.valuation_ratios

        # liquidity_ratio
        time.sleep(4)
        prompt = liquidity_ratios_prompt(liquidity_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        liquidity_analysis = model.generate_content(prompt)
        liquidity_ratio_analysis = filter_data(liquidity_analysis.text)
        logging.info("liquidity ratio analysis")

        # solvency_ratio
        time.sleep(4)
        prompt = solvency_ratio_prompt(solvency_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        solvency_analysis = model.generate_content(prompt)
        solvency_ratio_analysis = filter_data(solvency_analysis.text)
        logging.info("solvency ratio analysis")

        # efficiency_ratio
        time.sleep(4)
        prompt = efficiency_ratio_prompt(efficiency_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        efficiency_analysis = model.generate_content(prompt)
        efficiency_ratio_analysis = filter_data(efficiency_analysis.text)
        logging.info("efficiency ratio analysis")

        # growth_ratio
        time.sleep(4)
        prompt = growth_ratio_prompt(growth_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        growth_analysis = model.generate_content(prompt)
        growth_ratio_analysis = filter_data(growth_analysis.text)
        logging.info("growth ratio analysis")

        # coverage_ratio
        time.sleep(4)
        prompt = coverage_ratio_prompt(coverage_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        coverage_analysis = model.generate_content(prompt)
        coverage_ratio_analysis = filter_data(coverage_analysis.text)
        logging.info("coverage ratio analysis")

        # financial_ratio
        time.sleep(4)
        prompt = financial_ratio_prompt(financial_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        financial_analysis = model.generate_content(prompt)
        financial_ratio_analysis = filter_data(financial_analysis.text)
        logging.info("financial ratio analysis")

        # profitability_ratio
        time.sleep(4)
        prompt = profitability_ratio_prompt(profitability_ratio)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        profitability_analysis = model.generate_content(prompt)
        profitability_ratio_analysis = filter_data(profitability_analysis.text)
        logging.info("profitability ratio analysis")

        # valuation_ratios
        time.sleep(4)
        prompt = valuation_ratios_prompt(valuation_ratios)
        model = genai.GenerativeModel(
            "gemini-1.5-flash", generation_config=generation_config
        )
        valuation_analysis = model.generate_content(prompt)
        valuation_ratios_analysis = filter_data(valuation_analysis.text)
        logging.info("valuation ratio analysis")

        exist_data = session.query(Ratio).filter(Ratio.share_symbol == share).first()
        if exist_data:
            exist_data.liquidity_ratio = liquidity_ratio_analysis
            exist_data.solvency_ratio = solvency_ratio_analysis
            exist_data.efficiency_ratio = efficiency_ratio_analysis
            exist_data.growth_ratio = growth_ratio_analysis
            exist_data.coverage_ratio = coverage_ratio_analysis
            exist_data.financial_ratio = financial_ratio_analysis
            exist_data.profitability_ratio = profitability_ratio_analysis
            exist_data.valuation_ratios = valuation_ratios_analysis

            session.commit()
            logging.info("Updated Data in DB")
        else:
            ratio_entry = Ratio(
                company_id=ratios.company_id,
                share_symbol=share,
                liquidity_ratio=liquidity_ratio_analysis,
                solvency_ratio=solvency_ratio_analysis,
                efficiency_ratio=efficiency_ratio_analysis,
                growth_ratio=growth_ratio_analysis,
                coverage_ratio=coverage_ratio_analysis,
                financial_ratio=financial_ratio_analysis,
                profitability_ratio=profitability_ratio_analysis,
                valuation_ratios=valuation_ratios_analysis,
            )

            session.add(ratio_entry)
            session.commit()
            logging.info(" Data Stored in DB")


if __name__ == "__main__":
    ratio_analys()
