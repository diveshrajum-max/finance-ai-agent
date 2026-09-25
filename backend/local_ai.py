from backend.database import (
    get_transactions,
    get_mismatches,
    get_total_discrepancy,
    get_transaction,
    get_large_mismatches
)


def finance_assistant(question):

    q = question.lower().strip()

    # -----------------------------
    # Total discrepancy
    # -----------------------------

    if "total discrepancy" in q or "total difference" in q:

        total = get_total_discrepancy()

        if total is None:
            total = 0

        return f"The total financial discrepancy is ₹{total:,.2f}."


    # -----------------------------
    # Mismatches
    # -----------------------------

    if "mismatch" in q or "discrepancies" in q:

        data = get_mismatches()

        if data.empty:
            return "There are no amount mismatches."

        answer = "The following transactions have amount mismatches:\n\n"

        for _, row in data.iterrows():

            answer += (
                f"• {row['transaction_id']}: "
                f"Ledger ₹{row['amount_ledger']:,.2f}, "
                f"Bank ₹{row['amount_bank']:,.2f}, "
                f"Difference ₹{abs(row['difference']):,.2f}\n"
            )

        return answer


    # -----------------------------
    # Specific transaction
    # -----------------------------

    words = question.upper().split()

    for word in words:

        if word.startswith("T") and word[1:].isdigit():

            transaction_id = word

            data = get_transaction(transaction_id)

            if data.empty:
                return f"I could not find transaction {transaction_id}."

            row = data.iloc[0]

            status = row["status"]

            if status == "Matched":

                return (
                    f"Transaction {transaction_id} is matched. "
                    f"The ledger and bank amounts are both "
                    f"₹{row['amount_ledger']:,.2f}."
                )

            if status == "Amount Mismatch":

                return (
                    f"Transaction {transaction_id} has an amount mismatch. "
                    f"The ledger amount is ₹{row['amount_ledger']:,.2f}, "
                    f"while the bank amount is ₹{row['amount_bank']:,.2f}. "
                    f"The difference is ₹{abs(row['difference']):,.2f}."
                )

            return (
                f"Transaction {transaction_id} has status: {status}."
            )


    # -----------------------------
    # Large mismatches
    # -----------------------------

    if "above" in q or "over" in q or "greater than" in q:

        import re

        numbers = re.findall(r"\d+(?:,\d+)*(?:\.\d+)?", q)

        if numbers:

            threshold = float(numbers[-1].replace(",", ""))

            data = get_large_mismatches(threshold)

            if data.empty:
                return (
                    f"There are no mismatches greater than "
                    f"or equal to ₹{threshold:,.2f}."
                )

            answer = (
                f"Mismatches greater than or equal to "
                f"₹{threshold:,.2f}:\n\n"
            )

            for _, row in data.iterrows():

                answer += (
                    f"• {row['transaction_id']} — "
                    f"₹{abs(row['difference']):,.2f}\n"
                )

            return answer


    # -----------------------------
    # Number of transactions
    # -----------------------------

    if "how many" in q and "transaction" in q:

        data = get_transactions()

        return f"There are {len(data)} transactions in the database."


    # -----------------------------
    # Matched transactions
    # -----------------------------

    if "matched" in q:

        data = get_transactions()

        matched = (data["status"] == "Matched").sum()

        return f"There are {matched} matched transactions."


    return (
        "I can help you analyze the finance database. "
        "Try asking:\n\n"
        "• What is the total discrepancy?\n"
        "• Show me the mismatches.\n"
        "• Explain T002.\n"
        "• Which transactions have discrepancies above 1000?\n"
        "• How many transactions are matched?"
    )