import json

import pathlib

import random

import pandas as pd

from tqdm import tqdm
from datetime import datetime

from ehrgen.utils.FileUtils import readTemplate
from ehrgen.utils.FhirUtils import put

import logging

log = logging.getLogger("EHRQC")


def remapToFhir(indexFile, jsonTemplatePath, save=False, savePath='./'):
    log.info('indexFile: ' + indexFile)
    log.info('jsonTemplatePath: ' + jsonTemplatePath)
    fhirTemplate = readTemplate(jsonTemplateFile=jsonTemplatePath)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    indexDf = pd.read_csv(indexFile)
    for i, row in tqdm(indexDf[:10].iterrows(), total=indexDf.shape[0]):
        print('row: ', row)
        fhirJson = mapRemapToJson(row, fhirTemplate)
        log.info('fhirJson: ' + str(fhirJson))
        response = put('MolecularSequence/' + str(row.specimen_id), fhirJson)
        log.debug('response: ' + str(response.text))
        if save:
            pathlib.Path(savePath).mkdir(parents=True, exist_ok=True)
            saveFile = savePath + '/' + str(row.specimen_id) + '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.json'
            log.debug('Saving json to file: ' + saveFile)
            with open(saveFile, "w") as f:
                json.dump(fhirJson, f)


def mapRemapToJson(row, fhirTemplate):
    fhirTemplate['id'] = row['specimen_id']
    fhirTemplate['subject']['reference'] = 'Patient/' + row['person_id']
    fhirTemplate['formatted'][0]['url'] = row.fasta_file
    fhirTemplate['formatted'][1]['url'] = row.remap_file
    fhirTemplate['extension'][0]['valueString'] = random.choice(['Chromosome', 'Plasmid'])
    return fhirTemplate
