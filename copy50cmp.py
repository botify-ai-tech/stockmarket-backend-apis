import csv
from sqlalchemy.orm import Session
from server.models.ratio50 import Company50
from server.models.ratio import Company
from server.db.base import SessionLocal # adjust this path as needed
import pandas as pd


def load_nifty50_symbols(csv_path: str):
    NIFTY50_STOCKS = pd.read_csv(f"{csv_path}")["NIFTY50_STOCKS"].tolist()
    return NIFTY50_STOCKS


def migrate_to_company50(symbols: list[str]):
    db: Session = SessionLocal()

    try:
        for symbol in symbols:
            company = db.query(Company).filter(Company.share_symbol == symbol).first()

            if company:
                company50 = Company50(
                    id=company.id,
                    share_name=company.share_name,
                    current_date=company.current_date,
                    share_symbol=company.share_symbol,
                    share_price=company.share_price,
                    compnay_info_doc=company.compnay_info_doc,
                    share_price_percentage=company.share_price_percentage,
                    industry_pe=company.industry_pe,
                    sectore_pe=company.sectore_pe,
                    market_cap=company.market_cap,
                    high_low=company.high_low,
                    pe_ratio=company.pe_ratio,
                    pb_ratio=company.pb_ratio,
                    average_pe=company.average_pe,
                    sectore=company.sectore,
                    industry=company.industry,
                    enterprise_value=company.enterprise_value,
                    book_value=company.book_value,
                    dividend_yield=company.dividend_yield,
                    promoter_holding=company.promoter_holding,
                    eps=company.eps,
                    sales_growth=company.sales_growth,
                    profit_growth=company.profit_growth,
                    roce=company.roce,
                    cash=company.cash,
                    debt=company.debt,
                    roe=company.roe,
                    face_value=company.face_value,
                    bse=company.bse,
                    nse=company.nse,
                    chart=company.chart,
                    s_pros=company.s_pros,
                    s_cons=company.s_cons,
                    s_peer_comparison=company.s_peer_comparison,
                    s_quarterly_results=company.s_quarterly_results,
                    s_profit_loss=company.s_profit_loss,
                    s_balance_sheet=company.s_balance_sheet,
                    s_cash_flows=company.s_cash_flows,
                    s_ratios=company.s_ratios,
                    s_shareholding_pattern_quarterly=company.s_shareholding_pattern_quarterly,
                    s_shareholding_pattern_yearly=company.s_shareholding_pattern_yearly,
                    s_documents=company.s_documents,
                    t_strengths=company.t_strengths,
                    t_limitations=company.t_limitations,
                    t_quarterly_results=company.t_quarterly_results,
                    t_profit_loss=company.t_profit_loss,
                    t_balance_sheet_equity_and_liabilities=company.t_balance_sheet_equity_and_liabilities,
                    t_balance_sheet_assets=company.t_balance_sheet_assets,
                    t_cash_flows=company.t_cash_flows,
                )
                db.add(company50)

        db.commit()
        print("Migration complete.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    symbols = load_nifty50_symbols("NIFTY50_STOCKS.csv")
    migrate_to_company50(symbols)
