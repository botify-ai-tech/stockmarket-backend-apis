def gemini_prompt(news_data):
    return f"""As a proficient News Analyst with a specialized expertise in the intricate dynamics of the Stock Market, your primary task is a complex exercise of classification. From the list provided below, you need to discern and assign the most fitting class or classes to a given news article. The nature of this task acknowledges the possibility of an article fitting into multiple classes due to the intertwining nature of news.\n\nThe list of News Classes includes:\n\nbreaking_news, earnings_reports, analyst_reports, sector_analysis, stock_recommendations, ipo_news, mergers_acquisitions, economic_indicators, technical_analysis, fundamental_analysis, insider_trading_news, interest_rates_monetary_policy, market_forecasts_predictions, controversy, and Other.\n\nConsider intricacies such as the central theme of the article, the different stakeholders it impacts, and its potential repercussions on the market. Reflect on the intended tone or style of the article, discerning whether it adopts an informative, analytical, or speculative approach. Examine any underlying assumptions or nuances the article may have made about the state of the market or specific stocks.\n\nBased on the News Type, your task is to conduct a comprehensive analysis of a specific news article with a potential impact on the financial markets. Your analysis should examine the content, context, and implications of the news item, and provide a detailed perspective on its probable effects.\n\nFirstly, identify the Sector or Sectors (from bellowed mentioned List of sectors ONLY ) that would be most affected by the news.\n\nList of sectors: \n\nAbrasives \n\nAerospace & Defence \n\nAgro Chemicals \n\nAir Conditioners \n\nAir Transport Service \n\nAlcoholic Beverages \n\nAuto Ancillaries \n\nAutomobile \n\nBPO & ITeS \n\nBanks \n\nBearings \n\nCables \n\nCapital Goods - Electrical Equipment \n\nCapital Goods-Non Electrical Equipment \n\nCarbon Black \n\nCastings, Forgings & Fastners \n\nCement \n\nCement - Products \n\nCeramic Products \n\nChemicals \n\nCompressor \n\nComputer Education \n\nConstruction \n\nConsumer Durables \n\nCredit Rating Agencies \n\nCrude Oil & Natural Gas \n\nDiamond, Gems and Jewellery \n\nDiversified \n\nDry cells \n\nDyes & Pigments \n\nE-Commerce/App based Aggregator \n\nEdible Oil \n\nEducation \n\nElectronics \n\nEngineering \n\nEntertainment \n\nFMCG \n\nFerro Alloys \n\nFertilizers \n\nFinance \n\nFinancial Services \n\nFootwear \n\nGas Distribution \n\nGlass & Glass Products \n\nHealthcare \n\nHotels & Restaurants \n\nHousehold Products \n\nIT - Hardware \n\nIT - Software \n\nInfrastructure Developers & Operators \n\nInfrastructure Investment Trusts \n\nInsurance \n\nLeather \n\nLogistics \n\nMarine Port & Services \n\nMedia - Print/Television/Radio \n\nMining & Mineral products \n\nMiscellaneous \n\nNBFC \n\nNon Ferrous Metals \n\nOil Drill/Allied \n\nPSU Stocks \n\nPackaging \n\nPaints/Varnish \n\nPaper \n\nPetrochemicals \n\nPharmaceuticals \n\nPlantation & Plantation Products \n\nPlastic products \n\nPlywood Boards/Laminates \n\nPower Generation & Distribution \n\nPower Infrastructure \n\nPrinting & Stationery \n\nQuick Service Restaurant \n\nRailways \n\nReady made Garments/ Apparels \n\nReal Estate Investment Trusts \n\nRealty \n\nRefineries \n\nRefractories \n\nRetail \n\nShip Building \n\nShipping \n\nSteel \n\nStock/ Commodity Brokers \n\nSugar \n\nTea Coffee \n\nTelecom-Handsets/Mobile \n\nTelecom Equipment & Infra Services \n\nTelecom-Service \n\nTextiles \n\nTobacco Products \n\nTrading \n\nTravel Services \n\nTyres\n\nWood & Wood Products\n\nThis could range from the entire stock market, a specific sector within the market, or an individual stock. If the impact is sector-specific, please specify the name of the sector (e.g., Tech, Healthcare, Energy, etc.). If an individual stock is expected to be impacted, please provide the name of the stock.\n\nSecondly, provide a detailed explanation of how this news could potentially impact the identified Sector(s). Consider factors such as the scale and nature of the impact (positive/negative), the time frame of the impact (short-term/long-term), and any other relevant dynamics such as market volatility, investor sentiment, or macroeconomic indicators.\n\nThirdly, predict what the ultimate impact of the news will be. This should be a nuanced interpretation, blending quantitative and qualitative analysis, and considering multiple possible scenarios. For instance, will this news trigger a rally or a sell-off? Will it lead to increased market volatility or stability? Will it alter the competitive landscape within a sector or change the fortunes of a specific stock?\n\nCategory of News: Classify the news based on its content into one or more categories (e.g., Market Movement, Macroeconomic Factors, Mergers and Acquisitions, Regulatory/Policy Updates, Financial Performance, Product Launches). \nCompany Name: Identify the primary company or organization that is the central focus of the news. \nCountry Name: Also identify which country the news is related to. \n\nStrict Notes:\n1. Do not hallucinate and strictly follow the below given outpuit format.\n2. Do not consider comments, as they are only for reference. \n\nOutput Format:\n {{"article": {{"title": "","published_date": "","summary": ""  }},  "classification": {{"primary_class": "breaking_news" }},  "impact_analysis": {{"type_of_impact": "individual_stock","majority_market_impact": {{"is_impacted": false, "impact_description": "write description if the majority of the market is impacted, focusing on overall market trends important to investors"}},"sectors_impacted": {{"is_impacted": false, "sector_list": ["Write sector names here, like Tech, Healthcare, which would concern investors"]}},"stocks_impacted": {{"is_impacted": true, "stock_list": ["Provide the corresponding stock ticker symbol for the company, ensuring it is listed on any major stock exchange worldwide, including but not limited to the New York Stock Exchange (NYSE), NASDAQ, London Stock Exchange (LSE), National Stock Exchange (NSE), or Bombay Stock Exchange (BSE)."]}}}}, "category_impacted": {{"is_impacted": false, "category_list": ["Write category names here, like Market Movement, Regulatory/Policy Updates, which would concern investors"]}},  "Country": {{"is_country": false, "country_name": "Country Name" }},  "company_name": {{"is_company_name": false,  "company_name": "India"}}, "impact_explanation": {{"scale_of_impact": "", "timeframe_of_impact": "", "nature_of_impact": {{"investor_sentiment": "",  "market_volatility": ""}}, "Impact_detailed_explanation": ["Write a detailed and numbered explanation of the impact here, analyzing the consequences for investors, such as how the news will influence stock prices, investor confidence, and overall market sentiment."]  }}}} \nImportant Notes for Output : \n1. "primary_class" -  classification should describe the primary nature of the article, relevant from an investor's perspective   \n2. "is_country" - set this to true if country name  is avilable.\n3."is_impacted" - Set this to true if specific stocks/sectors/category are impacted.\n4. "type_of_impact" - Possible values: "majority_market", "sector", "individual_stock", analyzed from the investor's point of view.\n5."is_company_name" - Set this to true if specific company are impacted.\n6. "scale_of_impact" -  Possible values: "positive", "negative", "neutral" — How the news will affect the stock price from an investor's point of view.\n7. "timeframe_of_impact" -  Possible values: "short_term", "long_term" — Investors will want to know how long the effects are likely to last.\n8. "investor_sentiment" - Possible values: "bullish", "bearish", "neutral" — Define how investors are likely to react to the news.\n9. "market_volatility" - Describe the potential volatility level, which is crucial for investors planning trades or holding positions. ***\n\nStrict Notes:\nData Quality: Ensure that the JSON data is clean, accurate, and relevant to the news analysis.\n2. Ensure that you handle any error or any invalid format present in the output and the JSON. This includes handling any string that remains unclosed or missing commas or any other syntax error.*** \n **Strictly avoid adding any comments in the JSON output you create, as these comments are irrelevant.**\n\nNEWS Article: {news_data}"""


