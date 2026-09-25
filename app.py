import streamlit as st
import pandas as pd
import plotly.express as px

from backend.reconciliation import reconcile

from backend.database import (
    create_database,
    save_transactions,
    get_transactions,
    get_mismatches,
    get_total_discrepancy
)

from backend.local_ai import finance_assistant

create_database()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Finance Reconciliation Platform",
    page_icon="💰",
    layout="wide"
)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("💰 Finance Reconciliation & Reporting Platform")

st.write(
    "Automated reconciliation, discrepancy detection "
    "and financial reporting."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    ledger_file = st.file_uploader(
        "Upload Company Ledger",
        type=["csv", "xlsx"]
    )

with col2:
    bank_file = st.file_uploader(
        "Upload Bank Statement",
        type=["csv", "xlsx"]
    )


# --------------------------------------------------
# PROCESS FILES
# --------------------------------------------------

if ledger_file and bank_file:

    # Read ledger
    if ledger_file.name.endswith(".csv"):
        ledger = pd.read_csv(ledger_file)
    else:
        ledger = pd.read_excel(ledger_file)

    # Read bank
    if bank_file.name.endswith(".csv"):
        bank = pd.read_csv(bank_file)
    else:
        bank = pd.read_excel(bank_file)


    # Reconcile
    result = reconcile(ledger, bank)

    save_transactions(result)

    result = get_transactions()


    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------

    total = len(result)

    matched = (
        result["status"] == "Matched"
    ).sum()

    mismatch = (
        result["status"] == "Amount Mismatch"
    ).sum()

    missing_bank = (
        result["status"] == "Missing in Bank"
    ).sum()

    missing_ledger = (
        result["status"] == "Missing in Ledger"
    ).sum()


    match_rate = (
        matched / total * 100
        if total > 0
        else 0
    )


    # Total discrepancy
    total_discrepancy = get_total_discrepancy()

    if pd.isna(total_discrepancy):
        total_discrepancy = 0


    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    st.divider()

    st.subheader("📊 Reconciliation Overview")


    # KPI ROW 1
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Transactions",
        total
    )

    col2.metric(
        "Matched",
        matched
    )

    col3.metric(
        "Match Rate",
        f"{match_rate:.1f}%"
    )

    col4.metric(
        "Amount Mismatches",
        mismatch
    )

    col5.metric(
        "Total Discrepancy",
        f"₹{total_discrepancy:,.2f}"
    )


    # --------------------------------------------------
    # STATUS CHART
    # --------------------------------------------------

    st.subheader("Transaction Status")

    status_counts = (
        result["status"]
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Count"
    ]


    fig_status = px.bar(
        status_counts,
        x="Count",
        y="Status",
        orientation="h",
        title="Reconciliation Status"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )


    # --------------------------------------------------
    # DISCREPANCY ANALYSIS
    # --------------------------------------------------

    st.subheader("⚠️ Discrepancy Analysis")


    mismatches = get_mismatches()


    if len(mismatches) > 0:

        mismatches[
            "absolute_difference"
        ] = mismatches[
            "difference"
        ].abs()


        top_mismatches = (
            mismatches
            .sort_values(
                "absolute_difference",
                ascending=False
            )
            .head(10)
        )


        fig_mismatch = px.bar(
            top_mismatches,
            x="absolute_difference",
            y="transaction_id",
            orientation="h",
            title="Largest Transaction Discrepancies",
            labels={
                "absolute_difference":
                "Difference (₹)"
            }
        )


        st.plotly_chart(
            fig_mismatch,
            use_container_width=True
        )

    else:

        st.success(
            "No amount mismatches found."
        )


    # --------------------------------------------------
    # CATEGORY ANALYSIS
    # --------------------------------------------------

    st.subheader("📁 Category Analysis")


    if "category_ledger" in result.columns:

        category_summary = (
            result
            .groupby("category_ledger")
            ["amount_ledger"]
            .sum()
            .reset_index()
        )


        category_summary.columns = [
            "Category",
            "Ledger Amount"
        ]


        fig_category = px.bar(
            category_summary,
            x="Ledger Amount",
            y="Category",
            orientation="h",
            title="Ledger Amount by Category"
        )


        st.plotly_chart(
            fig_category,
            use_container_width=True
        )


    # --------------------------------------------------
    # TRANSACTION DETAILS
    # --------------------------------------------------

    st.subheader("📋 Transaction Details")


    display_columns = [
        "transaction_id",
        "date_ledger",
        "description_ledger",
        "amount_ledger",
        "amount_bank",
        "difference",
        "status"
    ]


    st.dataframe(
        result[display_columns],
        use_container_width=True
    )


    # --------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------

    st.subheader("📥 Download Report")


    csv_data = result.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="Download Reconciliation Report",
        data=csv_data,
        file_name="reconciliation_report.csv",
        mime="text/csv"
    )

    # ==========================================
# AI FINANCE ASSISTANT
# ==========================================

st.markdown("---")

st.header("🤖 AI Finance Assistant")

st.write(
    "Ask questions about your financial reconciliation data."
)

question = st.text_input(
    "Ask a finance question:",
    placeholder="Example: What is the total discrepancy?"
)

if st.button("Ask AI"):

    if question.strip():

        answer = finance_assistant(question)

        st.markdown("### AI Response")

        st.write(answer)

    else:

        st.warning("Please enter a question.")