import sqlite3
from Account import signed_in_account
from Ledger import get_ledger_data

##############################################################################################################################################################

def get_path():
    return "User\\"+ signed_in_account() + "\\Trial Balance.db"

def create_trial_balance():
    all_ledgers = get_ledger_data()
    
    db = sqlite3.connect(get_path())
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trial_balance (
            account TEXT PRIMARY KEY,
            debit REAL,
            credit REAL
        )
    ''')

    cursor.execute('DELETE FROM trial_balance')

    for account, entries in all_ledgers.items():
        debit_sum = sum(amount for _, _, amount, type in entries if type == 'debit')
        credit_sum = sum(amount for _, _, amount, type in entries if type == 'credit')
        
        if debit_sum > credit_sum:
            amt = debit_sum - credit_sum
            cursor.execute(''' INSERT INTO trial_balance (account, debit, credit) VALUES (?, ?, ?) ''', (account, amt, 0))
        elif credit_sum > debit_sum:
            amt = credit_sum - debit_sum
            cursor.execute(''' INSERT INTO trial_balance (account, debit, credit) VALUES (?, ?, ?) ''', (account, 0, amt))

    db.commit()
    db.close()

def get_trial_balance():
    create_trial_balance()
    db = sqlite3.connect(get_path())
    cursor = db.cursor()

    cursor.execute('SELECT * FROM trial_balance')
    trial_balance_data = cursor.fetchall()

    db.close()
    return trial_balance_data
