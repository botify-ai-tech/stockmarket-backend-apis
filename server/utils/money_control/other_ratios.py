def liquidity_ratios(all_screener_data_dict, share_name):

    liquidity_ratios_list = []

    inventory_ = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    cash_flow = all_screener_data_dict[share_name]["Screener"]["Cash Flows"]

    current_assets = next(
        item for item in inventory_ if item["balance sheet name"] == "Other Assets -"
    )
    inventory = next(
        (item for item in inventory_ if item["balance sheet name"] == "Inventories"), None
    ) 
    prepaid_expenses = next(
        item for item in inventory_ if item["balance sheet name"] == "Other asset items"
    )
    cash_and_equivalents = next(
        item for item in inventory_ if item["balance sheet name"] == "Cash Equivalents"
    )
    cash_flow_operations = next((
        item
        for item in cash_flow
        if item["cash flows name"] == "Cash from Operating Activity -"), None
    )

    long_term_borrowings = next(
        (item
        for item in inventory_
        if item["balance sheet name"] == "Long term Borrowings"), None
    )
    short_term_borrowings = next(
        (item for item in inventory_ if item["balance sheet name"] == "Short term Borrowings"), None
    )
    lease_liabilities = next(
        (item for item in inventory_ if item["balance sheet name"] == "Lease Liabilities"), None
    )
    other_liabilities = next(
        (item
        for item in inventory_
        if item["balance sheet name"] == "Other Liabilities -"), None
    )

    current_liabilities = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not long_term_borrowings :
            current_liabilities[year] = 0.0
            continue
        if not long_term_borrowings.get(year) :
            current_liabilities[year] = 0.0
            continue
        long_term_borrowings_ = (
    0.0 if long_term_borrowings is None else float(long_term_borrowings[year].replace(",", ""))
)

        short_term_borrowings_ = 0.0 if short_term_borrowings is None else float(short_term_borrowings[year].replace(",", ""))
        lease_liabilities_ = 0.0 if lease_liabilities is None else float(lease_liabilities[year].replace(",", ""))
        other_liabilities_ = 0.0 if other_liabilities is None else float(other_liabilities[year].replace(",", ""))
        liabilities = (
            long_term_borrowings_
            + short_term_borrowings_
            + lease_liabilities_
            + other_liabilities_
        )
        current_liabilities[year] = liabilities

    # Calculate Current Ratio for each year
    current_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not current_assets:
            current_ratio[year] = 0.0
            continue
        if not current_assets.get(year):
            current_ratio[year] = 0.0
            continue
        assets = float(current_assets[year].replace(",", ""))
        liabilities = current_liabilities[year]
        if liabilities != 0:
            ratio = round(assets / liabilities, 2)
        else:
            ratio = None  # Handle division by zero
        current_ratio[year] = ratio

    quick_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not current_assets:
            quick_ratio[year] = 0.0
            continue
        if not current_assets.get(year):
            quick_ratio[year] = 0.0
            continue
        assets = 0.0 if current_assets is None else float(str(current_assets[year]).replace(",", ""))
        inv = 0.0 if inventory is None else float(inventory[year].replace(",", ""))
        pre_exp = float(prepaid_expenses[year].replace(",", ""))
        liabilities = current_liabilities[year]
        if liabilities != 0:
            ratio = round((assets - inv - pre_exp) / liabilities, 2)
        else:
            ratio = None  # Handle division by zero
        quick_ratio[year] = ratio

    cash_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not cash_and_equivalents:
            cash_ratio[year] = 0.0
            continue
        if not cash_and_equivalents.get(year):
            cash_ratio[year] = 0.0
            continue
        cash = float(cash_and_equivalents[year].replace(",", ""))
        liabilities = current_liabilities[year]
        if liabilities != 0:
            ratio = round(cash / liabilities, 2)
        else:
            ratio = None  # Handle division by zero
        cash_ratio[year] = ratio

    operating_cash_flow_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not cash_flow_operations:
            operating_cash_flow_ratio[year] = 0.0
            continue
        if not cash_flow_operations.get(year):
            operating_cash_flow_ratio[year] = 0.0
            continue
        cash_flow = 0.0 if cash_flow_operations is None else float(cash_flow_operations[year].replace(",", ""))
        liabilities = current_liabilities[year]
        if liabilities != 0:
            ratio = round(cash_flow / liabilities, 2)
        else:
            ratio = None  # Handle division by zero
        operating_cash_flow_ratio[year] = ratio

    liquidity_ratios_list.append(
        {
            "Current Ratios": current_ratio,
            "Quick Ratios": quick_ratio,
            "Cash Ratios": cash_ratio,
            "Operating Cash Flow Ratios": operating_cash_flow_ratio,
        }
    )

    return liquidity_ratios_list