def ratio_prompt(ratio_data):
    return f"""Assume the role of a highly experienced Indian Stock analyst and Fundamental analyst of a leading financial institution. I will present to you various financial ratios of individual stocks in a meticulously curated JSON format. Drawing from your extensive expertise in the financial domain, you are expected to conduct a comprehensive analysis of these ratios and provide a detailed evaluation of the stock. These evaluations should clearly outline whether the given values indicate a favourable or an unfavourable situation for a potential investor. In addition to this, you are tasked with summarising the overall picture that the collection of these ratios paints about the Fundamental and Financial health of the stock. Your summary should be a succinct yet insightful interpretation of the varied financial indicators. This should include an enumeration of the Pros and Cons, if any, that are discernible from the given ratios. Further, based on the Fundamental and Financial health analysis and considering the ratios, you are required to provide an investment recommendation on the stock. The recommendation should categorize the stock as a 'Strong Buy', 'Buy', 'Hold', 'Sell', or 'Strong Sell'. Your recommendation should not only reflect your analysis of the given ratios but should also consider the general market trends, company-specific news, and other relevant financial data. Your analysis should be presented in a professional style, mirroring the succinct and insightful reports produced by leading financial analysts. It should demonstrate a clear understanding of the multifaceted implications of financial ratios and how they interact with broader market trends. You are encouraged to reference reputable financial sources to bolster your analysis and recommendations.\n Do not add any further explanations on anything, your task is to simply provide a JSON output and nothing else.\n Output Format: \n{{\n   "stock_analysis":{{\n"stock_name":"name of Company symbol",\n"evaluation":{{\n   "favourable_indicators":[\n {{\n    "ratio":"name of the ratio",\n    "indication":[\n "1. What ratio Indicates given a values ",\n "2. What ratio Indicates given a values ",\n "3. What ratio Indicates given a values",\n .\n .\n .\n    ]\n }},\n .\n .\n .\n   ],\n   "unfavourable_indicators":[\n {{\n    "ratio":" name of the ratio ",\n    "indication":[\n "1. What ratio Indicates given a values ",\n "2. What ratio Indicates given a values ",\n "3. What ratio Indicates given a values ",\n .\n .\n    ]\n }},\n .\n .\n .\n   ]\n}},\n"overall_picture":{{\n   "summary":"Concise summary of financial health and performance point wise",\n   "pros":[\n "List of pros based on ratios"\n   ],\n   "cons":[\n "List of cons based on ratios"\n   ]\n}},\n"investment_recommendation":{{\n   "recommendation":"Strong Buy / Buy / Hold / Sell / Strong Sell",\n   "rationale":"Justification for the recommendation in very Easy Language and point wise, including market trends and company-specific news"\n}}\n   }}\n}}. ***\n\nStrict Notes:\nData Quality: Ensure that the JSON data is clean, accurate, and relevant to the news analysis.\nStrictly follow the above given Output format and do not deviate from it.***\n Input Json: {ratio_data}"""
