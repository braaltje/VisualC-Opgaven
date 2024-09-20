import requests
import pandas as pd
import numpy as np
import os
from pandas import json_normalize
import json
import re
import time
import warnings
import zipfile
from os import listdir
from os.path import isfile, join

warnings.filterwarnings("ignore")

def removeSpecialChars(x):
    if type(x) == str:
        x = re.sub(r'(<!--.*?-->|<[^>]*>)', '', x)
        x = x.replace('&nbsp;', ' ')
        x = x.replace('\\n', ' ')
        x = x.replace('\n', ' ')
        x = x.replace('&gt;', '>')
        x = x.replace('&amp;', '&')
        x = x.replace('\\', '')
        x = re.sub(r'[^A-Za-z0-9!?.,: ()]+\'-/%&@', '', x)
    return x

def main():
    surveyIds = {
        "SV_3TPNSvgX6GtUpuJ",
        "SV_baA0LNAF2jjkEsZ",
        "SV_4YqhIQsgWKbxOFo",
        "SV_ebUChSnjxIo94Ox",
    }

    datastore_path = r"C:\Files\Qualtrics"

    for surveyId in surveyIds:

        my_headers = {
            'X-API-Token': '5idBrasSItt5NHwW1XQZLGxPywYEU0CEvEvNCfVl'}
        
        exportResponseURL = 'https://eu.qualtrics.com/API/v3/surveys/{0}/export-responses'.format(
            surveyId)
        exportResponseBody = {'format': 'json'}
        exportResponsePost = requests.post(
            exportResponseURL, headers=my_headers, json=exportResponseBody, verify=False)

        exportResponsePostJson = json.loads(exportResponsePost.content)

        exportResponseProgress = exportResponsePostJson['result']['status']

        exportResponseProgressID = exportResponsePostJson['result']['progressId']

        exportResponseStatusURL = 'https://eu.qualtrics.com/API/v3/surveys/{}/export-responses/{}'.format(
            surveyId, exportResponseProgressID)

        while exportResponseProgress != 'complete':
            exportResponseStatusResponse = requests.get(
                exportResponseStatusURL, headers=my_headers, verify=False)
            exportResponseStatusJson = json.loads(
                exportResponseStatusResponse.content)
            exportResponseProgress = exportResponseStatusJson['result']['status']
            if exportResponseProgress != 'complete':
                time.sleep(5)

        exportResponseFileID = exportResponseStatusJson['result']['fileId']

        exportFileURL = 'https://eu.qualtrics.com/API/v3/surveys/{}/export-responses/{}/file'.format(
            surveyId, exportResponseFileID)

        exportFileResponse = requests.get(
            exportFileURL, headers=my_headers, verify=False)

        FileName = "temp.zip"
        filePath = os.path.join(datastore_path, FileName)

        open(filePath, 'wb').write(exportFileResponse.content)
        print('ZIP file downloaded')

        unzipFolderName = surveyId + '-Unzip'
        unzipFolderPath = os.path.join(datastore_path, unzipFolderName)
        with zipfile.ZipFile(filePath, 'r') as zip_ref:
            zip_ref.extractall(unzipFolderPath)

        print('File was unzipped')

        # if surveyId == "SV_4YqhIQsgWKbxOFo":
        #     unzipFolderPath = join(unzipFolderPath, 'CIG')
        #     unzipFolderName = join(unzipFolderName, 'CIG')

        # onlyfiles = [f for f in listdir(unzipFolderPath) if isfile(join(unzipFolderPath, f))]

        questionsURL = 'https://eu.qualtrics.com/API/v3/survey-definitions/{0}/questions'.format(
            surveyId)
        # Modified to ignore cert verification
        questionsResponse = requests.get(
            questionsURL, headers=my_headers, verify=False)
        questionsJson = questionsResponse.json() #type-dict

        # df_question_json = json_normalize(
        #     questionsJson['result'], record_path='elements')
        
        FileName = 'Questions_'+ surveyId+ '.json'
        
        filePath = os.path.join(unzipFolderPath, FileName)

        if surveyId == "SV_4YqhIQsgWKbxOFo":
            filePath = os.path.join(unzipFolderPath + '/CIG', FileName)

        # df_question_json.to_csv(filePath, index=False)

        with open(filePath, 'w', encoding='utf-8') as file:
             json.dump(questionsJson, file, ensure_ascii=False)

if __name__ == '__main__':
    main()