def solvency_ratios(all_screener_data_dict, share_name):

    solvency_ratios_detail = []

    balance = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    profit = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]

    long_term_borrowings = next(
        (item for item in balance if item["balance sheet name"] == "Long term Borrowings"), None
    )
    short_term_borrowings = next(
        (item for item in balance if item["balance sheet name"] == "Short term Borrowings"), None
    )
    other_borrowings = next(
        (item for item in balance if item["balance sheet name"] == "Other Borrowings"), None
    )

    equity_capital = next(
        item for item in balance if item["balance sheet name"] == "Equity Capital"
    )

    reserves = next(
        item for item in balance if item["balance sheet name"] == "Reserves"
    )

    operating_profit = next((item for item in profit if item.get("profit loss name") == "Operating Profit"), None)
    exceptional_items = next(
        (item for item in profit if item.get("profit loss name") == "Exceptional items"), None
    )
    other_income_normal = next(
        (item for item in profit if item.get("profit loss name") == "Other income normal"), None
    )
    interest = next(item for item in profit if item.get("profit loss name") == "Interest")

    borrowings = next(
        item for item in balance if item["balance sheet name"] == "Borrowings -"
    )

    total_assets = next(
        item for item in balance if item["balance sheet name"] == "Total Assets"
    )

    debt_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not borrowings.get(year):
            debt_ratio[year] = 0.0
            continue
        borrowings_ = float(borrowings[year].replace(",", ""))
        assets = float(total_assets[year].replace(",", ""))

        if assets == 0:
            assets = 1
        ratio = round(borrowings_ / assets, 2)
        debt_ratio[year] = ratio

    equity_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not equity_capital.get(year):
            equity_ratio[year] = 0.0
            continue
        equity_capital_ = float(equity_capital[year].replace(",", ""))
        reserves_ = float(reserves[year].replace(",", ""))
        ratio = round(equity_capital_ + reserves_, 2)
        equity_ratio[year] = ratio

    debt_to_equity_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if equity_ratio[year] == 0:
            equity_ratio[year] = 1
            continue
        debt_to_equity_ratio_ = debt_ratio[year] / equity_ratio[year]
        ratio = round(debt_to_equity_ratio_, 2)
        debt_to_equity_ratio[year] = ratio
    # ---------------------------------------------------
    ebit = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not operating_profit:
            ebit[year] = 0
            continue
        if not operating_profit.get(year):
            ebit[year] = 0
            continue
        operating_profit_ = 0.0 if operating_profit is None else float(operating_profit[year].replace(",", ""))
        exceptional_items_ = 0.0 if exceptional_items is None else float(exceptional_items[year].replace(",", ""))
        other_income_normal_ =  0.0 if other_income_normal is None else float(other_income_normal[year].replace(",", ""))

        ebit_data = operating_profit_ + other_income_normal_ - exceptional_items_
        ebit[year] = ebit_data

    interest_coverage_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not interest.get(year):
            interest_coverage_ratio[year] = 0
            continue
        interest_ = float(interest[year].replace(",", ""))
        if interest_ == 0:
            interest_ = 1
        coverage_ratio = ebit[year] / interest_

        ratio = round(coverage_ratio, 2)
        interest_coverage_ratio[year] = ratio
    # ------------------------------------------
    total_borrowing = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        
        if not long_term_borrowings:
            total_borrowing[year] = 0.0
            continue
        if not long_term_borrowings.get(year):
            total_borrowing[year] = 0.0
            continue
        long_borrowings =  0.0 if long_term_borrowings is None else float(long_term_borrowings[year].replace(",", ""))
        short_borrowings = 0.0 if short_term_borrowings is None else float(short_term_borrowings[year].replace(",", ""))
        other_borrowing = 0.0 if other_borrowings is None else (float(other_borrowings[year].replace(",", "")) if other_borrowings[year] != '' else 0.0)

        ratio = long_borrowings + short_borrowings + other_borrowing
        total_borrowing[year] = ratio

    years = list(total_borrowing.keys())
    principal_repayments = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        repayment = abs(
            float(total_borrowing[previous]) - float(total_borrowing[current])
        )
        principal_repayments[current] = repayment

    tds = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not interest:
            tds[year] = 0.0
            continue
        if not interest.get(year):
            tds[year] = 0.0
            continue
        interest_ = float(interest[year].replace(",", ""))
        ratio = interest_ + principal_repayments[year]
        tds[year] = ratio

    noi = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not operating_profit:
            noi[year] = 0.0
            continue
        if not operating_profit.get(year):
            noi[year] = 0.0
            continue
        if not other_income_normal:
            noi[year] = 0.0
            continue
        if not other_income_normal.get(year):
            noi[year] = 0.0
            continue
        operating_profit_ = float(operating_profit[year].replace(",", ""))
        other_income_normal_ = float(other_income_normal[year].replace(",", ""))
        noi_data = operating_profit_ + other_income_normal_
        noi[year] = noi_data

    debt_service_coverage_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not noi:
                debt_service_coverage_ratio[year] = 0
                continue
        if not noi.get(year):
                debt_service_coverage_ratio[year] = 0
                continue
        if tds[year] == 0:
            tds[year] = 1
        ratio = round(noi[year] / tds[year], 2)
        debt_service_coverage_ratio[year] = ratio

    solvency_ratios_detail.append(
        {
            "Debt Ratio": debt_ratio,
            "Debt to Equity Ratio": debt_to_equity_ratio,
            "Interest Coverage Ratio": interest_coverage_ratio,
            "Debt Service Coverage Ratio": debt_service_coverage_ratio,
        }
    )

    return solvency_ratios_detail


