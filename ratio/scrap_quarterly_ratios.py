import logging
from datetime import datetime

from ratio.scraper_ratio import ration
from ratio.ratio_analys import ratio_analys
from ratio.assessment_green_flag import assessment_green_flag
from ratio.assessment_red_flag import assessment_red_flag

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

def scrape_quarterly(start,end):
      
    try : 
        unscraped_companies = []
        with open("ratio\\nsc.txt", "r", encoding="utf-8") as f:
            shares = f.readlines()

        for share in shares[start:end]:
            share = share.strip("\n")

            for func in [ration, ratio_analys, assessment_green_flag, assessment_red_flag]:
                response = func(share)
                if response is not None:
                    if response.get("unscraped_companies"):
                        unscraped_companies.append(share)
                        logging.warning(f"Company {share} could not be scraped.")
                        break  

                if "error" in response:
                    unscraped_companies.append(share)
                    logging.error(f"Error for {share}: {response.get('details', 'Unknown Error')}")
                    break
        
        last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "start": start,
            "end": end,
            "last_update_time": last_update_time,
            "unscraped_companies": unscraped_companies
        }

    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred", "details": str(e)}
    
