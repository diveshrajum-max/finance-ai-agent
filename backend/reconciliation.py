import pandas as pd


def reconcile(ledger, bank):

    result = ledger.merge(
        bank,
        on="transaction_id",
        how="outer",
        suffixes=("_ledger", "_bank"),
        indicator=True
    )

    def get_status(row):

        if row["_merge"] == "left_only":
            return "Missing in Bank"

        if row["_merge"] == "right_only":
            return "Missing in Ledger"

        if row["amount_ledger"] == row["amount_bank"]:
            return "Matched"

        return "Amount Mismatch"

    result["status"] = result.apply(
        get_status,
        axis=1
    )

    result["difference"] = (
        result["amount_bank"].fillna(0)
        - result["amount_ledger"].fillna(0)
    )

    return result