def efficiency_ratios(all_screener_data_dict, share_name):

    all_efficiency_ratios = []

    balance = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    profit = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]

    total_assets = next(
        item for item in balance if item["balance sheet name"] == "Total Assets"
    )
    sales = next((item for item in profit if item.get("profit loss name") == "Sales -"), None)
    material_cost = next(
        (item for item in profit if item.get("profit loss name") == "Material Cost % +"), None
    )
    manufacturing_cost = next(
        (item for item in profit if item.get("profit loss name") == "Manufacturing Cost %"), None
    )
    inventories = next(
        (item for item in balance if item["balance sheet name"] == "Inventories"), None
    )
    receivables = next(
        (item
        for item in balance
        if item["balance sheet name"] in ["Trade receivables", "Trade receivables +"]), None
    )

    cal_total_assets = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not total_assets:
            cal_total_assets[year] = 0.0
            continue
        if not total_assets.get(year):
            cal_total_assets[year] = 0.0
            continue
        total_assets_ = float(total_assets[year].replace(",", ""))
        cal_total_assets[year] = total_assets_

    years = list(cal_total_assets.keys())
    average_total_assets = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        repayment = (cal_total_assets[previous] + cal_total_assets[current]) / 2
        average_total_assets[current] = repayment

    asset_turnover_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            asset_turnover_ratio[year] = 0.0
            continue

        if not sales.get(year):
            asset_turnover_ratio[year] = 0.0
            continue
        net_sale = float(sales[year].replace(",", ""))
        if average_total_assets[year] == 0:
            average_total_assets[year] = 1
        ratio = round(net_sale / average_total_assets[year], 2)
        asset_turnover_ratio[year] = ratio
    # -------------------------------------------------
    cogs = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            cogs[year] = 0.0
            continue
        if not sales.get(year):
            cogs[year] = 0.0
            continue
        net_sale = float(sales[year].replace(",", ""))
        
        material_cost_ = 0.0 if material_cost is None else float(material_cost[year].replace(",", "").replace("%", "")) if material_cost[year] else 0.0
        manufacturing_cost_ = 0.0 if  manufacturing_cost is None else float(
            manufacturing_cost[year].replace(",", "").replace("%", "")
        ) if manufacturing_cost[year] else 0.0
        if manufacturing_cost_ == 0:
            manufacturing_cost_ = 1
        ratio = round(net_sale * (material_cost_ + manufacturing_cost_) / 100, 2)
        cogs[year] = ratio

    cal_inventories = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not inventories:
            cal_inventories[year] = 0.0
            continue
        if not inventories.get(year):
            cal_inventories[year] = 0.0
            continue
        total_inventories_ = 0.0 if inventories is None else float(inventories[year].replace(",", ""))
        cal_inventories[year] = total_inventories_

    years = list(cal_inventories.keys())
    average_total_inventories = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        repayment = (cal_inventories[previous] + cal_inventories[current]) / 2
        average_total_inventories[current] = repayment

    inventory_turnover_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if average_total_inventories[year] == 0.0:
            average_total_inventories[year] = 1.0
        inventory_turnover_ratio[year] = round(
            cogs[year] / average_total_inventories[year], 2
        )
    # -----------------------------------------
    accounts_receivable = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not receivables:
            accounts_receivable[year] = 0.0
            continue
        if not receivables.get(year):
            accounts_receivable[year] = 0.0
            continue
        ratio = 0.0 if receivables is None else float(receivables[year].replace(",", ""))
        accounts_receivable[year] = ratio

    years = list(accounts_receivable.keys())
    trade_receivables = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        repayment = round(
            (float(accounts_receivable[previous]) + float(accounts_receivable[current]))
            / 2,
            2,
        )
        trade_receivables[current] = repayment

    receivables_turnover_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            receivables_turnover_ratio[year] = 0.0
            continue
        if not sales.get(year):
            receivables_turnover_ratio[year] = 0.0
            continue
        net_sale = float(sales[year].replace(",", ""))

        if trade_receivables[year] == 0:
            trade_receivables[year] = 1
        ratio = round(net_sale / trade_receivables[year], 2)
        receivables_turnover_ratio[year] = ratio

    # -----------------------------------------------------------
    dsi = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not inventory_turnover_ratio:
            dsi[year] = 0.0
            continue
        if not inventory_turnover_ratio.get(year):
            dsi[year] = 0.0
            continue
        if inventory_turnover_ratio[year]:
            inventory_turnover_ratio[year] = 1
        ratio = round(365 / inventory_turnover_ratio[year], 2)
        dsi[year] = ratio

    # ----------------------------------------
    receivable_days = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not receivables_turnover_ratio:
            receivable_days[year] = 0.0
            continue
        if not receivables_turnover_ratio.get(year):
            receivable_days[year] = 0.0
            continue
        if receivables_turnover_ratio[year] == 0:
            receivables_turnover_ratio[year] = 1
        ratio = round(365 / receivables_turnover_ratio[year], 2)
        receivable_days[year] = ratio

    all_efficiency_ratios.append(
        {
            "Asset Turnover Ratio": asset_turnover_ratio,
            "Inventory Turnover Ratio": inventory_turnover_ratio,
            "Receivables Turnover Ratio": receivables_turnover_ratio,
            "Days Sales in Inventory Ratio": dsi,
            "Receivable Days": receivable_days,
        }
    )

    return all_efficiency_ratios


def growth_ratios(all_screener_data_dict, share_name):

    all_growth_ratios = []
    balance = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    profit = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]

    sales = next((item for item in profit if item.get("profit loss name") == "Sales -"), None)
    operating_profit = next(
        (item for item in profit if item.get("profit loss name") == "Operating Profit"), None
    )
    eps = next(item for item in profit if item.get("profit loss name") == "EPS in Rs")
    net_profit = next(
        (item for item in profit if item.get("profit loss name") == "Net Profit -"), None
    )
    total_assets = next(
        item for item in balance if item["balance sheet name"] == "Total Assets"
    )

    cal_sales = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not sales:
            cal_sales[year] = 0
            continue
        if not sales.get(year):
            cal_sales[year] = 0
            continue
        total_sale = float(sales[year].replace(",", ""))
        cal_sales[year] = total_sale

    years = list(cal_sales.keys())
    revenue_growth_rate = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]

        if cal_sales[previous] == 0:
            cal_sales[previous] = 1
        sale_ = round(
            ((cal_sales[current] - cal_sales[previous]) / cal_sales[previous]) * 100, 2
        )
        revenue_growth_rate[current] = f"{sale_}%"

    # --------------------------------------------------------
    cal_operating_profit = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not operating_profit:
            cal_operating_profit[year] = 0
            continue

        if not operating_profit.get(year):
            cal_operating_profit[year] = 0
            continue
        total_operating_profit = 0.0 if operating_profit is None else  float(operating_profit[year].replace(",", ""))
        cal_operating_profit[year] = total_operating_profit

    years = list(cal_operating_profit.keys())
    operating_profit_growth_rate = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        if cal_operating_profit[previous] ==0:
            cal_operating_profit[previous] =1 
        operating_profit_ = round(
            (
                (cal_operating_profit[current] - cal_operating_profit[previous])
                / cal_operating_profit[previous]
            )
            * 100,
            2,
        )
        operating_profit_growth_rate[current] = f"{operating_profit_}%"

    # --------------------------------------------
    cal_eps = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if eps:
            cal_eps[year] = 0
            continue

        if not eps.get(year):
            cal_eps[year] = 0
            continue
        total_eps = float(eps[year].replace(",", ""))
        cal_eps[year] = total_eps

    years = list(cal_eps.keys())
    eps_growth_rate = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        if cal_eps[previous] == 0:
            cal_eps[previous] = 1
        eps_ = round(
            ((cal_eps[current] - cal_eps[previous]) / cal_eps[previous]) * 100, 2
        )
        eps_growth_rate[current] = f"{eps_}%"

    # --------------------------------------------------
    cal_asset_growth_rate = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not total_assets:
            cal_asset_growth_rate[year] = 0
            continue

        if not total_assets.get(year):
            cal_asset_growth_rate[year] = 0
            continue
        total_asset_growth = float(total_assets[year].replace(",", ""))
        cal_asset_growth_rate[year] = total_asset_growth

    years = list(cal_asset_growth_rate.keys())
    asset_growth_rate = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]

        if cal_asset_growth_rate[previous] ==0:
            cal_asset_growth_rate[previous] = 1
        asset_growth_rate_ = round(
            (
                (cal_asset_growth_rate[current] - cal_asset_growth_rate[previous])
                / cal_asset_growth_rate[previous]
            )
            * 100,
            2,
        )
        asset_growth_rate[current] = f"{asset_growth_rate_}%"

    # --------------------------------------------------
    cal_net_profit = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not net_profit:
            cal_net_profit[year] = 0
            continue

        if not net_profit.get(year):
            cal_net_profit[year] = 0
            continue
        total_net_profit = 0.0 if net_profit is None else float(net_profit[year].replace(",", ""))
        cal_net_profit[year] = total_net_profit

    years = list(cal_net_profit.keys())
    net_profit_rate = {}

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]

        if cal_net_profit[previous] == 0:
            cal_net_profit[previous] = 1
        net_profit_rate_ = round(
            (
                (cal_net_profit[current] - cal_net_profit[previous])
                / cal_net_profit[previous]
            )
            * 100,
            2,
        )
        net_profit_rate[current] = f"{net_profit_rate_}%"

    all_growth_ratios.append(
        {
            "Revenue Growth Rate": revenue_growth_rate,
            "Operating Profit Growth Rate": operating_profit_growth_rate,
            "Earnings Per Share (EPS) Growth": eps_growth_rate,
            "Asset Growth Rate": cal_asset_growth_rate,
            "Net Income Growth Rate": net_profit_rate,
        }
    )

    return all_growth_ratios


