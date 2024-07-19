import pandas as pd


indexDf = pd.read_csv('/home/vmadmin/workspace/genome_data/index_saur.csv')

fastaInfoFile = []

for i, row in indexDf.iterrows():
    remapDf = pd.read_csv(row.remap_file)
    data = []
    for idx in remapDf.idx.unique():
        line = {'circular': 'false'}
        line['idx'] = idx.split(' ')[0]
        for attribute in idx.split(' '):
            if(len(attribute.split('=')) > 1):
                line[attribute.split('=')[0]] = attribute.split('=')[1]
        data.append(line)
    pd.DataFrame(data)[['idx' ,'length' ,'depth', 'circular']].to_csv('/home/vmadmin/workspace/genome_data/fasta_info/' + row.specimen_id + '_fasta_info.csv', index=False)
    fastaInfoFile.append('https://raw.githubusercontent.com/ryashpal/ehr-int-vis/main/genomic_data/fasta_info/' + row.specimen_id + '_fasta_info.csv')
indexDf['fasta_info_file'] = fastaInfoFile

indexDf.to_csv('/home/vmadmin/workspace/genome_data/index_saur.csv', index=False)
