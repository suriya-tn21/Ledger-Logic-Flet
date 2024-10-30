import sqlite3
import pandas as pd

from Account import signed_in_account
from Journal import all_journals, all_accounts

##############################################################################################################################################################

def get_path():
    return "User\\"+ signed_in_account() + "\\Ledger.db"

def create_ledgers():
    all_jours = all_journals()
    all_acc = all_accounts()
    
    if not all_jours or not all_acc:
        return  # If there are no journals or accounts, exit the function

    db = sqlite3.connect(get_path())
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Remove all existing tables
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}"')

    for account in all_acc:                # Creating tables for all the accounts
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{account}" (
                date TEXT NOT NULL,
                particulars TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL
            )
        ''')

    for journal in all_jours:                # Converting the journals into ledgers
        sno, date, debit_account, credit_account, amount, narration = journal[:6]
        cursor.execute(f'''INSERT INTO "{debit_account}" (date, particulars, amount, type) VALUES (?, ?, ?, 'debit')''', (date, credit_account, amount))
        cursor.execute(f'''INSERT INTO "{credit_account}" (date, particulars, amount, type) VALUES (?, ?, ?, 'credit')''', (date, debit_account, amount))

    db.commit()
    db.close()

def get_ledger_data():
    create_ledgers()
    db = sqlite3.connect(get_path())
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    ledger_data = {}
    
    for table in tables:
        account_name = table[0]
        cursor.execute(f'SELECT * FROM "{account_name}"')
        ledger_data[account_name] = cursor.fetchall()

    db.close()
    return ledger_data

def get_ledger_format():
    ledger_data = get_ledger_data()
    ledger_dict = {}
    if ledger_data:
        accounts = list(ledger_data.keys())

        for i, acc in enumerate(accounts):
            debit_entries = []
            debit_total = 0
            credit_entries = []
            credit_total = 0
            max_rows = 0

            for entry in ledger_data[acc]:
                if entry[3] == 'debit':
                    debit_entries.append([entry[0], f"To {entry[1]}", f"{entry[2]:.2f}"])
                    debit_total += entry[2]
                else:
                    credit_entries.append([entry[0], f"By {entry[1]}", f"{entry[2]:.2f}"])
                    credit_total += entry[2]

            balance = debit_total - credit_total
            if debit_total > credit_total:
                credit_entries.append(["", "By Balance c/d", f"{balance:.2f}"])  
            elif credit_total > debit_total:
                debit_entries.append(["", "To Balance c/d", f"{-balance:.2f}"])

            total_row = ["Total", "", f"{debit_total:.2f}", "", "Total", "", f"{credit_total:.2f}"]
            
            # Ensure that the total rows are added correctly
            max_rows = max(len(debit_entries), len(credit_entries))
            debit_entries += [["", "", ""]] * (max_rows - len(debit_entries))
            credit_entries += [["", "", ""]] * (max_rows - len(credit_entries))


            t_ledger_table = [
                debit_entries[i] + [""] + credit_entries[i]
                for i in range(max_rows)
            ]
            t_ledger_table.append(total_row)
            table = pd.DataFrame(
                t_ledger_table,
                columns=["Debit Date", "Debit Particulars", "Debit Amount", "", "Credit Date", "Credit Particulars", "Credit Amount"]
            )

            ledger_dict[acc] = table

    return ledger_dict
    