def coverage_ratios(data, stock_name):
    stock_data = data[stock_name]
    profit_loss = stock_data["Screener"]["Profit & Loss"]
    cash_flows = stock_data["Screener"]["Cash Flows"]

    coverage_ratio = []
    years = ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]

    invest_coverage_ratio = {}
    debt_service_ratio = {}
    debt_service_coverage_ratio = {}

    for year in years:
        
        if not profit_loss[0].get(year):
                invest_coverage_ratio[year] = 0
                debt_service_ratio[year] = 0
                debt_service_coverage_ratio[year] = 0
                continue
        interest_expense = float(
            next(
                (
                    item[year].replace(",", "")
                    for item in profit_loss
                    if item.get("profit loss name") == "Interest"
                ),
                0.0,
            )
        )
        profit_before_tax = float(
            next(
                (
                    item[year].replace(",", "") if item.get(year) else 0.0
                    for item in profit_loss
                    if item.get("profit loss name") == "Profit before tax"
                ),
                0.0,
            )
        )
        invest_coverage_ratio[year] = (
            round(profit_before_tax / interest_expense, 2)
            if interest_expense != 0
            else 0.0
        )
        debt_service = float(
            next(
                (
                    item[year].replace(",", "") if item.get(year) else 0.0
                    for item in cash_flows
                    if item["cash flows name"] == "Interest paid fin"
                ),
                0.0,
            )
        )  # Assumption - Interest paid fin includes principal
        ebit = float(
            next(
                (
                    item[year].replace(",", "") if item.get(year) else 0.0
                    for item in profit_loss
                    if item.get("profit loss name") == "Operating Profit"
                ),
                0.0,
            )
        )
        debt_service_ratio[year] = (
            round(ebit / debt_service, 2) if debt_service != 0 else 0.0
        )
        ebit = float(
            next(
                (
                    item[year].replace(",", "") if item.get(year) else 0.0
                    for item in profit_loss 
                    if item.get("profit loss name") == "Operating Profit"
                ),
                0.0,
            )
        )
        total_debt_service = float(
            next(
                (
                    item[year].replace(",", "") if item.get(year) else 0.0
                    for item in cash_flows
                    if item["cash flows name"] == "Interest paid fin"
                ),
                0.0,
            )
        )
        debt_service_coverage_ratio[year] = (
            round(ebit / total_debt_service, 2)
            if total_debt_service != 0
            else 0.0
        )
    coverage_ratio.append(
        {
            "Debt Service Coverage Ratio (DSCR)": debt_service_coverage_ratio,
            "Debt Service Ratio": debt_service_ratio,
            "Interest Coverage Ratio": invest_coverage_ratio,
        }
    )

    return coverage_ratio


