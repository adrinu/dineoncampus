import boto3
import json

f = open("secrets.json")
secrets = json.load(f)
f.close()

session = boto3.Session(
        aws_access_key_id=secrets["AWS_access_key_id"],
        aws_secret_access_key=secrets["AWS_secret_access_key"]
    )
db = session.resource(service_name="dynamodb", region_name='us-east-2')

def get_menu(schoolname, tablename=secrets["tablename"]):
    """
    Returns a dict of school menu

    Args:
        schoolname (str): School name
        tablename (str, optional): Name of table in db. Defaults to secrets["tablename"].

    Returns:
        dict: Menu of school 
    """
    table = db.Table(tablename)
    response = table.get_item(
        TableName="school_meals",
        Key={
          'schoolname': schoolname
       }
    ) 
    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        try:
            return response["Item"]
        except KeyError:
            return {}
    return response["ResponseMetadata"]["HTTPStatusCode"]

def add_menu(schoolname, data, tablename=secrets["tablename"]) -> int:
    """
    Adds meals to a school's database  

    Args:
        schoolname (str): School name
        new_data (dict): Parsed information about meals
        tablename (str, optional): Table name stored in dynamoDB. Defaults to secrets["tablename"].

    Returns:
        [int]: HTTP Status code
    """
    table = db.Table(tablename)
    response = table.put_item(
        Item = {
            "schoolname": schoolname,
            "meals": data,
        }
    )
    return response["ResponseMetadata"]["HTTPStatusCode"]
