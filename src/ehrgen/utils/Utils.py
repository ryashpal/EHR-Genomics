import warnings
warnings.filterwarnings('ignore')


def convertIdFromFhirToOmop(fhirId):
    omopId = '-' + str(fhirId)[1:] if str(fhirId).startswith('m') else str(fhirId)[1:]
    return omopId