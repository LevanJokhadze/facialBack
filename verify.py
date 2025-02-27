import os
import json
import yk_face as YKF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify(template):
    # Set API credentials
    KEY = os.getenv("YOUVERSE")  # or your hard-coded key
    YKF.Key.set(KEY)
    temp = list()
    tempDict = dict()

    BASE_URL = os.getenv("BASE_URL")  # or your hard-coded URL
    YKF.BaseUrl.set(BASE_URL)
    templates = []
    templates_file = "templates.json"

    with open(templates_file, "r") as file:
        templates = json.load(file)

    for i in templates:
        matching_score = YKF.face.verify(i['template'], template)
        tempDict['name'] = i['name']
        tempDict['last_name'] = i['last_name']
        tempDict['age'] = i['age']
        tempDict['score'] = matching_score
        temp.append(tempDict)

    detect = max(temp, key=lambda score: score['score'])
    if detect['score'] > 0.7:
        print(detect)
        return detect
    else:
        return False
        