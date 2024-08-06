import json
import pathlib

import pandas as pd

from tqdm import tqdm
from datetime import datetime

from src.ehrgen.utils.FileUtils import readTemplate
from src.ehrgen.utils.FhirUtils import put
from src.ehrgen.utils.GenomeUtils import getGeneMarkers

import logging

log = logging.getLogger("EHRQC")


def gtfToFhir(indexFile, jsonTemplatePath, save=False, savePath='./'):
    log.info('indexFile: ' + indexFile)
    log.info('jsonTemplatePath: ' + jsonTemplatePath)
    fhirTemplate = readTemplate(jsonTemplateFile=jsonTemplatePath)
    log.debug('fhirTemplate: ' + str(fhirTemplate))
    indexDf = pd.read_csv(indexFile)
    for i, row in tqdm(indexDf[:10].iterrows(), total=indexDf.shape[0]):
        markers = getGeneMarkers(row.annotation_file)
        log.debug('markers: ' + str(markers))
        for marker in markers:
            fhirJson = mapGtfToJson(row, marker, fhirTemplate)
            log.debug('fhirJson: ' + str(fhirJson))
            response = put('Observation/' + str(row.specimen_id) + '_' + str(marker), fhirJson)
            log.debug('response: ' + str(response.text))
            if save:
                pathlib.Path(savePath).mkdir(parents=True, exist_ok=True)
                saveFile = savePath + '/' + str(row.specimen_id) + '_' + str(marker) + '_' + datetime.today().strftime('%Y%m%d_%H%M%S') + '.json'
                log.debug('Saving json to file: ' + saveFile)
                with open(saveFile, "w") as f:
                    json.dump(fhirJson, f)


def mapGtfToJson(row, marker, fhirTemplate):
    fhirTemplate['id'] = row['specimen_id'] + '_' + str(marker)
    fhirTemplate['subject']['reference'] = 'Patient/' + row['person_id']
    fhirTemplate['encounter']['reference'] = 'Encounter/' + row['episode_id']
    fhirTemplate['valueString'] = marker
    return fhirTemplate
