from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io
from backend.database import (
    create_database,
    get_transactions,
    get_mismatches,
    get_total_discrepancy,
    save_transactions
)

from backend.reconciliation import reconcile


app = FastAPI(
    title="Finance Reconciliation API",
    description="REST API for finance reconciliation and reporting",
    version="1.0"
)


# Create database when API starts
create_database()


@app.get("/")
def home():

    return {
        "message": "Finance Reconciliation API is running"
    }


@app.get("/transactions")
def transactions():

    data = get_transactions()

    return data.to_dict(
        orient="records"
    )


@app.get("/mismatches")
def mismatches():

    data = get_mismatches()

    return data.to_dict(
        orient="records"
    )


@app.get("/summary")
def summary():

    data = get_transactions()

    total = len(data)

    matched = (
        data["status"] == "Matched"
    ).sum()

    mismatch = (
        data["status"] == "Amount Mismatch"
    ).sum()

    missing_bank = (
        data["status"] == "Missing in Bank"
    ).sum()

    missing_ledger = (
        data["status"] == "Missing in Ledger"
    ).sum()

    total_discrepancy = get_total_discrepancy()

    if total_discrepancy is None:
        total_discrepancy = 0

    return {

        "total_transactions": int(total),

        "matched": int(matched),

        "amount_mismatches": int(mismatch),

        "missing_in_bank": int(missing_bank),

        "missing_in_ledger": int(missing_ledger),

        "total_discrepancy": float(
            total_discrepancy
        )
    }

@app.post("/reconcile")
async def reconcile_files(
    ledger_file: UploadFile = File(...),
    bank_file: UploadFile = File(...)
):

    # Read uploaded files
    ledger_content = await ledger_file.read()
    bank_content = await bank_file.read()

    # Convert uploaded files into DataFrames
    if ledger_file.filename.endswith(".csv"):
        ledger = pd.read_csv(
            io.BytesIO(ledger_content)
        )
    else:
        ledger = pd.read_excel(
            io.BytesIO(ledger_content)
        )

    if bank_file.filename.endswith(".csv"):
        bank = pd.read_csv(
            io.BytesIO(bank_content)
        )
    else:
        bank = pd.read_excel(
            io.BytesIO(bank_content)
        )

    # Perform reconciliation
    result = reconcile(
        ledger,
        bank
    )

    # Save results to database
    save_transactions(
        result
    )

    # Calculate summary
    total = len(result)

    matched = (
        result["status"] == "Matched"
    ).sum()

    mismatches = (
        result["status"] == "Amount Mismatch"
    ).sum()

    missing_bank = (
        result["status"] == "Missing in Bank"
    ).sum()

    missing_ledger = (
        result["status"] == "Missing in Ledger"
    ).sum()

    total_discrepancy = (
        result.loc[
            result["status"] == "Amount Mismatch",
            "difference"
        ]
        .abs()
        .sum()
    )

    return {
        "message": "Reconciliation completed",

        "total_transactions": int(total),

        "matched": int(matched),

        "amount_mismatches": int(mismatches),

        "missing_in_bank": int(missing_bank),

        "missing_in_ledger": int(missing_ledger),

        "total_discrepancy": float(
            total_discrepancy
        )
    }