def financial_ratios(all_screener_data_dict, share_name):

    all_financial_ratios = []

    face_value = all_screener_data_dict[share_name]["Screener"]["share_info"][8][
        "Face Value"
    ]
    balance = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    profit = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]
    cash_flows = all_screener_data_dict[share_name]["Screener"]["Cash Flows"]

    net_profit = next(
        (item for item in profit if item.get("profit loss name") == "Net Profit -"), None
    )
    depreciation = next(
        item for item in profit if item.get("profit loss name") == "Depreciation"
    )
    exceptional = next(
        (item for item in profit if item.get("profit loss name") == "Exceptional items AT"), None
    )
    dividend = next(
        item for item in profit if item.get("profit loss name") == "Dividend Payout %"
    )
    minority_share = next(
        (item for item in profit if item.get("profit loss name") == "Minority share"), None
    )
    equity_capital = next(
        item for item in balance if item["balance sheet name"] == "Equity Capital"
    )
    reserves = next(
        item for item in balance if item["balance sheet name"] == "Reserves"
    )
    cash_from_operating = next(
        (item
        for item in cash_flows
        if item["cash flows name"] == "Cash from Operating Activity -"), None
    )
    fixed_purchased = next(
        item
        for item in cash_flows
        if item["cash flows name"] == "Fixed assets purchased"
    )
    fixed_sold = next(
        (item for item in cash_flows if item["cash flows name"] == "Fixed assets sold"), None
    )
    receivables = next((
        item for item in cash_flows if item["cash flows name"] == "Receivables"), None
    )
    inventory = next(
        (item for item in cash_flows if item["cash flows name"] == "Inventory"), None
    )
    payables = next(
        (item for item in cash_flows if item["cash flows name"] == "Payables"), None
    )
    loans_advances = next(
        (item for item in cash_flows if item["cash flows name"] == "Loans Advances"), None
    )
    other_wc_items = next(
        (item for item in cash_flows if item["cash flows name"] == "Other WC items"), None
    )

    adjusted_net_income = {}

    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not net_profit:
            adjusted_net_income[year] = 0.0
            continue
        if not net_profit.get(year):
            adjusted_net_income[year] = 0.0
            continue
        
        net_profit_ = 0.0 if net_profit is None else float(net_profit[year].replace(",", ""))
        exceptional_ = 0.0 if exceptional is None else float(exceptional[year].replace(",", ""))
        minority_share_ = 0.0 if minority_share is None else float(minority_share[year].replace(",", ""))

        adjusted_net_income_ratio = net_profit_ - exceptional_ - minority_share_
        adjusted_net_income[year] = adjusted_net_income_ratio

    shares_Outstanding = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not equity_capital:
            shares_Outstanding[year] = 0.0
            continue
        if not equity_capital.get(year):
            shares_Outstanding[year] = 0.0
            continue
        equity_capital_ = float(equity_capital[year].replace(",", ""))
        face_value_ = float(face_value.replace(",", "").replace("₹ ", ""))
        ratio = round(equity_capital_ / face_value_, 2)
        shares_Outstanding[year] = ratio

    adjusted_eps = {}

    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if shares_Outstanding[year] == 0:
            shares_Outstanding[year] = 1

        ratio = round(adjusted_net_income[year] / shares_Outstanding[year], 2)
        adjusted_eps[year] = ratio

    # ---------------------------------------------------
    shares_outstanding = {}
    for year in [
        "Mar 2019",
        "Mar 2020",
        "Mar 2021",
        "Mar 2022",
        "Mar 2023",
        "Mar 2024",
    ]:
        if not equity_capital:
            shares_Outstanding[year] = 0.0
            continue
        if not equity_capital.get(year):
            shares_Outstanding[year] = 0.0
            continue
        equity_capital_ = float(equity_capital[year].replace(",", ""))
        face_value_ = float(face_value.replace(",", "").replace("₹ ", ""))

        if face_value_ == 0:
            face_value_ = 1
        ratio = round(equity_capital_ / face_value_, 2)
        shares_outstanding[year] = ratio

    average_shares_outstanding = {}
    years = list(shares_outstanding.keys())

    for i in range(1, len(years)):
        previous = years[i - 1]
        current = years[i]
        _shares_outstanding = round(
            (shares_outstanding[current] + shares_outstanding[previous]) / 2, 2
        )
        average_shares_outstanding[current] = _shares_outstanding

    cash_eps = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not average_shares_outstanding:
            cash_eps[year] = 0.0
            continue
        if not average_shares_outstanding.get(year):
            cash_eps[year] = 0.0
            continue
        if average_shares_outstanding[year] == 0:
            average_shares_outstanding[year] = 1
        net_profit_ = float(net_profit[year].replace(",", ""))
        depreciation_ = float(depreciation[year].replace(",", ""))
        ratio = round((net_profit_ + depreciation_) / average_shares_outstanding[year])
        cash_eps[year] = ratio
    # -----------------------------------------------------------

    cal_total_equit = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not equity_capital.get(year):
            cal_total_equit[year] = 0.0
            continue
        if not equity_capital.get(year):
            cal_total_equit[year] = 0.0
            continue
        equity_capital_ = float(equity_capital[year].replace(",", ""))
        reserves_ = float(reserves[year].replace(",", ""))
        ratio = round(equity_capital_ + reserves_, 2)
        cal_total_equit[year] = ratio

    book_value_per_shar = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not cal_total_equit:
            book_value_per_shar[year] = 0.0
            continue
        if not cal_total_equit.get(year):
            book_value_per_shar[year] = 0.0
            continue
        if shares_Outstanding[year] == 0.0:
            shares_Outstanding[year] = 1.0
        ratio = round(cal_total_equit[year] / shares_Outstanding[year])
        book_value_per_shar[year] = float(ratio)

    # ---------------------------------------------------
    dps = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not dividend:
            dps[year] = 0.0
            continue
        if not dividend.get(year):
            dps[year] = 0.0
            continue
        dividend_pay = float(dividend[year].replace(",", "").replace("%", ""))
        if shares_Outstanding[year] == 0.0:
            shares_Outstanding[year] = 1.0
        ratio = round(dividend_pay / shares_Outstanding[year])
        dps[year] = float(ratio)

    # ---------------------------------------------------
    cash_from_operating_activities = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not cash_from_operating:
            cash_from_operating_activities[year] = 0.0
            continue
        if not cash_from_operating.get(year):
            cash_from_operating_activities[year] = 0.0
            continue
        cash_from_operating_activities_ = 0.0 if cash_from_operating is None else float(
            cash_from_operating[year].replace(",", "")
        )
        cash_from_operating_activities[year] = cash_from_operating_activities_
    # ------------------------------------------------
    net_capex = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not fixed_purchased:
            net_capex[year] = 0.0
            continue
        if not fixed_purchased.get(year):
            net_capex[year] = 0.0
            continue
        fixed_purchased_ = float(fixed_purchased[year].replace(",", ""))
        fixed_sold_ = 0.0 if fixed_sold is None else float(fixed_sold[year].replace(",", ""))
        ratio = round(fixed_purchased_ - fixed_sold_, 2)
        net_capex[year] = ratio

    # ---------------------------------------------------
    cwc = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not receivables:
            cwc[year] = 0 
            continue
        if not receivables.get(year):
            cwc[year] = 0 
            continue
        receivables_ = float(receivables[year].replace(",", ""))
        inventory_ = 0.0 if inventory is None else float(inventory[year].replace(",", ""))
        payables_ = 0.0 if payables is None else float(payables[year].replace(",", ""))
        loans_advances_ = 0.0 if loans_advances is None else float(loans_advances[year].replace(",", ""))
        other_wc_items_ = 0.0 if other_wc_items is None else float(other_wc_items[year].replace(",", ""))
        ratio = round(
            (receivables_ + inventory_ + loans_advances_)
            - (payables_ + other_wc_items_),
            2,
        )
        cwc[year] = ratio

    fcff = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not net_profit:
            fcff[year] = 0.0
            continue
        if not net_profit.get(year):
            fcff[year] = 0.0
            continue
        net_profit_ = float(net_profit[year].replace(",", ""))
        depreciation_ = float(depreciation[year].replace(",", ""))
        ratio = round(net_profit_ + depreciation_ - cwc[year] - net_capex[year], 2)
        fcff[year] = ratio

    # --------------------------------------------
    free_cash_flow_per_share = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not shares_Outstanding:
            free_cash_flow_per_share[year] = 0.0
            continue
        if not shares_Outstanding.get(year):
            free_cash_flow_per_share[year] = 0.0
            continue
        ratio = round(fcff[year] / shares_Outstanding[year], 2)
        free_cash_flow_per_share[year] = ratio

    all_financial_ratios.append(
        {
            "Adjusted Earnings Per Share (Adjusted EPS)": adjusted_eps,
            "Cash Earnings Per Share (Cash EPS)": cash_eps,
            "Book Value Per Share": book_value_per_shar,
            "Dividend Per Share (DPS)": dps,
            "Cash from Operating Activities": cash_from_operating_activities,
            "Capital Expenditures (CapEx)": net_capex,
            "Free Cash Flow to Firm (FCFF)": fcff,
            "Free Cash Flow Per Share": free_cash_flow_per_share,
        }
    )

    return all_financial_ratios


