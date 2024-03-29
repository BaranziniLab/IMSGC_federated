import pandas as pd 
import argparse
from pathlib import Path
import os
import statsmodels.formula.api as smf
import logging
import sys



parser = argparse.ArgumentParser(prog='Federates Genomic Analysis',
                                 description= 'Run a Simple Linear Regression on the target metric controlling for covariates',
                                 epilog='Thanks for participating in the research project :) ')


parser.add_argument("-p", "--path",type=str, required=True, dest='path')
parser.add_argument("-t", "--target", type=str, nargs='+', required=True, dest='target')
parser.add_argument('-id', '--id', type=str, required=False)
parser.add_argument("-c", "--covariates", type=str, nargs='+', required=True, dest='covariates')
parser.add_argument("-ft", '--file-type', choices=['csv', 'tsv', 'sas', 'spss'], default='csv')
parser.add_argument('-out', '--out', type=str, required=True)
args = parser.parse_args()

_delimiter = {'tsv':'/t', 'csv':',', }
file_dir = Path(args.path)
targets = args.target
covariates = args.covariates
file_type = args.file_type
id = args.id
out_dir = args.out


try:
    os.mkdir(out_dir)
except FileExistsError:
    print('Folder results already created')
    pass

sys.stdout = open(out_dir + '/logfile_base.log', 'w')
sys.stderr = sys.stdout
sys.stdin = sys.stdout

if not file_dir.exists():
    print("The file for analysis doesn't exist, or there is a typo")
    raise SystemExit(1)


try:
    print('... loading file from: ' + args.path)
    df = pd.read_table(file_dir, delimiter=_delimiter[file_type])
except:
    print('Error reading file from Pandas. Check that the format of the file is correct')
    raise SystemExit(1)

final_columns = covariates + targets 
if id != None:
    final_columns = list(id) + final_columns

try:
   df_analysis = df[final_columns]
except KeyError:
    print('ERROR!: One or more columns are not in the dataframe. These are columns in the DF:')
    print(list(df.columns))
    print('And these are the one you selected for the analysis:')
    print(final_columns)
    raise SystemExit(1)


if id != None:
    amount_of_duplicated = len(df_analysis.loc[df_analysis[id].duplicated()])

    if amount_of_duplicated > 0:
        print('!! ALARM : THERE ARE DUPLICATED IDS !! ')

    amount_of_duplicated.drop_duplicates(subset=id)

n_rows = len(df_analysis)

print('The data frame contains {n} rows'.format(n = n_rows))

n_rows_na = n_rows - len(df_analysis.dropna())
if n_rows_na > 0:
    print('The dataframe contains {n} NaN rows '.format(n = n_rows_na))
    df_analysis.dropna(inplace=True)


for target_var in targets:

    string_formula_covariates = ' + '.join(covariates)

    print("...Running analysis for {target}".format(target=target_var))

    formula_maker = """{target} ~ {second_string}""".format(target=target_var, second_string = string_formula_covariates)

    print("The formula for the analysis is: " + formula_maker)
    mod = smf.ols(formula=formula_maker, data=df_analysis).fit()

    metadata = pd.read_html(mod.summary().tables[0].as_html(),header=0,index_col=0)[0].reset_index()
    results = pd.read_html(mod.summary().tables[1].as_html(),header=0,index_col=0)[0].reset_index()

    metadata_name = "/metadata_{target}.tsv".format(target=target_var)
    results_name = "/results_{target}.tsv".format(target=target_var)

    results.to_csv(out_dir + results_name, index=False, sep='\t')
    metadata.to_csv(out_dir + metadata_name, index=False, sep='\t')
