import pandas as pd


indexDf = pd.read_csv('/home/vmadmin/workspace/genome_data/index_saur.csv')

remapInfoFile = []

for i, row in indexDf.iterrows():
    print('i: ', i)
    dfs = []
    remapDf = pd.read_csv(row.remap_file)
    for j, remapRow in remapDf.iterrows():
        tempDf = pd.DataFrame({'token': remapRow.input_str[2:-2].replace('\n', '').split("' '"), 'token_type_id': remapRow.token_type_ids[1:-1].replace('\n', '').split(" ")})
        tempDf['idx'] = remapRow.idx.split(' ')[0]
        dfs.append(tempDf)
    df = pd.concat(dfs)
    df.to_csv('/home/vmadmin/workspace/genome_data/remap_info/' + row.specimen_id + '_remap_info.csv', index=False)
    remapInfoFile.append('https://raw.githubusercontent.com/ryashpal/ehr-int-vis/main/genomic_data/remap_info/' + row.specimen_id + '_remap_info.csv')
indexDf['remap_info_file'] = remapInfoFile

indexDf.to_csv('/home/vmadmin/workspace/genome_data/index_saur.csv', index=False)
