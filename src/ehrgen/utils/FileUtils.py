import json


def readTemplate(jsonTemplateFile):
    with open(jsonTemplateFile) as f:
        jsonTemplate = f.read()
    return json.loads(jsonTemplate)


def readSqlFile(sqlFilePath):
    sql = None
    with open(sqlFilePath) as f:
        sql = f.read()
    return sql