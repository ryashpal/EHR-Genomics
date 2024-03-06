import os
import json
from tqdm import tqdm


for file in tqdm(os.listdir('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/observation/raw_to_be_corrected')):
    with open('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/observation/raw_to_be_corrected/' + file) as f:
        fhirJson = json.load(f)
    fhirJson['encounter']['reference'] = fhirJson['encounter']['reference'].replace('''Encounter/P''', '''Encounter/E''')
    with open('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/observation/raw/' + file, "w") as f:
        json.dump(fhirJson, f)
    os.remove('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/observation/raw_to_be_corrected/' + file)
