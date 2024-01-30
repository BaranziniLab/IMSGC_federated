import pandas as pd 
import argparse
from pathlib import Path
import os
import statsmodels.formula.api as smf
import logging
import sys



parser = argparse.ArgumentParser(prog='Federates Genomic Analysis',
                                 description= 'Convert wide-format data to long-format',
                                 epilog='Thanks for participating in the research project :) ')


parser.add_argument("-p", "--path",type=str, required=True, dest='path')
parser.add_argument("-t", "--target", type=str,  nargs='+', required=True, dest='target')
parser.add_argument('-id', '--id', type=str,nargs='+', required=True)
parser.add_argument("-c", "--covariates", type=str, nargs='+', required=True, dest='covariates')
parser.add_argument("-time", "--time", type=str,  nargs='+', required=True, dest='time')
parser.add_argument("-ft", '--file-type', choices=['csv', 'tsv', 'sas', 'spss'], default='csv')
parser.add_argument('-out', '--out', type=str, required=True)
parser.add_argument('-filter', '--filter-var', type=str, required=False, dest='filter_var')
args = parser.parse_args()




_delimiter = {'tsv':'/t', 'csv':',', }
file_dir = Path(args.path)
targets = args.target
covariates = args.covariates
times = args.time 
file_type = args.file_type
id = args.id
out_dir = args.out

try:
    os.mkdir(out_dir)
except FileExistsError:
    print('Folder results already created')
    pass


sys.stdout = open(out_dir + '/wide_to_long_logger.log', 'w')
sys.stderr = sys.stdout
sys.stdin = sys.stdout

id_string = id[0]
target_string = targets[0]


if not file_dir.exists():
    print("The file for analysis doesn't exist, or there is a typo")
    raise SystemExit(1)

try:
    print('... loading file from: ' + args.path)
    df = pd.read_table(file_dir, delimiter=_delimiter[file_type])
except:
    print('Error reading file from Pandas. Check that the format of the file is correct')
    raise SystemExit(1)

final_columns = covariates + targets + id 


try:
   df_analysis = df[final_columns]
except KeyError:
    print('ERROR!: One or more columns are not in the dataframe. These are columns in the DF:')
    print(list(df.columns))
    print('And these are the one you selected for the analysis:')
    print(final_columns)
    raise SystemExit(1)

df_analysis = df_analysis.melt(id_vars=covariates + id)
df_analysis.dropna(inplace=True)


for time, tar in zip(times, targets):

    df_analysis.loc[df_analysis['variable'] ==  tar, 'time'] = time
    
results_name = "/long_transformed_{target}.tsv".format(target=target_string)
df_analysis.to_csv(out_dir + results_name,  sep='\t', index=False)