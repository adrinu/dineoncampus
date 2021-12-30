from boto3.resources.model import Request
from botocore.config import Config
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


def get_menu(schoolname, tablename=secrets["tablename"]) -> int:
    table = db.Table(tablename)
    response = table.get_item(
        TableName="school_meals",
        Key={
          'schoolname': schoolname
       }
    ) 
    return response

def add_school(schoolname, data, tablename=secrets["tablename"]) -> int:
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
    return response["HTTPStatusCode"]

def update_menu(schoolname, new_data, tablename=secrets["tablename"]) -> int:
    """
    Updates a school's database info with new meals

    Args:
        schoolname (str): School name
        new_data (dict): Parsed information about meals
        tablename (str, optional): Table name stored in dynamoDB. Defaults to secrets["tablename"].

    Returns:
        [int]: HTTP Status code
    """
    
    table = db.Table(tablename)
    response = table.update_item(
        Key={
            'schoolname': schoolname
        },
        UpdateExpression="set meals=:d",
        ExpressionAttributeValues={
            ":d": new_data
        },
        ReturnValues="UPDATED_NEW"
    )
    return response["HTTPStatusCode"]