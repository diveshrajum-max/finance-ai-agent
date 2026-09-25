import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.database import (
    get_transactions,
    get_mismatches,
    get_total_discrepancy,
    get_transaction,
    get_large_mismatches
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# -----------------------------
# Database tools
# -----------------------------

def transactions_tool():
    data = get_transactions()
    return data.to_dict(orient="records")


def mismatches_tool():
    data = get_mismatches()
    return data.to_dict(orient="records")


def total_discrepancy_tool():
    value = get_total_discrepancy()

    if value is None:
        value = 0

    return float(value)


def transaction_tool(transaction_id):
    data = get_transaction(transaction_id)
    return data.to_dict(orient="records")


def large_mismatches_tool(threshold):
    data = get_large_mismatches(threshold)
    return data.to_dict(orient="records")


# -----------------------------
# Tool definitions for AI
# -----------------------------

tools = [
    {
        "type": "function",
        "name": "get_transactions",
        "description": "Get all reconciled financial transactions from the database.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },

    {
        "type": "function",
        "name": "get_mismatches",
        "description": "Get all transactions where the ledger and bank amounts do not match.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },

    {
        "type": "function",
        "name": "get_total_discrepancy",
        "description": "Get the total absolute financial discrepancy.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },

    {
        "type": "function",
        "name": "get_transaction",
        "description": "Get details of a specific transaction using its transaction ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "Transaction ID such as T002"
                }
            },
            "required": ["transaction_id"],
            "additionalProperties": False
        }
    },

    {
        "type": "function",
        "name": "get_large_mismatches",
        "description": "Get mismatched transactions whose absolute discrepancy is greater than or equal to a specified amount.",
        "parameters": {
            "type": "object",
            "properties": {
                "threshold": {
                    "type": "number",
                    "description": "Minimum discrepancy amount in rupees"
                }
            },
            "required": ["threshold"],
            "additionalProperties": False
        }
    }
]


# -----------------------------
# AI Agent
# -----------------------------

def ask_finance_ai(question):

    response = client.responses.create(
        model="gpt-5-mini",

        instructions="""
        You are a Finance AI Assistant.

        You help users analyze financial reconciliation data.

        Always use the available database tools when the user asks
        about actual transactions, discrepancies, mismatches,
        amounts, or financial records.

        Never invent financial data.

        Explain financial results clearly and concisely.
        Amounts are in Indian Rupees (₹).
        """,

        input=question,

        tools=tools
    )

    # Process tool calls
    while True:

        tool_outputs = []

        for item in response.output:

            if item.type != "function_call":
                continue

            arguments = json.loads(item.arguments)

            if item.name == "get_transactions":
                result = transactions_tool()

            elif item.name == "get_mismatches":
                result = mismatches_tool()

            elif item.name == "get_total_discrepancy":
                result = total_discrepancy_tool()

            elif item.name == "get_transaction":
                result = transaction_tool(
                    arguments["transaction_id"]
                )

            elif item.name == "get_large_mismatches":
                result = large_mismatches_tool(
                    arguments["threshold"]
                )

            else:
                result = {"error": "Unknown tool"}

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                }
            )

        if not tool_outputs:
            return response.output_text

        response = client.responses.create(
            model="gpt-5-mini",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools
        )


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    question = input("Ask a finance question: ")

    answer = ask_finance_ai(question)

    print("\nAI:")
    print(answer)