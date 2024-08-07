import json

import pathlib

import random

import pandas as pd
import numpy as np

from tqdm import tqdm
from datetime import datetime

from src.ehrgen.utils.FileUtils import readTemplate
from src.ehrgen.utils.FhirUtils import put

import logging

log = logging.getLogger("EHRQC")


def genomeToFhir(indexFile, jsonTemplatePath, save=False, savePath='./'):
    log.info('indexFile: ' + indexFile)
    log.info('jsonTemplatePath: ' + jsonTemplatePath)
    fhirTemplate = readTemplate(jsonTemplateFile=jsonTemplatePath)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    indexDf = pd.read_csv(indexFile)
    for i, row in tqdm(indexDf.iterrows(), total=indexDf.shape[0]):
        fhirJson = mapGenomeToJson(row, fhirTemplate)
        log.debug('fhirJson: ' + str(fhirJson))
        response = put('MolecularSequence/' + str(row.specimen_id), fhirJson)
        log.debug('response: ' + str(response.text))
        if save:
            pathlib.Path(savePath).mkdir(parents=True, exist_ok=True)
            saveFile = savePath + '/' + str(row.specimen_id) + '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.json'
            log.debug('Saving json to file: ' + saveFile)
            with open(saveFile, "w") as f:
                json.dump(fhirJson, f)


def mapGenomeToJson(row, fhirTemplate):
    fhirTemplate['id'] = row['specimen_id']
    fhirTemplate['subject']['reference'] = 'Patient/P' + str(row['patient_id'])
    fhirTemplate['formatted'][0]['url'] = '' if pd.isnull(row['amr_file']) else row['amr_file']
    fhirTemplate['formatted'][1]['url'] = '' if pd.isnull(row['remap_file']) else row['remap_file']
    fhirTemplate['formatted'][2]['url'] = '' if pd.isnull(row['fasta_info_file']) else row['fasta_info_file']
    fhirTemplate['formatted'][3]['url'] = '' if pd.isnull(row['remap_info_file']) else row['remap_info_file']
    fhirTemplate['extension'][0]['valueString'] = 'Chromosome'
    return fhirTemplate