def profitability_ratios(all_screener_data_dict, share_name):

    all_profitability_ratios = []

    balance = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
    profit = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]
    cash_flows = all_screener_data_dict[share_name]["Screener"]["Cash Flows"]
    ratios = all_screener_data_dict[share_name]["Screener"]["Ratios"]

    sales = next((item for item in profit if item.get("profit loss name") == "Sales -"), None)
    material_cost = next(
        (item for item in profit if item.get("profit loss name") == "Material Cost % +"), None
    )
    manufacturing_cost = next(
        (item for item in profit if item.get("profit loss name") == "Manufacturing Cost %"), None
    )
    roce_data = next((item for item in ratios if item["ratios name"] == "ROCE %"), None)
    net_Profit = next(
        (item for item in profit if item.get("profit loss name") == "Net Profit -"), None
    )
    minority_share = next(
        (item for item in profit if item.get("profit loss name") == "Minority share"), None
    )
    equity_capital = next(
        item for item in balance if item["balance sheet name"] == "Equity Capital"
    )
    reserves = next(
        item for item in balance if item["balance sheet name"] == "Reserves"
    )
    assets = next(
        item for item in balance if item["balance sheet name"] == "Total Assets"
    )
    operating_profit = next(
        (item for item in profit if item.get("profit loss name") == "Operating Profit"), None
    )
    exceptional_items = next(
        (item for item in profit if item.get("profit loss name") == "Exceptional items"), None
    )
    other_income_normal = next(
        (item for item in profit if item.get("profit loss name") == "Other income normal"), None
    )
    tax = next(item for item in profit if item.get("profit loss name") == "Tax %")
    profit_befor_tax = next(
        item for item in profit if item.get("profit loss name") == "Profit before tax"
    )
    borrowings = next(
        item for item in balance if item["balance sheet name"] == "Borrowings -"
    )
    cash_flow_operations = next(
        (item
        for item in cash_flows
        if item["cash flows name"] == "Cash from Operating Activity -"), None
    )
    fixed_purchased = next(
        item
        for item in cash_flows
        if item["cash flows name"] == "Fixed assets purchased"
    )
    fixed_sold = next(
        (item for item in cash_flows if item["cash flows name"] == "Fixed assets sold"), None
    )

    cogs = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            cogs[year] = 0
            continue
        if not sales.get(year):
            cogs[year] = 0 
            continue
        net_sale = float(sales[year].replace(",", ""))
        material_cost_ = 0.0 if material_cost is None else float(material_cost[year].replace(",", "").replace("%", "")) if material_cost[year] else 0.0
        manufacturing_cost_ = 0.0 if manufacturing_cost is None else float(
            manufacturing_cost[year].replace(",", "").replace("%", "")
        ) if manufacturing_cost[year] else 0.0
        if manufacturing_cost_ == 0.0:
            manufacturing_cost_ = 1.0
        ratio = round(net_sale * (material_cost_ + manufacturing_cost_) / 100, 2)
        cogs[year] = ratio

    gross_profit = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            gross_profit[year] = 0
            continue
        if not sales.get(year):
            gross_profit[year] = 0 
            continue
        net_sale = float(sales[year].replace(",", ""))
        ratio = round(net_sale - cogs[year], 2)
        gross_profit[year] = ratio

    gmp = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            gmp[year] = 0
            continue
        if not sales.get(year):
            gmp[year] = 0 
            continue
        net_sale = float(sales[year].replace(",", ""))
        if net_sale == 0:
            net_sale = 1
        ratio = round((gross_profit[year] / net_sale) * 100, 2)
        gmp[year] = f"{ratio} %"
    # -----------------------------------------------------
    roce = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not roce_data:
            roce[year] = 0.0
            continue

        if not roce_data.get(year):
            roce[year] = 0.0
            continue
        ratio = float(roce_data[year].replace(",", "").replace("%", ""))
        roce[year] = f"{ratio} %"

    # ----------------------------------------------------
    net_income = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not net_Profit:
            net_income[year] = 0.0
            continue
        if not net_Profit.get(year):
            net_income[year] = 0.0
            continue
        net_income_ = 0.0 if net_Profit is None else float(net_Profit[year].replace(",", ""))
        minority_share_ = 0.0 if minority_share is None else float(minority_share[year].replace(",", ""))
        ratio = round(net_income_ - minority_share_, 2)
        net_income[year] = ratio

    shareholder_equity = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not equity_capital:
            shareholder_equity[year] = 0.0
            continue
        if not equity_capital.get(year):
            shareholder_equity[year] = 0.0
            continue
        equity_capital_ = float(equity_capital[year].replace(",", ""))
        reserves_ = float(reserves[year].replace(",", ""))
        ratio = round(equity_capital_ + reserves_, 2)
        shareholder_equity[year] = ratio

    roe = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if shareholder_equity[year] == 0.0:
            shareholder_equity[year] = 1.0

        ratio = round((net_income[year] / shareholder_equity[year]) * 100, 2)
        roe[year] = f"{ratio} %"

    # ------------------------------------------------------
    roa = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not net_Profit:
            roa[year] = 0.0
            continue
        if not net_Profit.get(year):
            roa[year] = 0.0
            continue
        if not assets.get(year):
            roa[year] = 0.0
            continue
        net_income_ = float(net_Profit[year].replace(",", ""))
        total_assets = float(assets[year].replace(",", ""))
        if total_assets == 0.0:
            total_assets = 1.0
        ratio = round((net_income_ / total_assets) * 100, 2)
        roa[year] = ratio

    # ----------------------------------------------
    ebit = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not operating_profit:
            ebit[year] = 0.0
            continue
            
        if not operating_profit.get(year):
            ebit[year] = 0.0
            continue
        operating_profit_ = 0.0 if operating_profit is None else float(operating_profit[year].replace(",", ""))
        exceptional_items_ = 0.0 if exceptional_items is None else float(exceptional_items[year].replace(",", ""))
        other_income_normal_ =  0.0 if other_income_normal is None else float(other_income_normal[year].replace(",", ""))

        ebit_data = operating_profit_ + other_income_normal_ - exceptional_items_
        ebit[year] = ebit_data

    tax_rate = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not tax:
            tax_rate[year] = 0.0
            continue
        if not tax.get(year):
            tax_rate[year] = 0.0
            continue
        tax_ = float(tax[year].replace(",", "").replace("%", ""))
        profit_befor_tax_ = float(profit_befor_tax[year].replace(",", ""))
        if profit_befor_tax_ == 0.0:
            profit_befor_tax_ = 1.0
        ratio = round(tax_ / profit_befor_tax_, 2)
        tax_rate[year] = ratio

    nopat = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        ratio = round(ebit[year] * (1 - tax_rate[year]), 2)
        nopat[year] = ratio

    debt_ratio = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not borrowings:
            debt_ratio[year] = 0.0
            continue
        if not borrowings.get(year):
            debt_ratio[year] = 0.0
            continue
        borrowings_ = float(borrowings[year].replace(",", ""))
        total_assets = float(assets[year].replace(",", ""))
        if total_assets == 0.0:
            total_assets = 1.0
        ratio = round(borrowings_ / total_assets, 2)
        debt_ratio[year] = ratio

    invested_capital = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        ratio = round(debt_ratio[year] + shareholder_equity[year], 2)
        invested_capital[year] = ratio

    roic = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if invested_capital[year] == 0.0:
            invested_capital[year] = 1.0
        ratio = round((nopat[year] / invested_capital[year]) * 100, 2)
        roic[year] = f"{ratio} %"
    # -----------------------------------------------------
    operating_margin = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not operating_profit:
            operating_margin[year] = 0.0
            continue
        if not operating_profit.get(year):
            operating_margin[year] = 0.0
            continue
        operating_profit_ = float(operating_profit[year].replace(",", ""))
        net_sale = float(sales[year].replace(",", ""))
        if net_sale == 0.0:
            net_sale = 1.0
        ratio = round((operating_profit_ / net_sale * 100), 2)
        operating_margin[year] = f"{ratio} %"
    # --------------------------------------------------------
    net_margin = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not sales:
            net_margin[year] = 0
            continue
        if not sales.get(year):
            net_margin[year] = 0.0
            continue
        net_sale = float(sales[year].replace(",", ""))
        if net_sale == 0.0:
            net_sale = 1.0
        ratio = round((net_income[year] / net_sale) * 100, 2)
        net_margin[year] = f"{ratio} %"

    # --------------------------------------------
    net_capex = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not fixed_purchased:
            net_capex[year] = 0.0
            continue
        if not fixed_purchased.get(year):
            net_capex[year] = 0.0
            continue
        fixed_purchased_ = float(fixed_purchased[year].replace(",", ""))
        fixed_sold_ = 0.0 if fixed_sold is None else float(fixed_sold[year].replace(",", ""))
        ratio = round(fixed_purchased_ - fixed_sold_, 2)
        net_capex[year] = ratio

    cash_profit_margin = {}
    for year in ["Mar 2020", "Mar 2021", "Mar 2022", "Mar 2023", "Mar 2024"]:
        if not cash_flow_operations:
            cash_profit_margin[year] = 0.0
            continue
        if not cash_flow_operations.get(year):
            cash_profit_margin[year] = 0.0
            continue

        if not sales:
            cash_profit_margin[year] = 0.0
            continue
        if not sales.get(year):
            cash_profit_margin[year] = 0.0
            continue
        cash_flow_operations_ = 0.0 if cash_flow_operations is None else float(cash_flow_operations[year].replace(",", ""))
        net_sale = 0.0 if sales is None else float(sales[year].replace(",", ""))
        if net_sale == 0.0:
            net_sale = 1.0
        ratio = round(((cash_flow_operations_ - net_capex[year]) / net_sale) * 100, 2)
        cash_profit_margin[year] = f"{ratio} %"
    # ------------------------------------------------------

    all_profitability_ratios.append(
        {
            "Gross Profit Margin": gmp,
            "Return on Capital Employed (ROCE)": roce,
            "Return on Equity (ROE)": roe,
            "Return on Assets (ROA)": roa,
            "Return on Invested Capital (ROIC)": roic,
            "Operating Margin": operating_margin,
            "Net Margin": net_margin,
            "Cash Profit Margin": cash_profit_margin,
        }
    )

    return all_profitability_ratios


