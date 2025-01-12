import google.generativeai as genai
import json
from Account import signed_in_account

genai.configure(api_key = "AIzaSyACtt2wK19nlEVYcBhN8-5F9wwDYzarNB0")
model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat()

prerequisite_info = """Journal
A general journal is a daybook or subsidiary journal in which transactions relating to adjustment entries, opening stock, depreciation, accounting errors etc. are recorded. The source documents for general journal entries may be journal vouchers, copies of management reports and invoices. Journals are prime entry books, and may also be referred to as books of original entry, from when transactions were written in a journal before they were manually posted to accounts in the general ledger or a subsidiary ledger.
It is where double-entry bookkeeping entries are recorded by debiting one or more accounts and crediting another one or more accounts with the same total amount. The total amount debited and the total amount credited should always be equal, thereby ensuring the accounting equation is maintained.
In manual accounting information systems, a variety of special journals may be used, such as a sales journal, purchase journal, cash receipts journal, disbursement journal, and a general journal. The transactions recorded in a general journal are those that do not qualify for entry in any special journal used by the organisation, such as non-routine or adjusting entries.

A general journal entry is a record of financial transactions in order by date. A general journal entry would typically include the date of the transaction, the names of the accounts to be debited and credited, the amount of each debit and credit, and a summary explanation of the transaction, commonly known as a narration. Each debit and credit account and the narration would be entered on consecutive lines, and typically at least one line would be left blank before the next journal entry, and entries should not be split over more than one page. There may be multiple debit or credit entries, but the sum of the debits must be equal to the sum of the credits. For example, multiple expenses (debits) may be paid with one payment (a credit).

Debit/Credit
Debits and credits in double-entry bookkeeping are entries made in account ledgers to record changes in value resulting from business transactions. A debit entry in an account represents a transfer of value to that account, and a credit entry represents a transfer from the account. Each transaction transfers value from credited accounts to debited accounts.
Indicating Debits with the suffix "Dr" or writing them plain, and indicating credits with the suffix "Cr".
Whether a debit increases or decreases an account's net balance depends on what kind of account it is. The basic principle is that the account receiving benefit is debited, while the account giving benefit is credited. For instance, an increase in an asset account is a debit. An increase in a liability or an equity account is a credit.
Three golden rules, one for each type of account:
Real accounts: Debit whatever comes in and credit whatever goes out.
Personal accounts: Receiver's account is debited and giver's account is credited.
Nominal accounts: Expenses and losses are debited and incomes and gains are credited.

In accounting terms, assets are recorded on the left side (debit) of asset accounts, because they are typically shown on the left side of the accounting equation (A=L+SE). Likewise, an increase in liabilities and shareholder's equity are recorded on the right side (credit) of those accounts, thus they also maintain the balance of the accounting equation. In other words, if "assets are increased with left side entries, the accounting equation is balanced only if increases in liabilities and shareholder’s equity are recorded on the opposite or right side. Conversely, decreases in assets are recorded on the right side of asset accounts, and decreases in liabilities and equities are recorded on the left side". Similar is the case with revenues and expenses, what increases shareholder's equity is recorded as credit because they are on the right side of the equation and vice versa.

Double-entry bookkeeping
Double-entry bookkeeping, also known as double-entry accounting, is a method of bookkeeping that relies on a two-sided accounting entry to maintain financial information. Every entry to an account requires a corresponding and opposite entry to a different account. The double-entry system has two equal and corresponding sides, known as debit and credit; this is based on the fundamental accounting principle that for every debit, there must be an equal and opposite credit. A transaction in double-entry bookkeeping always affects at least two accounts, always includes at least one debit and one credit, and always has total debits and total credits that are equal. The purpose of double-entry bookkeeping is to allow the detection of financial errors and fraud. Double-entry bookkeeping is based on "balancing" the books, that is to say, satisfying the accounting equation. The accounting equation serves as an error detection tool; if at any point the sum of debits for all accounts does not equal the corresponding sum of credits for all accounts, an error has occurred. 

Ledger
A ledger is a book or collection of accounts in which accounting transactions are recorded. Each account has:
An opening or brought-forward balance
A list of transactions, each recorded as either a debit or credit in separate columns
An ending or closing, or carry-forward, balance.
The ledger is a permanent summary of all amounts entered in supporting journals (day books) which list individual transactions by date. Usually every transaction, or a total of a series of transactions, flows from a journal to one or more ledgers. Depending on the company's bookkeeping procedures, all journals may be totaled and the totals posted to the relevant ledger each month. At the end of the accounting period, the company's financial statements are generated from summary totals in the ledgers. For every debit recorded in a ledger, there must be a corresponding credit, so that overall the total debits equal the total credits. 

Trial Balance
A trial balance is an internal financial statement that lists the adjusted closing balances of all the general ledger accounts (both revenue and capital) contained in the ledger of a business as at a specific date. This list will contain the name of each nominal ledger account in the order of liquidity and the value of that nominal ledger balance. Each nominal ledger account will hold either a debit balance or a credit balance. The debit balance values will be listed in the debit column of the trial balance and the credit value balance will be listed in the credit column. The trading profit and loss statement and balance sheet and other financial reports can then be produced using the ledger accounts listed on the same balance. The primary purpose of preparing a trial balance is to ensure the accuracy of an entity's double-entry bookkeeping system. Accounting equation rule states that there must be equal debit and credit for every financial transaction, therefore, the value of all the debit and credit balances on trial balance must be equal. If the total of the debit column does not equal the total value of the credit column then this would show that there is an error in the nominal ledger accounts. This error must be found before a profit and loss statement and balance sheet can be produced. Hence trial balance is important in case of adjustments. Whenever any adjustment is performed run trial balance and confirm if all the debit amount is equal to credit amount.

Profit and Loss A/c
An income statement or profit and loss account is one of the financial statements of a company and shows the company's revenues and expenses during a particular period. It indicates how the revenues are transformed into the net income or net profit (the result after all revenues and expenses have been accounted for). The purpose of the income statement is to show managers and investors whether the company made profit or loss during the period being reported. Income statements may help investors and creditors determine the past financial performance of the enterprise, predict the future performance, and assess the capability of generating future cash flows using the report of income and expenses. It is very important for the business.

Balance Sheet
In accounting, a balance sheet is a summary of the financial balances of an individual or organisation, whether it be a sole proprietorship, a business partnership, a corporation, private limited company or other organisation such as a government or not-for-profit entity. Another way to look at the balance sheet equation is that total assets equals liabilities plus owner's equity.


You are an accounting assistant. You will not answer any questions outside of your expertise. If asked reply with "That is out of my field to answer". Your job is to assist the user with any and all enquires about anything related to accounting and finance. 

Your Name is Gemini Assistant.
"""

try:
    chat.send_message(prerequisite_info)
except:
    pass

def ask(question):
    response = chat.send_message(question)
    add_chat_history(question, response.text)
    return response.text

def add_chat_history(question, answer):
    entry = {
        "question": question,
        "answer": answer
    }
    
    try:
        with open("User\\" + signed_in_account() + "\\Gemini_Chat_History.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(entry)

    with open("User\\" + signed_in_account() + "\\Gemini_Chat_History.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def get_history():
    try:
        with open("User\\" + signed_in_account() + "\\Gemini_Chat_History.json", "r", encoding="utf-8") as f:
            history = json.load(f)
            formatted_history = []
            for entry in history:
                formatted_history.append(f"You: {entry['question']}")
                formatted_history.append(f"AI: {entry['answer']}")
            return formatted_history
    except FileNotFoundError:
        return "No History"
