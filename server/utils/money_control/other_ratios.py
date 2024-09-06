import json


def calculate_cash_flow_to_sales_ratio(json_data, share_name):
    # Load JSON data if it's a string, otherwise assume it's already a dictionary
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Access the first item of the list if the data is encapsulated in a list
    screener_data = data.get(share_name).get("Screener")

    # Directly access 'Cash Flows' and 'Profit & Loss'
    cash_flows = screener_data["Cash Flows"]
    profit_loss = screener_data["Profit & Loss"]

    # Initialize dictionaries for cash flow and sales
    cash_from_operations = {}
    sales_data = {}
    cash_from_investing_activity = {}

    # Extract cash flow and sales data
    for entry in cash_flows:
        if entry.get("cash flows name") == "Cash from Operating Activity -":
            for year, value in entry.items():
                # print(value)
                if year.startswith("Mar"):
                    cash_from_operations[year] = float(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Sales -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    sales_data[year] = float(value.replace(",", ""))

    for entry in cash_flows:
        if entry.get("cash flows name") == "Cash from Investing Activity -":
            for year, value in entry.items():
                # print(value)
                if year.startswith("Mar"):
                    cash_from_investing_activity[year] = float(value.replace(",", ""))

    # Calculate the ratio for each year where data is available
    ratios_sales = {"Ratio": "Operating Cash Flow to Sales Ratio"}
    ratios_fcf = {"Ratio": "Free Cash Flow (FCF)"}

    for year in sorted(cash_from_operations.keys(), reverse=True)[:5]:
        if year in sales_data:
            # Calculate Operating Cash Flow to Sales Ratio
            operating_cash_flow_to_sales = cash_from_operations[year] / sales_data[year]
            ratios_sales[year] = f"{operating_cash_flow_to_sales:.4f}"

            # Calculate Free Cash Flow (FCF)
            free_cash_flow = (
                cash_from_operations[year] - cash_from_investing_activity[year]
            )
            ratios_fcf[year] = f"{free_cash_flow:.4f}"

    cash_flow_ratios = [ratios_sales, ratios_fcf]

    return {"Cash Flow Ratios": cash_flow_ratios}


def efficiency_ratios(json_data, share_name):

    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Access the first item of the list if the data is encapsulated in a list
    screener_data = data.get(share_name).get("Screener")

    receivables_turnover_ratio = {}
    sales_data = {}
    payables_turnover_ratio = {}
    average_payables = {}
    total_assets = {}
    current_liabilities = {}

    cash_flows = screener_data["Cash Flows"]
    profit_loss = screener_data["Profit & Loss"]
    balance_sheet = screener_data["Balance Sheet"]

    for entry in cash_flows:
        if entry.get("cash flows name") == "Receivables":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    receivables_turnover_ratio[year] = int(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Sales -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    sales_data[year] = int(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Expenses -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    payables_turnover_ratio[year] = int(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Trade Payables":
            # print(entry)
            for year, value in entry.items():
                if year.startswith("Mar"):
                    average_payables[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Total Assets":
            # print(entry)
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_assets[year] = int(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Total Liabilities":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    current_liabilities[year] = int(value.replace(",", ""))

    # print(average_payables)
    ratios_receivables_turnover = {"Ratio": "Receivables Turnover Ratio"}
    ratio_payables_turnover = {"Ratio": "Payables Turnover Ratio"}
    ratio_working_capital = {"Ratio": "Working Capital Turnover Ratio"}
    working_capital = {}

    for year in sorted(receivables_turnover_ratio.keys(), reverse=True)[:5]:
        if year in sales_data:
            # Calculate Operating Cash Flow to Sales Ratio
            if receivables_turnover_ratio[year] == 0:
                receivables_turnover_ratio[year] = 1
            operating_cash_flow_to_sales = (
                sales_data[year] / receivables_turnover_ratio[year]
            )
            ratios_receivables_turnover[year] = f"{operating_cash_flow_to_sales:.4f}"

    for year in sorted(payables_turnover_ratio.keys(), reverse=True)[:5]:
        if year in average_payables:
            # print(year)
            payables_turnover = payables_turnover_ratio[year] / average_payables[year]
            ratio_payables_turnover[year] = f"{payables_turnover:.4f}"

    for year in sorted(total_assets.keys(), reverse=True)[:5]:
        if year in current_liabilities:
            capital = total_assets[year] - current_liabilities[year]
            working_capital[year] = f"{capital:.4f}"

    for year in sorted(working_capital.keys(), reverse=True)[:5]:
        if year in sales_data:
            working_capital_value = float(working_capital[year])
        # Check if the working capital is zero and handle accordingly
        if working_capital_value == 0.0:
            working_capital_value = 1.0  #
            working_capital_turnover = sales_data[year] / working_capital_value
            ratio_working_capital[year] = f"{working_capital_turnover:.4f}"

    efficiency_ratios = [
        ratios_receivables_turnover,
        ratio_payables_turnover,
        ratio_working_capital,
    ]

    return {"Efficiency Ratios": efficiency_ratios}


def profitability_ratios(json_data, share_name):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    screener_data = data.get(share_name).get("Screener")

    profit_loss = screener_data["Profit & Loss"]

    # ebitda_margin
    operating_profit = {}
    depreciation = {}
    sales_data = {}

    for entry in profit_loss:
        if entry.get("profit loss name") == "Sales -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    sales_data[year] = int(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Operating Profit":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    operating_profit[year] = int(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Depreciation":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    depreciation[year] = int(value.replace(",", ""))

    ebitda = {}
    ebitda_margin = {"Ratio": "EBITDA Margin"}

    for year in sorted(operating_profit.keys(), reverse=True)[:5]:
        if year in depreciation:
            ebitda[year] = operating_profit[year] + depreciation[year]

    for year in sorted(ebitda.keys(), reverse=True)[:5]:
        if year in sales_data:
            ebitda_margin_ratio = (ebitda[year] / sales_data[year]) * 100
            ebitda_margin[year] = f"{ebitda_margin_ratio:.4f}"

    profitability = [ebitda_margin]

    return {"Profitability Ratios": profitability}


def market_valuation_ratios(json_data, share_name):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    screener_data = data.get(share_name).get("Screener")

    profit_loss = screener_data["Profit & Loss"]
    balance_sheet = screener_data["Balance Sheet"]
    market_cap = screener_data["share_info"][0].get("Market Cap")
    market_cap = float(market_cap.replace(",", "").replace(" Cr.", "").replace("₹", ""))

    sales_data = {}
    total_debt = {}
    cash_equivalents = {}

    for entry in profit_loss:
        if entry.get("profit loss name") == "Sales -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    sales_data[year] = int(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Borrowings -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_debt[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Cash Equivalents":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    cash_equivalents[year] = float(value.replace(",", ""))

    market_cap_ratios = {"Ratio": "EV/Sales"}
    ev = {}
    for year in sorted(sales_data.keys(), reverse=True)[:5]:
        if year in total_debt and year in cash_equivalents:
            enterprise_value = market_cap + total_debt[year] - cash_equivalents[year]
            ev[year] = enterprise_value

    for year in sorted(ev.keys(), reverse=True)[:5]:
        if year in sales_data:
            ev_to_sales = ev[year] / sales_data[year]
            market_cap_ratios[year] = f"{ev_to_sales:.4f}"

    return {"Market Valuation Ratios": market_cap_ratios}


def additional_ratios(json_data, share_name):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    screener_data = data.get(share_name).get("Screener")

    profit_loss = screener_data["Profit & Loss"]
    balance_sheet = screener_data["Balance Sheet"]

    equity_capital = {}
    reserves = {}
    total_assets = {}
    total_liabilities = {}
    operating_profit = {}
    other_income = {}
    total_debt = {}
    net_profit = {}

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Equity Capital":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    equity_capital[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Reserves":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    reserves[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Total Assets":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_assets[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Total Liabilities":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_liabilities[year] = float(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Operating Profit":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    operating_profit[year] = float(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Other Income":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    other_income[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Borrowings -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_debt[year] = float(value.replace(",", ""))

    for entry in profit_loss:
        if entry.get("profit loss name") == "Net Profit":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    net_profit[year] = float(value.replace(",", ""))

    equity = {}
    ebit = {}
    cost_of_investment = {}
    equity_ratio = {"Ratio": "Equity Ratio "}
    debt_ratio = {"Ratio": "Debt Ratio"}
    return_on_investment = {"Ratio": "Return on Investment"}

    for year in sorted(equity_capital.keys(), reverse=True)[:5]:
        if year in reserves:
            equity[year] = equity_capital[year] + reserves[year]

    for year in sorted(equity.keys(), reverse=True)[:5]:
        if year in total_assets:
            debt_to_equity = equity[year] / total_assets[year]
            equity_ratio[year] = f"{debt_to_equity:.4f}"

    for year in sorted(total_liabilities.keys(), reverse=True)[:5]:
        if year in total_assets:
            debt_to_assets = total_liabilities[year] / total_assets[year]
            debt_ratio[year] = f"{debt_to_assets:.4f}"

    for year in sorted(operating_profit.keys(), reverse=True)[:5]:
        if year in other_income:
            ebit[year] = operating_profit[year] + other_income[year]

    for year in sorted(total_debt.keys(), reverse=True)[:5]:
        if year in equity:
            cost_of_investment[year] = total_debt[year] + equity[year]

    for year in sorted(net_profit.keys(), reverse=True)[:5]:
        if year in cost_of_investment:
            roi = net_profit[year] / cost_of_investment[year]
            return_on_investment[year] = f"{roi:.4f}"

    additional_ratios = [equity_ratio, debt_ratio, return_on_investment]

    return {"Additional Ratios": additional_ratios}


def other_ratios(json_data, share_name):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    screener_data = data.get(share_name).get("Screener")

    balance_sheet = screener_data["Balance Sheet"]
    cash_flows = screener_data["Cash Flows"]
    market_cap = screener_data["share_info"][0].get("Market Cap")
    market_cap = float(market_cap.replace(",", "").replace(" Cr.", "").replace("₹", ""))

    cash_from_operations = {}
    cash_from_investing_activity = {}
    trade_payables = {}
    advance_from_customers = {}
    other_liability_items = {}


    for entry in cash_flows:
        if entry.get("cash flows name") == "Cash from Operating Activity -":
            for year, value in entry.items():
                # print(value)
                if year.startswith("Mar"):
                    cash_from_operations[year] = float(value.replace(",", ""))

    for entry in cash_flows:
        if entry.get("cash flows name") == "Cash from Investing Activity -":
            for year, value in entry.items():
                # print(value)
                if year.startswith("Mar"):
                    cash_from_investing_activity[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Trade Payables":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    trade_payables[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Advance from Customers":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    if value == "":
                        advance_from_customers[year] = 0.0
                    else:
                        advance_from_customers[year] = float(value.replace(",", ""))

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Other liability items":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    other_liability_items[year] = float(value.replace(",", ""))

    fcf = {}
    current_liabilities_ration = {}

    price_to_free_cash_flow = {"Ratio": "Free Cash Flow(FCF)"}
    operating_cash_flow_ratio = {
        "Ratio": "Operating Cash Flow Ratio"
    }

    for year in sorted(cash_from_operations.keys(), reverse=True)[:5]:
        if year in cash_from_investing_activity:
            free_cash_flow = (
                cash_from_operations[year] - cash_from_investing_activity[year]
            )
            fcf[year] = free_cash_flow

    for year in sorted(fcf.keys(), reverse=True)[:5]:
        fcf_yield = market_cap / fcf[year]
        price_to_free_cash_flow[year] = f"{fcf_yield:.4f}"

    for year in sorted(advance_from_customers.keys(), reverse=True)[:5]:
        if year in trade_payables and year in other_liability_items:
            current_liabilities = (
                trade_payables[year]
                + advance_from_customers[year]
                + other_liability_items[year]
            )
            current_liabilities_ration[year] = f"{current_liabilities:.4f}"

    for year in sorted(cash_from_operations.keys(), reverse=True)[:5]:
        if year in current_liabilities_ration:
            current_liability_value = float(current_liabilities_ration[year])
            operating_cash_flow_ = cash_from_operations[year] / current_liability_value
            operating_cash_flow_ratio[year] = f"{operating_cash_flow_:.4f}"

    other_ratio = [price_to_free_cash_flow, operating_cash_flow_ratio]

    return {"Other Ratios": other_ratio}


# def economic_value(screener_data, current_liabilities_ration, market_cap):

#     profit_loss = screener_data["Profit & Loss"]
#     balance_sheet = screener_data["Balance Sheet"]

#     # ebitda_margin
#     operating_profit = {}
#     tax = {}
#     profit_before_tax = {}
#     nopat = {}
#     total_assets = {}
#     total_debt = {}

#     for entry in profit_loss:
#         if entry.get("profit loss name") == "Operating Profit":
#             for year, value in entry.items():
#                 if year.startswith("Mar"):
#                     operating_profit[year] = int(value.replace(",", ""))

#     for entry in profit_loss:
#         if entry.get("profit loss name") == "Tax %":
#             for year, value in entry.items():
#                 if year.startswith("Mar"):
#                     tax[year] = int(value.replace(",", ""))

#     for entry in profit_loss:
#         if entry.get("profit loss name") == "Profit Before Tax":
#             for year, value in entry.items():
#                 if year.startswith("Mar"):
#                     profit_before_tax[year] = int(value.replace(",", ""))

#     for entry in balance_sheet:
#         if entry.get("balance sheet name") == "Total Assets":
#             for year, value in entry.items():
#                 if year.startswith("Mar"):
#                     total_assets[year] = int(value.replace(",", ""))

#     for entry in balance_sheet:
#         if entry.get("balance sheet name") == "Borrowings -":
#             for year, value in entry.items():
#                 if year.startswith("Mar"):
#                     total_debt[year] = float(value.replace(",", ""))

#     tax_rate = {}
#     capital_employed = {}
#     v = {}

#     for year in sorted(tax.keys(), reverse=True)[:5]:
#         if year in profit_before_tax:
#             tax_rate[year] = (tax[year] / 100) / profit_before_tax[year]

#     for year in sorted(operating_profit.keys(), reverse=True)[:5]:
#         if year in tax_rate:
#             nopat[year] = operating_profit[year] * (1 - tax_rate[year])

#     for year in sorted(total_assets.keys(), reverse=True)[:5]:
#         if year in current_liabilities_ration:
#             capital_employed[year] = (
#                 total_assets[year] - current_liabilities_ration[year]
#             )

#     for year in sorted(total_debt.keys(), reverse=True)[:5]:
#         v[year] = market_cap + total_debt[year]


def convert_to_float(value):
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return 0.0


def risk_and_solvency_ratios(json_data, share_name):
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    screener_data = data.get(share_name).get("Screener")

    balance_sheet = screener_data["Balance Sheet"]
    profit_loss = screener_data["Profit & Loss"]
    cash_flows = screener_data["Cash Flows"]
    summary = screener_data.get("share_info", {})
    
    market_cap_data = next((item for item in summary if "Market Cap" in item), None)
    market_cap = int(market_cap_data["Market Cap"].replace("\u20b9", "").replace(" Cr.", "").replace(",", "")) 
    
    # Extract data for T1 to T5
    working_capital = {}
    total_assets = {}
    retained_earnings = {}
    ebit = {}
    total_liabilities = {}
    sales_data = {}

    current_liabilities = {}

    for entry in balance_sheet:
        if entry.get("balance sheet name") == "Total Assets":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_assets[year] = int(value.replace(",", ""))

        if entry.get("balance sheet name") == "Reserves":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    retained_earnings[year] = int(value.replace(",", ""))

        if entry.get("balance sheet name") == "Total Liabilities":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    total_liabilities[year] = int(value.replace(",", ""))

        if entry.get("balance sheet name") in ["Trade Payables", "Advance from Customers", "Other liability items"]:
            for year, value in entry.items():
                if year.startswith("Mar"):
                    if year not in current_liabilities:
                        current_liabilities[year] = 0
                    current_liabilities[year] += convert_to_float(value)

    for year in total_assets.keys():
        if year in current_liabilities:
            working_capital[year] = total_assets[year] - current_liabilities[year]

    for entry in profit_loss:
        if entry.get("profit loss name") == "Operating Profit":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    ebit[year] = int(value.replace(",", ""))
        
        if entry.get("profit loss name") == "Other Income":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    if year in ebit:
                        ebit[year] += int(value.replace(",", ""))
                    else:
                        ebit[year] = int(value.replace(",", ""))

        if entry.get("profit loss name") == "Sales -":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    sales_data[year] = int(value.replace(",", ""))

    # Calculate Altman Z-Score
    altman_z_score = {"Ratio": "Altman Z-Score"}
    for year in sorted(total_assets.keys(), reverse=True)[:5]:
        if year in working_capital and year in retained_earnings and year in ebit and year in total_liabilities:
            t1 = working_capital[year] / total_assets[year]
            t2 = retained_earnings[year] / total_assets[year]
            t3 = ebit[year] / total_assets[year]
            t4 = market_cap / total_liabilities[year]
            t5 = sales_data.get(year, 0) / total_assets[year]

            z_score = (1.2 * t1) + (1.4 * t2) + (3.3 * t3) + (0.6 * t4) + (1.0 * t5)
            altman_z_score[year] = f"{z_score:.4f}"

    # Calculate DSCR
    dscr = {"Ratio": "Debt Service Coverage Ratio (DSCR)"}
    interest_paid = {}
    principal_repayment = {}

    for entry in cash_flows:
        if entry.get("cash flows name") == "Interest paid fin":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    interest_paid[year] = int(value.replace(",", ""))

        if entry.get("cash flows name") == "Repayment of borrowings":
            for year, value in entry.items():
                if year.startswith("Mar"):
                    principal_repayment[year] = int(value.replace(",", ""))

    for year in sorted(ebit.keys(), reverse=True)[:5]:
        if year in interest_paid and year in principal_repayment:
            total_debt_service = interest_paid[year] + principal_repayment[year]
            if total_debt_service == 0:
                total_debt_service = 1 
            dscr_ratio = ebit[year] / total_debt_service
            dscr[year] = f"{dscr_ratio:.4f}"

    solvency_ratios = [altman_z_score, dscr]

    return {"Risk and Solvency Ratios": solvency_ratios}





