import pandas as pd


cohortDf = pd.read_csv('/home/vmadmin/workspace/EHR-Genomics/data/omop_to_fhir/cohort_saur.csv')
mappingDf = pd.read_csv('/home/vmadmin/workspace/genome_data/mapping.csv', sep='\t')


def getRemapFile(tubeCode):
    import os
    remapFile = None
    for folder in os.listdir('/home/vmadmin/workspace/genome_data/remap_files'):
        if ('fasta.gz' in folder) and (tubeCode in folder):
            remapFile = '/home/vmadmin/workspace/genome_data/remap_files/' + folder + '/train.csv.remap'
    return remapFile
