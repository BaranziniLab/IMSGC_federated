import pandas as pd 
import argparse
from pathlib import Path
import os
import statsmodels.formula.api as smf
import logging
import sys



parser = argparse.ArgumentParser(prog='Federates Genomic Analysis',
                                 description= 'Run a Mixed Linear Model on the target metric controlling for covariates',
                                 epilog='Thanks for participating in the research project :) ')


parser.add_argument("-p", "--path",type=str, required=True, dest='path')
parser.add_argument("-t", "--target", type=str,  nargs='+', required=True, dest='target')
parser.add_argument('-id', '--id', type=str,nargs='+', required=True)
parser.add_argument("-c", "--covariates", type=str, nargs='+', required=True, dest='covariates')
parser.add_argument("-ft", '--file-type', choices=['csv', 'tsv', 'sas', 'spss'], default='csv')
parser.add_argument('-out', '--out', type=str, required=True)
parser.add_argument('-filter', '--filter-var', type=str, required=False, dest='filter_var')
args = parser.parse_args()


_delimiter = {'tsv':'/t', 'csv':',', }
file_dir = Path(args.path)
target = args.target
covariates = args.covariates
file_type = args.file_type
id = args.id
out_dir = args.out


sys.stdout = open(out_dir + '/logfile', 'w')
sys.stderr = open(out_dir + '/logfile_error', 'w')
sys.stdin = sys.stdout

id_string = id[0]
target_string = target[0]

if not file_dir.exists():
    print("The file for analysis doesn't exist, or there is a typo")
    raise SystemExit(1)

try:
    print('... loading file from: ' + args.path)
    df = pd.read_table(file_dir, delimiter=_delimiter[file_type])
except:
    print('Error reading file from Pandas. Check that the format of the file is correct')
    raise SystemExit(1)


final_columns = covariates + target 

if id != None:
    final_columns = id + final_columns


try:
   df_analysis = df[final_columns]
except KeyError:
    print('ERROR!: One or more columns are not in the dataframe. These are columns in the DF:')
    print(list(df.columns))
    print('And these are the one you selected for the analysis:')
    print(final_columns)
    raise SystemExit(1)

n_ids = df_analysis[id_string].nunique()
n_rows = len(df_analysis)

print('The data frame contains {id} unique patients, and {n} rows'.format(n = n_rows, id=n_ids))


n_rows_na = n_rows - len(df_analysis.dropna())

if n_rows_na > 0:
    print('The dataframe contains {n} NaN rows '.format(n = n_rows_na))
    df_analysis.dropna(inplace=True)

try:
    os.mkdir(out_dir)
except FileExistsError:
    print('Folder results already created')
    pass


string_formula_covariates = ' + '.join(covariates)

print("...Running analysis for {target}".format(target=target_string))

formula_maker = """{target} ~ {second_string}""".format(target=target_string, second_string = string_formula_covariates)

print("The formula for the analysis is: " + formula_maker)

#od = smf.ols(formula=formula_maker, data=df_analysis).fit()
mod = smf.mixedlm(formula_maker, data=df_analysis, groups=id_string, re_formula='~1').fit(reml=False)

metadata = mod.summary().tables[0]
results = mod.summary().tables[1].reset_index()

metadata_name = "/llm_metadata_{target}.tsv".format(target=target_string)
results_name = "/llm_results_{target}.tsv".format(target=target_string)

results.to_csv(out_dir + results_name,  sep='\t')
metadata.to_csv(out_dir + metadata_name, sep='\t')