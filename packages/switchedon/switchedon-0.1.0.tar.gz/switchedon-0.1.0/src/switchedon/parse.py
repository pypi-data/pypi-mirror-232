import argparse
import os
import inquirer
import numpy as np
import pandas as pd

CREDIT = "Credit"
DEBIT = "Debit"

bban = {
    "00803660466350": {
        "currency": "KSH",
        "name": "Switched On World Ltd - KES - I&M Bank"
    },
    "00803660461250": {
        "currency": "USD",
        "name": "Switched On World Ltd - USD - I&M Bank"
    }
}

def convert_date_format(df, column_name: str):
    df[column_name] = pd.to_datetime(df[column_name], dayfirst=True)
    df[column_name] = df[column_name].dt.strftime("%Y-%m-%d")

def parse_csv(input_file, output_file):
    input_df = pd.read_csv(input_file, dtype = {'Account number(BBAN)': str})
    convert_date_format(input_df, "Book date")
    print(f"Successfully read {len(input_df)} transactions")
    output_df = pd.DataFrame()

    def get_account_name(x):
        if x in bban:
            return bban[x]["name"]
        print(x)
        raise ValueError("Unknown account number")

    output_df["Date"] = input_df["Book date"]
    output_df["Deposit"] = np.where(input_df["Credit/debit indicator"] == CREDIT, input_df["Amount"], 0)
    output_df["Withdrawal"] = np.where(input_df["Credit/debit indicator"] == DEBIT, input_df["Amount"], 0)
    output_df["Description"] = input_df["Description"]
    output_df["Reference Number"] = input_df["Transaction reference"]
    output_df["Bank Account"] = input_df["Account number(BBAN)"].apply(get_account_name)
    output_df["Currency"] = input_df["Instructed currency"]

    output_df = output_df[::-1] # reverse row order
    if len(output_df) != len(input_df):
        raise ValueError("Row count mismatch between input and output dataframes")
    output_df.to_csv(output_file, index=False)
    print(f"Successfully parsed {len(output_df)} transactions")

def get_directory_and_file():
    base_dir = './transactions'
    directories = [name for name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, name))]

    directory_questions = [
        inquirer.List('directory',
                      message="Which folder do you want to use?",
                      choices=directories,
                      ),
    ]

    directory_answers = inquirer.prompt(directory_questions)
    selected_directory = directory_answers['directory']

    files = [f for f in os.listdir(os.path.join(base_dir, selected_directory)) if os.path.isfile(os.path.join(base_dir, selected_directory, f))]

    file_questions = [
        inquirer.List('file',
                      message="Which file do you want to use?",
                      choices=files,
                      ),
    ]

    file_answers = inquirer.prompt(file_questions)
    selected_file = file_answers['file']

    return [base_dir, selected_directory, selected_file]

def main():
    [base_dir, directory, file_name] = get_directory_and_file()
    input_file_path = os.path.join(base_dir, directory, file_name)
    output_file_path = os.path.join('./parsed', directory, file_name)
    parse_csv(input_file_path, output_file_path)

if __name__ == "__main__":
    main()