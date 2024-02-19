import json
import pathlib

from tqdm import tqdm
from datetime import datetime

from ehrgen.utils.DbUtils import readDbFromSql
from ehrgen.utils.FileUtils import readTemplate
from ehrgen.utils.FhirUtils import put
from ehrgen.utils.Utils import convertIdFromFhirToOmop

import logging

log = logging.getLogger("EHRQC")


def omopToFhir(entity, sqlFilePath, jsonTemplatePath, mapping, save=False, savePath='./'):
    log.info('Starting OMOP to FHIR for ' + entity)
    log.info('sqlFilePath: ' + sqlFilePath)
    log.info('jsonTemplatePath: ' + jsonTemplatePath)
    log.info('mapping: ' + str(mapping))
    omopData = readDbFromSql(sqlFilePath)
    log.debug('omopData: ' + str(omopData))
    fhirTemplate = readTemplate(jsonTemplateFile=jsonTemplatePath)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    for i, row in tqdm(omopData.iterrows(), total=omopData.shape[0]):
        log.debug('i: ' + str(i))
        log.debug('row: ' + str(row))
        fhirJson = mapSqlToJson(row, fhirTemplate, mapping)
        log.debug('fhirJson: ' + str(fhirJson))
        response = put(entity + '/' + str(row.id), fhirJson) # move this line to Utility fucntion
        log.debug('response: ' + str(response.text))
        if save:
            pathlib.Path(savePath).mkdir(parents=True, exist_ok=True)
            saveFile = savePath + '/' + str(row.id) + '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.json'
            log.debug('Saving json to file: ' + saveFile)
            with open(saveFile, "w") as f:
                json.dump(fhirJson, f)


def mapSqlToJson(row, fhirTemplate, mapping):
    for keys in mapping.keys():
        value = mapping[keys]
        if(isinstance(value, str)):
            keyList = keys.split('||')
            if len(keyList)>1:
                childNode = fhirTemplate
                for i in range((len(keyList) - 1)):
                    childNode = childNode[keyList[i]]
                childNode[keyList[i + 1]] = row[value]
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
    return fhirTemplate