AVAILABLE_YEARS = [
    "Mar 2019",
    "Mar 2020",
    "Mar 2021",
    "Mar 2022",
    "Mar 2023",
    "Mar 2024",
]


def valuation_ratios(data, stock_name):
    valuation_ratios_list = []
    stock_data = data[stock_name]
    share_info = stock_data["Screener"]["share_info"]
    market_cap = float(
        share_info[0]["Market Cap"]
        .replace("₹ ", "")
        .replace(" Cr.", "")
        .replace(",", "")
    )
    face_value = float(share_info[8]["Face Value"].replace("₹ ", "").replace(",", ""))
    balance_sheet = stock_data["Screener"]["Balance Sheet"]
    profit_loss = stock_data["Screener"]["Profit & Loss"]
    share_price = float(
        stock_data["Screener"]["share_price"].replace("₹ ", "").replace(",", "")
    )
    operating_profit = next(
        (item for item in profit_loss if item.get("profit loss name") == "Operating Profit"), None
    )
    depriciation = next(
        (item
        for item in profit_loss
        if item.get("profit loss name") == "Other income normal"), None
    )
    book_value = next(
    (
        float(item["Book Value"].replace("₹ ", "").replace(",", "").replace(" Cr.", "").replace("₹", "")) 
        if item["Book Value"] and item["Book Value"].strip() != "" and item["Book Value"].replace(",", "").replace("₹", "").replace(" Cr.", "").replace("₹", "").isnumeric() 
        else 0.0
        for item in share_info
        if "Book Value" in item
    ),
    0.0,
)

    eps_val = {}
    shares_Outstanding = {}
    pe_ratio = {}
    ev_by_ebitda = {}
    pb_ratio = {}
    dividend_yield = {}
    peg_ratio = {}
    price_to_sales = {}
    for year in AVAILABLE_YEARS:

        equity_capital = next(
            item
            for item in balance_sheet
            if item["balance sheet name"] == "Equity Capital"
        )
        if not equity_capital.get(year):
            shares_Outstanding[year] = 0
            eps_val[year] = 0
            pe_ratio[year] = 0
            ev_by_ebitda[year] = 0
            pb_ratio[year] = 0
            peg_ratio[year] = 0
            dividend_yield[year] = 0
            continue

        equity_capital_ = float(equity_capital[year].replace(",", ""))
        face_value_ = face_value
        shares_Outstanding[year] = round(equity_capital_ / face_value_, 2)

        eps_val[year] = next(
            (
                float(item[year].replace(",", "") if item.get(year) else 0.0)
                for item in profit_loss
                if item.get("profit loss name") == "EPS in Rs"
            ),
            0.0,
        )

        pe_ratio[year] = (
            max(0, round(share_price / eps_val[year], 2))
            if eps_val[year] and eps_val[year] != 0
            else 0.0
        )

        borrowing = next(
            float(item[year].replace(",", ""))
            for item in balance_sheet
            if item["balance sheet name"] == "Borrowings -"
        )
        cash_equivalents = next(
            float(item[year].replace(",", ""))
            for item in balance_sheet
            if item["balance sheet name"] == "Cash Equivalents"
        )
        ev = market_cap + borrowing - cash_equivalents  #
        if not operating_profit:
            ebitda = 0.0
            continue
        if not operating_profit.get(year):
            ebitda = 0.0
        else:
            ebitda = 0.0 if operating_profit is None else float(operating_profit[year].replace(",", "")) + 0.0 if depriciation is None else float(
                depriciation[year].replace(",", "")
            ) 

        if ebitda == 0.0:
            ebitda = 1.0

        ev_by_ebitda[year] = round(ev / ebitda, 2)

        pb_ratio[year] = round(share_price / book_value, 2) if book_value else 0.0

        dividend_yield_val = next(
            (
                item.get(year)
                for item in profit_loss
                if item.get("profit loss name") == "Dividend Payout %"
            ),
            0.0,
        )
        dividend_yield[year] = (
            round(float(dividend_yield_val.replace("%", "").replace(",", "")) / 100, 2)
            if dividend_yield_val
            else 0.0
        )

        # PEG Ratio (requires EPS growth rate -  approximating with a simple year-over-year calculation, can be improved)
        if (
            year != "Mar 2019"
            and eps_val
            and eps_val[AVAILABLE_YEARS[AVAILABLE_YEARS.index(year) - 1]]
        ):
            eps_growth = (
                (
                    eps_val[AVAILABLE_YEARS[AVAILABLE_YEARS.index(year)]]
                    - eps_val[AVAILABLE_YEARS[AVAILABLE_YEARS.index(year) - 1]]
                )
                / eps_val[AVAILABLE_YEARS[AVAILABLE_YEARS.index(year) - 1]]
            ) * 100
            peg_ratio[year] = (
                round(pe_ratio[year] / eps_growth, 2) if eps_growth != 0 else 0.0
            )
        else:
            peg_ratio[year] = 0.0

        total_sales = next(
            (
                float(item[year].replace(",", "") if item.get(year) else 0.0)
                for item in profit_loss
                if item.get("profit loss name") == "Sales -"
            ),
            0.0,
        )
        if total_sales == 0.0:
            total_sales = 1.0
        price_to_sales[year] = round(market_cap / total_sales, 2)

    valuation_ratios_list.append(
        {
            "P/E Ratio": pe_ratio,
            "P/B Ratio": pb_ratio,
            "Dividend Yield Ratio": dividend_yield,
            "PEG Ratio": peg_ratio,
            "Price to Sale Ratio": price_to_sales,
            "EV/EBITDA": ev_by_ebitda,
        }
    )

    return valuation_ratios_list
