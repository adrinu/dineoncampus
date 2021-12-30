from playwright.sync_api import sync_playwright
from database_ops import add_school
import logging

logging.basicConfig(filename="scrape.log", format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLoggerClass()


def convert_to_float(s) -> float:
    """
    Converts a string to float

    Args:
        s (str): a string containg numbers and periods 

    Returns:
        float: 
    """
    allowed_chars = "0123456789."
    num = s.strip()
    try:
        return float(num)
    except ValueError:
        return float("".join([i for i in num if i in allowed_chars]))
        

def extract_nutrient_info(s) -> dict:
    """
    Extract nutritional facts

    Args:
        s (str): nutrientional facts

    Returns:
        dict: macronutrient and its value 
    """
    result = {}
    
    # Seperate each nutritent fact
    facts = s.split("\n")
    for fact in facts:
        temp = fact.split(":")
        # Check if we can perform the following action
        try:
            # input could be "100 g" or "g"
            
            result[temp[0].strip()] = convert_to_float(temp[1])
        except IndexError:
            continue
    return result
 
def scrape_school_menu(schoolname, school_endurl) -> None:
    """
    Scrapes school's menu off from dineoncampus.com and adds it to database

    Args:
        school_endurl (str): The rest of the url after .com/
    """

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        page = browser.new_page()
        page.goto("https://dineoncampus.com/{}".format(school_endurl))
        page.wait_for_timeout(5000)
        
        # Click on dropdown
        page.click('css=[id="dropdown-grouped__BV_toggle_"]')
        
        places_to_eat = {}
        dropdown_items = page.query_selector_all('css=[role="presentation"] >> button')
        
        # Click on Dropdown
        page.click('css=[id="dropdown-grouped__BV_toggle_"]')
        for item in dropdown_items:
            page.click('css=[id="dropdown-grouped__BV_toggle_"]')
            # Click on item to load menu
            item.click()
            
            # Wait for the page to load
            page.wait_for_timeout(5000)
            
            tabs = page.query_selector_all('css=[role="tab"]')
            if not tabs:
                logger.warning("Menu not loaded for {}".format(item.inner_text().strip()))
            else:
                logger.info("Menu loaded {}".format(item.inner_text()))
                for tab in tabs:
                    logger.info("Getting meals for the tab '{}'".format(tab.inner_text().strip()))
                    store_tab = {}
                    # Wait for the page to load
                    page.wait_for_timeout(5000)
                    
                    # Grab Nutritional info, portions, calories 
                    menu_item = page.query_selector_all('css=[class="btn mt-3 btn-nutrition btn-info-outline btn-sm"]')
                    portions = page.query_selector_all('css=[data-label="Portion"]')
                    calories = page.query_selector_all('css=[data-label="Calories"]')
        
                    store_nutrients = {}
                    for i in range(len(menu_item)):
                        try:
                            menu_item[i].click()
                            # Wait to load Nutritional facts
                            page.wait_for_timeout(5000)
                            
                            # Menu item name
                            menu_item_name = page.query_selector('css=[class="modal-header"]')
                            nutruitional_facts = page.query_selector('css=[class="modal-body"]')
                            
                            store_nutrients[menu_item_name.inner_text()] = extract_nutrient_info(nutruitional_facts.inner_text())
                            store_tab[tab.inner_text()] = store_nutrients
                            
                            # Close Nutritional popup
                            page.click('css=[aria-label="Close"]')
                            page.wait_for_timeout(1000)

                            # Store Calories and Portion size
                            store_nutrients["Calories"] = calories[i]
                            store_nutrients["Serving Size"] = portions[i]
                            
                        except Exception as e:
                            logger.error("Exception occued", exc_info=True)
            places_to_eat[item.inner_text()] = store_tab
        
        # Log information about adding data to database
        status_code = add_school(schoolname, {schoolname: places_to_eat})
        if status_code == 200:
            logger.info("Successfully added {} to the database".format(schoolname))
        else:
            logger.error("Recieved a HTTP Status code of {}", status_code)
        
        browser.close()