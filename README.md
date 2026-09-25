# AI-Powered Finance Reconciliation & Reporting Platform

A finance technology application that automates financial reconciliation,
detects transaction discrepancies, stores financial data using SQL, exposes
REST APIs, and provides an AI-powered finance assistant.

## Project Overview

Financial reconciliation is an important finance operation where records from
different sources are compared to identify mismatches, missing transactions,
and discrepancies.

This project automates that process by comparing a company ledger with a bank
statement and generating an interactive financial dashboard.

## Key Features

- Upload CSV or Excel financial files
- Automated ledger-bank reconciliation
- Transaction matching
- Amount mismatch detection
- Missing transaction detection
- Financial discrepancy calculation
- SQLite database storage
- SQL-based financial analysis
- Interactive Streamlit dashboard
- REST API using FastAPI
- Finance AI Assistant
- Financial reports and visualizations

## System Architecture

```text
              CSV / Excel Files
                     |
                     v
            Reconciliation Engine
                     |
                     v
                SQLite DB
                     |
          +----------+----------+
          |                     |
          v                     v
    Streamlit Dashboard     FastAPI REST API
          |
          v
    Finance AI Assistant
