def getGeneMarkers(gtfFilePath):
    geneMarkers = []
    with open(gtfFilePath, 'r') as f:
        for line in f:
            metaData = line.split('\t')[8]
            if(metaData):
                metaDataList = metaData.split(';')
                geneName = None
                geneId = None
                for metaDataItem in metaDataList:
                    if metaDataItem.strip():
                        metaDataKeyValue = metaDataItem.strip().split()
                        metaDataKey = metaDataKeyValue[0].strip().strip('"')
                        metaDataValue = metaDataKeyValue[1].strip().strip('"')
                        if metaDataKey == 'gene_id':
                            geneId = metaDataValue
                        elif metaDataKey == 'gene_name':
                            geneName = metaDataValue
                if geneName and geneId and (geneName not in geneId):
                    geneMarkers.append(geneName)
    return geneMarkers


def createFastaFile(remapFilePath, fastaFilePath):
    import pandas as pd

    df = pd.read_csv(remapFilePath)
    with open(fastaFilePath, 'w+') as f:
        for i, row in df.iterrows():
                f.write('>' + str(row[0]) + '\n' + str(row[1]) + '\n')


if __name__ == '__main__':
    # getGeneMarkers('/home/yram0006/phd/chapter_3/workspace/EHR-Genomics/data/genome/annotation/GSE152834_GCF_900620245.1_BPH2947_genomic.gtf')
    # createFastaFile(
    #     '/home/yram0006/phd/chapter_3/workspace/EHR-Genomics/data/genome/remap/ALF23C222_short.fasta.gz.8000/train.csv.remap'
    #     , '/home/yram0006/phd/chapter_3/workspace/EHR-Genomics/data/genome/fasta/ALF23C222_short.fasta.gz.8000.fasta'
    #     )

    import os

    remapDir = '/home/yram0006/phd/chapter_3/workspace/EHR-Genomics/data/genome/simulated/remap'
    fastaDir = '/home/yram0006/phd/chapter_3/workspace/EHR-Genomics/data/genome/simulated/fasta'
    for dir in os.listdir(remapDir):
        createFastaFile(
            remapFilePath = remapDir + '/' + dir + '/train.csv.remap'
            , fastaFilePath = fastaDir + '/' + dir + '.fasta'
            )
