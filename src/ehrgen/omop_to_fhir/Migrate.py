import os
import json
import pathlib

from tqdm import tqdm
from datetime import datetime

from multiprocessing import Pool

from src.ehrgen.utils.DbUtils import readDbFromSql
from src.ehrgen.utils.FileUtils import readTemplate
from src.ehrgen.utils.FhirUtils import put
from src.ehrgen.utils.Utils import convertIdFromFhirToOmop

import logging

# logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger("EHRQC")


def omopToFhir(entity, sqlFilePath, jsonTemplatePath, mapping, readFromDb=False, loadToFHIR=False, save=False, savePath='./'):
    log.info('Starting OMOP to FHIR for ' + entity)
    log.info('sqlFilePath: ' + sqlFilePath)
    log.info('jsonTemplatePath: ' + jsonTemplatePath)
    log.info('mapping: ' + str(mapping))
    log.info('readFromDb: ' + str(readFromDb))
    log.info('loadToFHIR: ' + str(loadToFHIR))
    log.info('save: ' + str(save))
    log.info('savePath: ' + str(savePath))
    omopData = readDbFromSql(sqlFilePath)
    log.debug('omopData: ' + str(omopData))
    fhirTemplate = readTemplate(jsonTemplateFile=jsonTemplatePath)
    log.info('fhirTemplate: ' + str(fhirTemplate))
    rawSavePath = savePath + '/raw'
    pathlib.Path(rawSavePath).mkdir(parents=True, exist_ok=True)
    if readFromDb:
        log.info('Saving raw json files')
        for i, row in tqdm(omopData.iterrows(), total=omopData.shape[0]):
            log.debug('i: ' + str(i))
            log.debug('row: ' + str(row))
            fhirJson = mapSqlToJson(row, fhirTemplate, mapping)
            rawFile = pathlib.Path(rawSavePath + '/' + str(i) + '_' + str(row.id) + '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.json')
            if not rawFile.is_file():
                with open(rawFile, "w") as f:
                    json.dump(fhirJson, f)
    if loadToFHIR:
        log.info('Loading json data to FHIR')
        i = 0
        fileList = os.listdir(rawSavePath)[:10000]
        while fileList and (len(fileList) > 0):
            i += 1
            log.info('Records Completed: ' + str(i * 10000))
            poolArgs = []
            for rawFilePath in tqdm(fileList):
                poolArgs.append((entity, save, savePath, rawSavePath, rawFilePath))
            with Pool(4) as p:
                p.starmap(loadJsonToFhir, poolArgs)
            fileList = os.listdir(rawSavePath)[:10000]
            # fileList = None


def loadJsonToFhir(entity, save, savePath, rawSavePath, rawFilePath):
    log.debug('rawFilePath: ' + str(rawFilePath))
    fhirJson = None
    with open(rawSavePath + '/' + rawFilePath) as f:
        fhirJson = json.load(f)
    response = put(entity + '/' + str(rawFilePath.split('_')[1]), fhirJson)
    log.debug('response: ' + str(response.text))
    subDirPath = None
    if save:
        if response.ok:
            subDirPath = savePath + '/success'
        else:
            subDirPath = savePath + '/failure'
        pathlib.Path(subDirPath).mkdir(parents=True, exist_ok=True)
        saveFile = subDirPath + '/' + rawFilePath
        log.debug('Saving json to file: ' + saveFile)
        os.replace(src=rawSavePath + '/' + rawFilePath, dst=saveFile)


def mapSqlToJson(row, fhirTemplate, mapping):

    log.debug('row')
    log.debug(row)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    log.debug('mapping: ' + str(mapping))

    for keys in mapping.keys():
        log.debug('keys: ' + str(keys))
        value = mapping[keys]
        if(isinstance(value, str)):
            keyList = keys.split('||')
            log.debug('keyList: ' + str(keyList))
            if len(keyList)>1:
                childNode = fhirTemplate
                for i in range((len(keyList) - 1)):
                    index = keyList[i]
                    if index.isdigit():
                        index = int(index)
                    log.debug('index: ' + str(index))
                    childNode = childNode[index]
                index = keyList[i + 1]
                if index.isdigit():
                    index = int(index)
                childNode[index] = row[value]
            else:
                childNode = fhirTemplate
                childNode[keys] = row[value]
        else:
            innerData = readDbFromSql(sqlFilePath=value['sqlFilePath'], params=convertIdFromFhirToOmop(row['id']))
            innerFhirTemplate = None
            for j, innerRow in innerData.iterrows():
                innerFhirTemplate = readTemplate(jsonTemplateFile=value['jsonTemplatePath'])
                for innerKeys in value['json_sql_mapping']:
                    innerValue = value['json_sql_mapping'][innerKeys]
                    innerKeyList = innerKeys.split('||')
                    if len(innerKeyList)>1:
                        childNode = innerFhirTemplate
                        for i in range((len(innerKeyList) - 1)):
                            childNode = childNode[innerKeyList[i]]
                        childNode[innerKeyList[i + 1]] = innerRow[innerValue]
                    else:
                        childNode = innerFhirTemplate
                        childNode[innerKeys] = row[innerValue]
            childNode = fhirTemplate
            childNode[keys] = [innerFhirTemplate]
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    return fhirTemplate
