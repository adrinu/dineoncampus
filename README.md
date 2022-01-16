# mealbuddyapp-scrapetool

Scapes a school's menu on dineoncampus.com and updates dynamoDB database. This script runs on EC2 instance, a CRON Job will execute once everyday to update database with new menus for the day

## API Reference

The mobile application makes a GET call to the API, returns a JSON response containing a map of foods and their nutrition facts

#### Get a school's menu

```http
  GET /default/scrape-dineoncampus
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `schoolname` | `string` | Name of the school to get menu from |

Pick a schoolname from [dineoncampus_urls json file](https://github.com/adrinu/mealbuddyapp-backend/blob/master/dineoncampus_urls.json) and try it! Or just [click me](https://0qszzssmbk.execute-api.us-east-2.amazonaws.com/default/scrape-dineoncampus?schoolname=NYU) 

## Roadmap

- [Add more schools for the script to scrape](https://github.com/adrinu/mealbuddyapp-backend/blob/master/dineoncampus_urls.json)
- Add a API call to the rerun scrape script to update a school menu if there were any changes made to the menu.
