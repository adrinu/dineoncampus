from playwright.sync_api import sync_playwright
import database_ops as dbo
import logging

logging.basicConfig(filename="scrape.log", format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

def convert_to_int(s) -> int:
    """
    Converts a string to int

    Args:
        s (str): a string containg numbers and periods 

    Returns:
        int: 
    """
    allowed_chars = "0123456789."
    num = s.strip()
    try:
        temp = int(num)
        return temp
    except:
        res = "".join([i for i in num if i in allowed_chars])
        return int(float(res)) if res != "" else 0
        
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
            result[temp[0].strip()] = convert_to_int(temp[1])
        except IndexError:
            continue
    return result
 
def scrape_school_menu(schoolname, school_endurl) -> None:
    """
    Scrapes school's menu off from dineoncampus.com and adds it to database

    Args:
        school_endurl (str): The rest of the url after .com/
    """
    logging.info("Scraping {}".format(schoolname))
    logging.info("-"*25)
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
                logging.warning(msg="Menu not loaded for {}.".format(item.inner_text().strip()))
            else:  
                logging.info(msg="Menu loaded {}".format(item.inner_text()))
                for tab in tabs:
                    logging.info(msg="Getting meals for the tab '{}'".format(tab.inner_text().strip()))
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
                            menu_item_name_element = page.query_selector('css=[class="modal-header"]')
                            menu_item_name = menu_item_name_element.inner_text().replace("\n", "").replace("\u00d7", "").replace("\u00ae", "")
                            
                            nutruitional_facts_element = page.query_selector('css=[class="modal-body"]')
                            nutruitional_facts = nutruitional_facts_element.inner_text()
                            
                            store_nutrients[menu_item_name] = extract_nutrient_info(nutruitional_facts)
                            store_tab[tab.inner_text().strip()] = store_nutrients
                            
                            # Close Nutritional popup
                            page.click('css=[aria-label="Close"]')
                            page.wait_for_timeout(1000)

                            # Store Calories and Portion size
                            # store_nutrients["Calories"]= calories[i].inner_text()
                            # store_nutrients["Serving Size"] = portions[i].inner_text()
                            store_nutrients[menu_item_name]["Calories"] = calories[i].inner_text()
                            store_nutrients[menu_item_name]["Portion"] = portions[i].inner_text()
                
                        except Exception as e:
                            logging.error("Exception occured", exc_info=True)
                places_to_eat[item.inner_text()] = store_tab
        
        # Log information about adding data to database
        data = {}
        data[schoolname] = places_to_eat
        status_code = dbo.add_menu(schoolname, data)

        if status_code == 200:
            logging.info(msg="Successfully added {} to the database".format(schoolname))
        else:
            logging.error(msg="Recieved a HTTP Status code of {}".format(status_code))
    
        logging.info(msg="Completed Scraping script!")
        logging.info("-"*25)
        browser.close()