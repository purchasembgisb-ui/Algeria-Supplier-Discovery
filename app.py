import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from database import init_db, list_companies, upsert_companies, export_all
from discovery import build_queries, build_search_links
from website_collector import enrich_url
from exporters import save_csv, save_excel, push_google_sheets

st.set_page_config(page_title="Algeria Supplier Discovery", page_icon="🔎", layout="wide")
DB_PATH = Path("data/suppliers.db")
init_db(DB_PATH)

st.title("Algeria Supplier Discovery")
st.caption("Free supplier research and database for suppliers, distributors, wholesalers, and manufacturers in Algeria.")
st.info("No paid search API is used. Searches open in Google, Bing, or DuckDuckGo in your browser; you choose which supplier leads to save.")

with st.sidebar:
    st.header("Search settings")
    keyword = st.text_input("Product / activity", value="industrial equipment")
    wilaya = st.selectbox("Wilaya", ["All Algeria", "Alger", "Oran", "Constantine", "Sétif", "Blida", "Mostaganem", "Annaba", "Tlemcen", "Béjaïa"])
    language = st.selectbox("Search language", ["French", "Arabic", "French + Arabic"])

# Query links are generated locally and never sent to a paid search API.
tab_search, tab_manual, tab_database, tab_import, tab_export = st.tabs(["Discover", "Add supplier", "Database", "Import URLs / CSV", "Export"])

with tab_search:
    st.subheader("Discover suppliers for free")
    st.write("Choose a search phrase, open a search engine, review the results, and add useful suppliers manually or paste their public website URLs in the import tab.")
    queries = build_queries(keyword, wilaya, language)
    if not queries:
        st.warning("Enter a product or activity in the sidebar.")
    else:
        selected_query = st.selectbox("Search phrase", queries)
        cols = st.columns(3)
        for col, item in zip(cols, build_search_links(selected_query)):
            col.link_button(f"Search with {item['engine']}", item["url"], use_container_width=True)
        with st.expander("Other suggested searches"):
            for query in queries:
                st.markdown(f"**{query}**")
                links = build_search_links(query)
                st.markdown(" · ".join(f"[{x['engine']}]({x['url']})" for x in links))
    st.caption("This tool does not scrape search-engine results. Only save company information you can verify from an accessible source.")

with tab_manual:
    st.subheader("Add a supplier to your database")
    with st.form("manual_supplier_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("Company name *")
            activity = st.text_input("Products / activity", value=keyword)
            company_wilaya = st.selectbox("Wilaya", ["", "Alger", "Oran", "Constantine", "Sétif", "Blida", "Mostaganem", "Annaba", "Tlemcen", "Béjaïa", "Other"])
            phone = st.text_input("Phone")
        with c2:
            email = st.text_input("Business email")
            website = st.text_input("Company website (https://...) ")
            social_url = st.text_input("Official business social page (optional)")
            source_url = st.text_input("Source page URL (optional)")
        notes = st.text_area("Notes / evidence / contact person (optional)")
        verification_status = st.selectbox("Verification status", ["Unverified", "Verified", "Rejected"])
        submitted = st.form_submit_button("Save supplier", type="primary")
        if submitted:
            if not company_name.strip():
                st.error("Company name is required.")
            else:
                record = {
                    "company_name": company_name.strip(), "activity": activity.strip(), "wilaya": company_wilaya,
                    "phone": phone.strip(), "email": email.strip(), "website": website.strip(),
                    "social_url": social_url.strip(), "source_url": source_url.strip() or website.strip(),
                    "source_name": "Manual entry", "evidence": notes.strip(),
                    "verification_status": verification_status,
                    "notes": "Added manually. Verify details before contacting." if not notes.strip() else notes.strip(),
                }
                upsert_companies(DB_PATH, [record])
                st.success("Supplier saved to the database.")

with tab_database:
    st.subheader("Supplier database")
    db = pd.DataFrame(list_companies(DB_PATH))
    if db.empty:
        st.info("Your database is empty. Use Discover, Add supplier, or Import URLs / CSV.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            filter_text = st.text_input("Filter by company, activity, email, or wilaya")
        with c2:
            status = st.selectbox("Verification status", ["All", "Unverified", "Verified", "Rejected"])
        if filter_text:
            mask = db.astype(str).apply(lambda col: col.str.contains(filter_text, case=False, na=False)).any(axis=1)
            db = db[mask]
        if status != "All":
            db = db[db["verification_status"] == status]
        st.dataframe(db, use_container_width=True, hide_index=True)
        st.caption("Records are deduplicated by source URL. Verify each supplier before treating it as a confirmed business.")

with tab_import:
    st.subheader("Import supplier records or collect public URLs")
    uploaded = st.file_uploader("Upload CSV with company_name and/or source_url columns", type=["csv"])
    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded).fillna("")
            st.dataframe(imported.head(20), use_container_width=True)
            if st.button("Import CSV rows"):
                upsert_companies(DB_PATH, imported.to_dict("records"))
                st.success(f"Imported {len(imported)} rows.")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")
    urls_text = st.text_area("Paste public company or directory URLs (one URL per line)")
    if st.button("Collect permitted public pages", type="primary"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.warning("Paste at least one URL first.")
        else:
            rows = []
            progress = st.progress(0)
            for i, url in enumerate(urls):
                try:
                    rows.append(enrich_url(url))
                except Exception as exc:
                    rows.append({"source_url": url, "source_name": "URL import", "notes": f"Collection failed: {exc}", "verification_status": "Unverified"})
                progress.progress((i + 1) / len(urls))
            upsert_companies(DB_PATH, rows)
            st.success(f"Processed {len(rows)} URL(s). Review and verify the records in Database.")

with tab_export:
    st.subheader("Export records")
    all_rows = export_all(DB_PATH)
    df = pd.DataFrame(all_rows)
    if df.empty:
        st.info("Nothing to export yet.")
    else:
        st.download_button("Download CSV", data=save_csv(df), file_name="algeria_suppliers.csv", mime="text/csv")
        st.download_button("Download Excel", data=save_excel(df), file_name="algeria_suppliers.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.markdown("### Optional: Google Sheets export")
        st.write("Create a Google Cloud service account, enable the Google Sheets API, and share your spreadsheet with the service-account email as an Editor. For online deployment, put the credentials in Streamlit App settings → Secrets; never upload the JSON key to GitHub.")
        spreadsheet_id = st.text_input("Google spreadsheet ID", value="")
        worksheet = st.text_input("Worksheet name", value="Suppliers")
        if st.button("Export to Google Sheets"):
            try:
                push_google_sheets(df, spreadsheet_id, worksheet)
                st.success("Export sent to Google Sheets.")
            except Exception as exc:
                st.error(f"Google Sheets export failed: {exc}")

st.divider()
st.caption("Free search workflow; no paid search API. Follow each site's terms, robots.txt, applicable law, and reasonable request limits. Do not collect private or access-restricted data.")
