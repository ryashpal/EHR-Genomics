from ehrgen.omop_to_fhir import Migrate as MigrateOmopToFhir
from ehrgen.gff_to_fhir import Migrate as MigrateGtfToFhir
from ehrgen.remap_to_fhir import Migrate as MigrateRemapToFhir
from ehrgen.config import RunConfig


if __name__ == "__main__":

    import logging
    import sys

    log = logging.getLogger("EHRQC")
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    if RunConfig.run_config_omop_to_fhir:
        for config in RunConfig.run_config_omop_to_fhir:
            log.info('Performing OMOP-to-FHIR conversion')
            if config['type'] == 'migrate':
                MigrateOmopToFhir.omopToFhir(
                    entity=config['entity'],
                    sqlFilePath=config['sqlFilePath'],
                    jsonTemplatePath=config['jsonTemplatePath'],
                    mapping=config['json_sql_mapping'],
                    readFromDb=config['readFromDb'],
                    loadToFHIR = config['loadToFHIR'],
                    save=config['save'],
                    savePath=config['savePath']
                    )
            elif config['type'] == 'execute':
                if 'function' in config:
                    if 'args' in config:
                        config['function'](args=config['args'])
                    else:
                        config['function']()


    # if RunConfig.run_config_fhir_to_omop:
    #     for config in RunConfig.run_config_fhir_to_omop:
    #         log.info('Performing FHIR-to-OMOP conversion')
    #         if config['type'] == 'migrate':
    #             Migrate.fhirToOmop(
    #                 entity=config['entity'],
    #                 urlQueryStringPath=config['urlQueryStringPath'],
    #                 sqlFilePath=config['sqlFilePath'],
    #                 mapping=config['sql_json_mapping'],
    #                 )


    for config in RunConfig.run_config_gtf_to_fhir:
        log.info('Performing GTF-to-FHIR conversion')
        if config['type'] == 'migrate':
            MigrateGtfToFhir.gtfToFhir(
                indexFile=config['index_file'],
                jsonTemplatePath=config['jsonTemplatePath'],
                    save=config['save'],
                    savePath=config['savePath'],
                )


    for config in RunConfig.run_config_remap_to_fhir:
        log.info('Performing REMAP-to-FHIR conversion')
        if config['type'] == 'migrate':
            MigrateRemapToFhir.remapToFhir(
                indexFile=config['index_file'],
                jsonTemplatePath=config['jsonTemplatePath'],
                    save=config['save'],
                    savePath=config['savePath'],
                )
