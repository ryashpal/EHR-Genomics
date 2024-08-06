import pandas as pd

from src.ehrgen.utils import FhirUtils


def extract(name, lowerRiskScore, higherRiskScore, fromDate, toDate, savePath):

    responses = FhirUtils.readData(
        'http://10.172.235.4:8080/fhir/Patient?name=' + str(name)
        + '&_has:RiskAssessment:subject:probability=ge' + str(lowerRiskScore)
        + '&_has:RiskAssessment:subject:probability=le' + str(higherRiskScore)
        + (('&_has:Encounter:subject:date-start=ge' + str(fromDate)) if fromDate else '')
        + (('&_has:Encounter:subject:date-start=ge' + str(toDate)) if toDate else '')
    )

    patientRows = []
    for response in responses:
        if 'entry' in response:
            entries = response['entry']
            for entry in entries:
                row = {
                    'patient_id': entry['resource']['id'],
                }
                patientRows.append(row)

    dfs = []
    for patientRow in patientRows:
        responses = FhirUtils.readData('http://10.172.235.4:8080/fhir/MolecularSequence?subject=' + patientRow['patient_id'])
        for response in responses:
            if 'entry' in response:
                entries = response['entry']
                for entry in entries:
                    for formatted in entry['resource']['formatted']:
                        if(formatted['title'] == 'Remap info file'):
                            df = pd.read_csv(formatted['url'])
                            df['tube_id'] = entry['resource']['id']
                            df['patient_id'] = patientRow['patient_id']
                            dfs.append(df)
    mergedDf = pd.concat(dfs)
    mergedDf.to_csv(savePath, index=False)


if __name__ == '__main__':

    import logging
    import sys
    import argparse

    log = logging.getLogger("EHR-Int")
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    log.info("Parsing command line arguments")

    parser = argparse.ArgumentParser(description='EHR-Int data integration utility')

    parser.add_argument('-n', '--name', nargs=1, default='', help='Patient name')

    parser.add_argument('-lrs', '--lower_risk_score', nargs=1, type=float, default=[0],
                        help='Specify the lower risk score cutoff value. By default: [-lrs=0]')

    parser.add_argument('-hrs', '--higher_risk_score', nargs=1, type=float, default=[1],
                        help='Specify the higher risk score cutoff value. By default: [-hrs=1]')

    parser.add_argument('-fd', '--from_date', nargs=1, default=[''], help='From Date in the format [YYYY-MM-DD]')

    parser.add_argument('-td', '--to_date', nargs=1, default=[''], help='To Date in the format [YYYY-MM-DD]')

    parser.add_argument('-sp', '--save_path', nargs=1, default=['/tmp/genomics.csv'],
                        help='Path of the file to store the outputs')

    args = parser.parse_args()

    log.info('args.name: ' + str(args.name[0]))
    log.info('args.lower_risk_score: ' + str(float(args.lower_risk_score[0])))
    log.info('args.higher_risk_score: ' + str(float(args.higher_risk_score[0])))
    log.info('args.from_date: ' + str(args.from_date[0]))
    log.info('args.to_date: ' + str(args.to_date[0]))
    log.info('args.save_path: ' + str(args.save_path[0]))

    extract(
        name = str(args.name[0]),
        lowerRiskScore = float(args.lower_risk_score[0]),
        higherRiskScore = float(args.higher_risk_score[0]),
        fromDate = str(args.from_date[0]),
        toDate = str(args.to_date[0]),
        savePath = str(args.save_path[0])
    )
