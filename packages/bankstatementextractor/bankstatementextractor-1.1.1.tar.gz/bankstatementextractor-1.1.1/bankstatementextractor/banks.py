import base64
import cv2
import io
import numpy as np
import re
from datetime import datetime
from PIL import Image
from bankstatementextractor.bank_utils import *

import fitz  # PyMuPDF library
import PyPDF2  # PyPDF2 library
import os
import subprocess
import torch
from pdf2image import convert_from_path
from unidecode import unidecode
import pandas as pd
import itertools    
os.sys.path
from io import StringIO

class Banks:

    def __init__(self):
        pass

    # def adcb_1(): 
    def adib_1(self,file_path):
        try:
            doc = fitz.open(file_path)
            output = []

            for page in doc:
                page_output = page.get_text("blocks")
                output.append(page_output)

            plain_text_data = []

            for page_output in output:
                previous_block_id = 0
                page_plain_text_data = []

                for block in page_output:
                    if block[6] == 0:
                        if previous_block_id != block[5]:
                            plain_text = unidecode(block[4])
                            page_plain_text_data.append(plain_text)
                            previous_block_id = block[5]

                if 'Consolidated Statement\n' in page_plain_text_data:
                    continue

                page_plain_text_data = [text for text in page_plain_text_data if not text.startswith(('balance', 'opening'))]

                plain_text_data.append(page_plain_text_data)

            flat_data = [item for sublist in plain_text_data for item in sublist]

            ob = r'Opening Balance\n([\d,.]+)'
            opening_balance = None

            for item in flat_data:
                match = re.search(ob, item)
                if match:
                    opening_balance = match.group(1)
                    opening_balance = float(opening_balance.replace(',', ''))
                    break

            cb = r'Closing Balance \n([\d,.]+)'
            closing_balance = None

            for item in flat_data:
                match = re.search(cb, item)
                if match:
                    closing_balance = match.group(1)
                    closing_balance = float(closing_balance.replace(',', ''))
                    break

            pattern = r'(\d{2}-\d{2}-\d{4})\s+([\s\S]*?)\n([\d,]+\.\d{2})\n([\d,]+\.\d{2})'
            matches = re.findall(pattern, '\n'.join(flat_data))
            data_list = []
            previous_amount2 = None

            for match in matches:
                date = match[0]
                description = match[1]
                amount1 = match[2]
                amount2 = match[3]

                amount2_numeric = float(amount2.replace(',', ''))

                if previous_amount2 is not None and amount2_numeric < previous_amount2:
                    amount1 = '-' + amount1

                previous_amount2 = amount2_numeric

                data_list.append((date, description, amount1, amount2))

            columns = ["timestamp", "description", "amount", "running_balance"]
            df = pd.DataFrame(data_list, columns=columns)
            df['amount'] = df['amount'].apply(lambda x: float(x.replace(',', '')))
            df['running_balance'] = df['running_balance'].apply(lambda x: float(x.replace(',', '')))
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y')
            print(df)
            if df.loc[0, 'running_balance'] < opening_balance:
                df.loc[0, 'amount'] = -df.loc[0, 'amount']

            json_data = df.to_json(orient='records')
            with open('data_1.json', 'w') as json_file:
                json_file.write(json_data)

            doc.close()

            return json_file  # Indicate success

        except Exception as e:
            return str(e)  # Return the error message if an exception occurs

        
    # def adib_2():
    def cbd_1(self,file_path):
        try:
            pattern = r'^\d{2}/\d{2}/\d{4}'  # Pattern to check if the transaction starts with a date
            
            count = 0
            name = ''
            currency = ''
            acc_type = ''
            iban = ''
            account_number = ''
            branch = ''
            
            doc = fitz.open(file_path)
            output = []
            data_ = []
            prev_balance = 0
            
            for page in doc:
                output += page.get_text("blocks")

            for tup in output:
                trans = tup[4].encode("ascii", errors="ignore").decode()

                # TODO: extracting account details
                if count == 2:
                    if trans.startswith('::\n'):
                        branch = output[count+1][4].replace('\n',',').rstrip(',')
                        name = output[count+2][4].strip().split('\n')[1].strip()
                    else:
                        branch = trans.replace('\n',',').rstrip(',')
                        name = output[count+1][4].strip().split('\n')[1].strip()

                if trans.lower().startswith('acct. no.') and account_number == '':
                    account_number = trans.strip().split('\n')[1].strip()

                if trans.lower().startswith('iban') and iban == '':
                    iban = trans.strip().split('\n')[1].strip()
                    acc_type = trans.strip().split('\n')[-1].strip()

                if trans.strip().lower().startswith('currency') and currency == '':
                    currency = trans.strip().split('\n')[1]
                    if "-" in currency:
                        currency = currency[currency.index('-')+1:].strip()

                if trans.strip().startswith('Balance Brought FWD'):
                    prev_balance = trans.split('\n')[1].replace(',','')

                # TODO: extracting transaction details
                if re.match(pattern, trans):
                    trans_list = trans.split('\n')
                    t_date = trans_list[0]

                    # TODO: extraction of description - number of lines = 1
                    if len(trans_list) == 6:
                        description = trans_list[1]
                        cur_balance = trans_list[4].replace(',','')

                        # check if the transaction is debit or credit
                        if float(cur_balance) > float(prev_balance):
                            amount = trans_list[3]
                        else:
                            amount = '-' + trans_list[3]

                    # TODO: extraction of description - number of lines = 2
                    elif len(trans_list) == 7:
                        description = trans_list[1] + ' ' + trans_list[2]
                        cur_balance = trans_list[5].replace(',','')

                        # check if the transaction is debit or credit
                        if float(cur_balance) > float(prev_balance):
                            amount = trans_list[4]
                        else:
                            amount = '-' + trans_list[4]

                    # TODO: extraction of description - number of lines = 3
                    elif len(trans_list) == 8:
                        description = trans_list[1] + ' ' + trans_list[2] + ' ' + trans_list[3] 
                        cur_balance = trans_list[6].replace(',','')

                        # check if the transaction is debit or credit
                        if float(cur_balance) > float(prev_balance):
                            amount = trans_list[5]
                        else:
                            amount = '-' + trans_list[5]

                    # TODO: extraction of description - number of lines = 4
                    elif len(trans_list) == 9:
                        description = trans_list[1] + ' ' + trans_list[2] + ' ' + trans_list[3] + ' ' + trans_list[4]
                        cur_balance = trans_list[7].replace(',','')

                        # check if the transaction is debit or credit
                        if float(cur_balance) > float(prev_balance):
                            amount = trans_list[6]
                        else:
                            amount = '-' + trans_list[6]

                    # TODO: extraction of description - number of lines = 5
                    elif len(trans_list) == 10:
                        description = trans_list[1] + ' ' + trans_list[2] + ' ' + trans_list[3] + ' ' + trans_list[4] + ' ' + trans_list[5]
                        cur_balance = trans_list[8].replace(',','')

                        # check if the transaction is debit or credit
                        if float(cur_balance) > float(prev_balance):
                            amount = trans_list[7]
                        else:
                            amount = '-' + trans_list[7]

                    obj = {
    #                         'name' : name,
    #                         'currency_code' : currency,
    #                         'type' : acc_type,
    #                         'iban' : iban,
    #                         'account_number' : account_number,
    #                         'bank_name' : 'Commercial Bank of Dubai',
    #                         'branch' : branch,
                            "timestamp": t_date,  # Keep it as a string
                            "description": description,
                            "amount": amount,
                            "running_balance": cur_balance
                        }
                    data_.append(obj)

                    prev_balance = cur_balance

                count += 1

            df2 = pd.DataFrame(data_)
        
            # Convert the timestamp column to datetime
            df["timestamp"] = pd.to_datetime(df["timestamp"], format='%d/%m/%Y')
            df['amount'] = df['amount'].apply(lambda x: float(x.replace(',', '')))
            df['running_balance'] = df['running_balance'].apply(lambda x: float(x.replace(',', '')))
            # Print the JSON
            json_data = json.dumps(data_, indent=4)
            #print("JSON Data:\n", json_data)

            # Print the DataFrame
            print(df)
            return json_data

        except Exception as e:
            return str(e)
        

    # def ei_1():    
    # def fab_1():       
    # def enbd_1():
    def liv_1(self,file_path):
        try:
            doc = fitz.open(file_path)
            output = []
            for page in doc:
                page_output = page.get_text("blocks")  # Get the text blocks for each page
                output.append(page_output)  # Append the page output to the main output list

            plain_text_data = []  # Initialize an empty list to store the plain text

            for page_output in output:
                previous_block_id = 0  # Set a variable to mark the block id
                page_plain_text_data = []  # Initialize an empty list to store the plain text for each page

                for block in page_output:
                    if block[6] == 0:  # We only take the text
                        if previous_block_id != block[5]:  # Compare the block number
                            plain_text = unidecode(block[4])
                            page_plain_text_data.append(plain_text)  # Store the plain text in the list for the current page
                            previous_block_id = block[5]  # Update the previous block id

                # Check if 'Consolidated Statement' is present in the sublist and delete the sublist
                if 'Consolidated Statement\n' in page_plain_text_data:
                    continue  # Skip the current page 
                plain_text_data.append(page_plain_text_data)

            # Initialize variables to store information
            name = None
            address = None
            statement_period = None
            account_balance = None
            account_no = None
            iban = None

            # Iterate through the list and search for the respective information
            for item in plain_text_data[0]:
                if item.startswith('Name :'):
                    name = item.split('Name :')[1].replace('\n', '')
                elif item.startswith('Address :'):
                    address = item.split('Address :')[1].replace('\n', '')
                elif item.startswith('Statement period :'):
                    statement_period = item.split('Statement period :')[1].replace('\n', '')
                elif item.startswith('Account balance :'):
                    account_balance = item.split('Account balance :')[1].replace('\n', '')
                elif item.startswith('AccountNo :'):
                    account_no = item.split('AccountNo :')[1].replace('\n', '')
                elif item.startswith('IBAN :'):
                    iban = item.split('IBAN :')[1].replace('\n', '')

            obj = {
                'name': name,
                'currency_code': 'AED',
                'type': '',
                'iban': iban,
                'account_number': account_no,
                'bank_name': 'LIV by ENBD',
                'branch': '',
                'address': address,
                'account_balance': account_balance
            }

            opening_balance_index = next((i for sublist in plain_text_data for i, text in enumerate(sublist) if text.startswith('IBAN :')), -1)

            if opening_balance_index != -1:
                plain_text_data = plain_text_data[opening_balance_index + 1:]

            plain_text_data = [[element for element in sublist if not element.startswith(('Confirmation of the correctness', 'This statement is generated on', 'Money in'))] for sublist in plain_text_data]
            plain_text_data = list(itertools.chain.from_iterable(plain_text_data))
            plain_text_data = [element.rstrip() for element in plain_text_data]
            plain_text_data = [elem.split('\n') for elem in plain_text_data]

            # Initialize empty lists to store data
            dates = []
            transactions = []
            amounts = []
            balances = []

            # Regex pattern to match date'dd/mm/yyyy'
            date_pattern = r'\d{2}/\d{2}/\d{4}'

            # Initialize a transaction variable to concatenate transaction details
            transaction = ""

            # Iterate through the list
            for item in plain_text_data:
                if re.match(date_pattern, item[0]):
                    # If the item is a date, store it and reset the transaction variable
                    date = item[0]
                    transaction = ""
                else:
                    # Concatenate the elements in the sublist after the date to form the transaction
                    transaction += " ".join(item) + " "

                    # Check if the item contains an amount and balance
                    amount_match = re.search(r'([-+]?\d{1,3}(?:,\d{3})*\.\d+)', item[0])
                    if amount_match:
                        amount = amount_match.group(1).replace(',', '')  # Remove commas
                        balance = item[-1].replace(',', '')  # Remove commas
                        # Append data to respective lists
                        dates.append(pd.to_datetime(date, format='%d/%m/%Y'))
                        transactions.append(transaction.strip())  # Remove trailing spaces
                        amounts.append(pd.to_numeric(amount))
                        balances.append(pd.to_numeric(balance))

            # Create a DataFrame
            df = pd.DataFrame({'timestamp': dates, 'description': transactions, 'amount': amounts, 'running_balance': balances})
            print(df)
            # Input json
            combined_data = {'personal_data': obj, 'transactions': json.loads(df.to_json(orient='records'))}
            combined_json = json.dumps(combined_data, indent=4)

            # Close the PDF document
            doc.close()

            return combined_json

        except Exception as e:
            return str(e)


    # def mashreq_1():    
    # def sib_1():