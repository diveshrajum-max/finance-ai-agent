import pandas as pd

from backend.reconciliation import reconcile
from backend.database import (
    create_database,
    save_transactions,
    get_transactions,
    get_mismatches,
    get_total_discrepancy
)


# Read data

ledger = pd.read_csv(
    "data/ledger.csv"
)

bank = pd.read_csv(
    "data/bank.csv"
)


# Reconcile

result = reconcile(
    ledger,
    bank
)


# Create database

create_database()


# Save results

save_transactions(
    result
)


# Read from SQL database

database_data = get_transactions()


print("\nDATA FROM SQL DATABASE\n")

print(
    database_data[
        [
            "transaction_id",
            "amount_ledger",
            "amount_bank",
            "difference",
            "status"
        ]
    ].to_string(index=False)
)

print("\nMISMATCHES\n")

print(
    get_mismatches().to_string(index=False)
)


print("\nTOTAL DISCREPANCY\n")

print(
    get_total_discrepancy()
)