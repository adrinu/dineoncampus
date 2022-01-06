from scrape import scrape_school_menu
import argparse
import json

f = open("dineoncampus_urls.json", "r")
schools = json.load(f)
f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("--s", type=str, help="Scapes given school menu")
    parser.add_argument("--all", action='store_true' ,help="Scrapes all menus in dineoncampus_urls.json")
    
    args = parser.parse_args()
    
    for school, url in schools.items():
        print("Scraping {}".format(school))
        scrape_school_menu(school, url)
        print("Done!")
    
    print("Done with scraping all schools!")
    
    #scrape_school_menu(args.s, schools[args.s])
    