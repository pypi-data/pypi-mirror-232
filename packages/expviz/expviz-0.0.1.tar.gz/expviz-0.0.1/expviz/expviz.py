import pandas as pd
from tabulate import tabulate
from IPython.display import display, HTML
import os
import json

# Set global display options
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

# Function to convert nested dictionary to DataFrame
def dict_to_dataframe(data, fmt='{:,.3g}', transpose = False):
    for exp in data:
        for metric in data[exp]:
            try:
                data[exp][metric] = fmt.format(data[exp][metric])
            except:
                pass
    df = pd.DataFrame(data).T
    if transpose:
        df = df.T
    return df

# Function to convert DataFrame to LaTeX
def to_latex(data, fmt='{:,.3g}', transpose=False, escape=None):
    df = dict_to_dataframe(data, fmt = fmt, transpose = transpose)
    latex_code = df.to_latex(escape=escape)
    
    # Fit the LaTeX table into the template
    table_tmp = """\\begin{table}[t]
    \\centering
    \\scriptsize
    
    %s
    
    \caption{Caption Title.}
    \label{tab:tablename}
    \end{table}
    """
    return table_tmp % latex_code

# Function to convert DataFrame to Markdown
def to_markdown(data, fmt='{:,.3g}', transpose=False):
    df = dict_to_dataframe(data, fmt = fmt, transpose = transpose)
    markdown_table = tabulate(df, tablefmt="pipe", headers="keys")
    return markdown_table

# Function to display DataFrame in Jupyter
def show(data, fmt='{:,.3g}', transpose=False):
    df = dict_to_dataframe(data, fmt = fmt, transpose = transpose)
    display(HTML(df.to_html()))

def read_results(baseurl, expnames, filename="eval.json"):
    results = {}
    if isinstance(expnames, list):
        for expname in expnames:
            filepath = os.path.join(baseurl, expname, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    results[expname] = json.load(file)
            else:
                print(f"File not found: {filepath}")
    elif isinstance(expnames, dict):
        for key, value in expnames.items():
            filepath = os.path.join(baseurl, value, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    results[key] = json.load(file)
            else:
                print(f"File not found: {filepath}")
    else:
        print("Invalid expnames type. It should be either a list or a dict.")
    return results
