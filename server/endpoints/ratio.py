import os
from fastapi.responses import JSONResponse
from requests import Session

from fastapi import APIRouter, Depends, HTTPException

from server import crud, schemas
from server.endpoints.deps import get_db
from server.utils.auth import get_current_user
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

ratio_router = APIRouter()


@ratio_router.post("/ratio-analysis/{symbol}")
def get_company_symbol(
    symbol: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        ratio_details = crud.ratio.get_ratio_analysis(db, symbol)

        response = {
            "share_symbol": ratio_details.share_symbol,
            "liquidity_ratio": ratio_details.liquidity_ratio,
            "solvency_ratio": ratio_details.solvency_ratio,
            "efficiency_ratio": ratio_details.efficiency_ratio,
            "growth_ratio": ratio_details.growth_ratio,
            "coverage_ratio": ratio_details.coverage_ratio,
            "financial_ratio": ratio_details.financial_ratio,
            "profitability_ratio": ratio_details.profitability_ratio,
            "valuation_ratios": ratio_details.valuation_ratios,
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response,
                "message": "Ratio analysis fetch successfully. ",
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@ratio_router.post("/assessment/{symbol}")
def assessment(
    symbol: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        assessments = crud.ratio.get_by_symbol(db, symbol)
        if not assessments:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": [],
                    "message": "No any assessment details found..",
                },
            )

        final_output = {
            "symbol": assessments[0].share_symbol,
            "green": [],
            "red": [],
        }

        for assessment in assessments:
            if assessment.flag == "green":
                assessment_details_green = {
                    "asset_management": assessment.management_assessment,
                    "liquidity_assessment": assessment.liquidity_assessment,
                    "debt_assessment": assessment.debt_assessment,
                    "equity_assessment": assessment.equity_assessment,
                    "revenue_assessment": assessment.revenue_assessment,
                    "cost_assessment": assessment.cost_assessment,
                    "operational_assessment": assessment.operational_assessment,
                    "risk_assessment": assessment.risk_assessment,
                    "summary": assessment.summary,
                    "flag": assessment.flag,
                }
                final_output["green"].append(assessment_details_green)

            elif assessment.flag == "red":
                assessment_details_red = {
                    "liquidity_assessment": assessment.liquidity_assessment or [],
                    "debt_assessment": assessment.debt_assessment or [],
                    "equity_assessment": assessment.equity_assessment or [],
                    "management_assessment": assessment.management_assessment or [],
                    "revenue_assessment": assessment.revenue_assessment or [],
                    "cost_assessment": assessment.cost_assessment or [],
                    "capital_assessment": assessment.capital_assessment or [],
                    "dividend_assessment": assessment.dividend_assessment or [],
                    "earnings_assessment": assessment.earnings_assessment or [],
                    "receivables_assessment": assessment.receivables_assessment or [],
                    "valuation_assessment": assessment.valuation_assessment or [],
                    "miscellaneous_assessment": assessment.miscellaneous_assessment
                    or [],
                    "other_assessment": assessment.other_assessment or [],
                    "operational_assessment": assessment.operational_assessment or [],
                    "risk_assessment": assessment.risk_assessment or [],
                    "summary": assessment.summary,
                    "flag": assessment.flag,
                }
                final_output["red"].append(assessment_details_red)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": final_output,
                "message": "Assessment details found successfully.",
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@ratio_router.post("/stock-list/{symbol}")
def stock_list(
    symbol: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        company = crud.ratio.get_by_company_details(db, symbol)

        company_details = {
            "share_name": company.share_name,
            "share_price": company.share_price,
            "market_cap": company.market_cap,
            "high_low": company.high_low,
            "pe_ratio": company.pe_ratio,
            "sectore": company.sectore,
            "industry": company.industry,
            "enterprise_value": company.enterprise_value,
            "book_value": company.book_value,
            "dividend_yield": company.dividend_yield,
            "face_value": company.face_value,
            "bse": company.bse,
            "nse": company.nse,
            "roce": company.roce,
            "roe": company.roe,
            "eps": company.eps,
            "debt": company.debt,
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": company_details,
                "message": "stock details fetch successfully.",
            },
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@ratio_router.post("/companies")
def companies(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 1,
    limit: int = 10,
    search: str = None,
):
    try:
        companies = crud.ratio.get_all_companies(db, skip, limit, search)
        all_companies = []
        for company in companies:
            company_details = {
                "share_name": company.share_name,
                "share_symbol": company.share_symbol,
                "share_price": company.share_price,
                "high_low": company.high_low,
                "bse": company.bse,
                "nse": company.nse,
            }
            all_companies.append(company_details)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": all_companies,
                "message": "companies details fetch successfully.",
            },
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@ratio_router.post("/profit-loss/{symbol}")
def stock_list(
    symbol: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        company = crud.ratio.get_by_company_details(db, symbol)

        profit_loss = company.s_profit_loss

        compounded_sales_growth = profit_loss[-1].get("Compounded Sales Growth")
        compounded_profit_growth = profit_loss[-1].get("Compounded Profit Growth")
        stock_price_cagr = profit_loss[-1].get("Stock Price CAGR")
        return_on_equity = profit_loss[-1].get("Return on Equity")

        profit_loss_details = {
            "compounded_sales_growth": compounded_sales_growth,
            "compounded_profit_growth": compounded_profit_growth,
            "stock_price_cagr": stock_price_cagr,
            "return_on_equity": return_on_equity,
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": profit_loss_details,
                "message": "profit loss details fetch successfully.",
            },
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()
