from io import BytesIO
import os
import pandas as pd


def save_csv(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def save_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Suppliers")
    return buffer.getvalue()


def _google_credentials():
    """Use a local credentials JSON path or Streamlit Cloud secrets."""
    credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if credentials_file:
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        return Credentials.from_service_account_file(credentials_file, scopes=scopes)

    try:
        import streamlit as st
        service_account_info = st.secrets.get("gcp_service_account", None)
        if service_account_info:
            from google.oauth2.service_account import Credentials
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            return Credentials.from_service_account_info(dict(service_account_info), scopes=scopes)
    except Exception:
        pass
    return None


def push_google_sheets(df, spreadsheet_id, worksheet_name):
    if not spreadsheet_id.strip():
        raise ValueError("Enter a Google spreadsheet ID.")
    credentials = _google_credentials()
    if credentials is None:
        raise ValueError(
            "Google credentials are not configured. On Streamlit Cloud, add a [gcp_service_account] "
            "section to App settings → Secrets. See README.md for the fields and setup steps."
        )
    import gspread
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=max(1000, len(df) + 1), cols=max(20, len(df.columns)))
    worksheet.clear()
    values = [df.columns.astype(str).tolist()] + df.fillna("").astype(str).values.tolist()
    worksheet.update(values, value_input_option="RAW")
