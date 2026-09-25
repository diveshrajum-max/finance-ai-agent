import sqlite3
import pandas as pd


DATABASE = "finance.db"


def create_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (

            transaction_id TEXT PRIMARY KEY,

            date_ledger TEXT,

            description_ledger TEXT,

            category_ledger TEXT,

            amount_ledger REAL,

            amount_bank REAL,

            difference REAL,

            status TEXT
        )
    """)

    conn.commit()

    conn.close()


def save_transactions(data):

    conn = sqlite3.connect(DATABASE)

    data_to_save = data[
        [
            "transaction_id",
            "date_ledger",
            "description_ledger",
            "category_ledger",
            "amount_ledger",
            "amount_bank",
            "difference",
            "status"
        ]
    ]

    data_to_save.to_sql(
        "transactions",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def get_transactions():

    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT *
        FROM transactions
    """

    data = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return data

def get_mismatches():

    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT
            transaction_id,
            amount_ledger,
            amount_bank,
            difference,
            status
        FROM transactions
        WHERE status = 'Amount Mismatch'
        ORDER BY ABS(difference) DESC
    """

    data = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return data

def get_total_discrepancy():

    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT
            SUM(ABS(difference))
        AS total_discrepancy

        FROM transactions

        WHERE status = 'Amount Mismatch'
    """

    result = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return result.iloc[0]["total_discrepancy"]

def get_transaction(transaction_id):
    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT *
        FROM transactions
        WHERE transaction_id = ?
    """

    data = pd.read_sql_query(
        query,
        conn,
        params=(transaction_id,)
    )

    conn.close()

    return data


def get_large_mismatches(threshold):
    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT
            transaction_id,
            amount_ledger,
            amount_bank,
            difference,
            status
        FROM transactions
        WHERE status = 'Amount Mismatch'
        AND ABS(difference) >= ?
        ORDER BY ABS(difference) DESC
    """

    data = pd.read_sql_query(
        query,
        conn,
        params=(threshold,)
    )

    conn.close()

    return data