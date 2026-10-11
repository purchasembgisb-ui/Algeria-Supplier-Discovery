# Algeria Supplier Discovery — Free Search Edition

A browser-friendly Streamlit app for discovering, reviewing, and organizing suppliers, distributors, wholesalers, and manufacturers in Algeria.

## What changed in this edition

- **No paid search API and no API key required.** Search phrases are generated locally and open in Google, Bing, or DuckDuckGo in your browser.
- The app does **not** scrape search-engine result pages or invent demo suppliers. You review search results yourself, then add supplier details or paste public company URLs.
- Manual supplier entry with company, activity, wilaya, phone, business email, website, source URL, notes, and verification status.
- Import supplier records from CSV.
- Collect limited information from permitted public HTML pages after checking `robots.txt`, with a conservative request delay.
- SQLite supplier database, duplicate handling by source URL, and verification statuses.
- Export to CSV, Excel, or Google Sheets.
- Google Sheets export supports Streamlit Cloud secrets (no credentials JSON file needs to be uploaded to GitHub).

## Use in a browser (no local installation required)

1. Create a GitHub repository and upload the project files at the repository root. Include `app.py`, `database.py`, `discovery.py`, `website_collector.py`, `exporters.py`, `requirements.txt`, and this README. Do **not** upload `.env`, database files, service-account JSON keys, or private supplier datasets.
2. Open https://share.streamlit.io/, sign in with GitHub, and create an app using your repository, branch `main`, and main file `app.py`.
3. Deploy. No search API key or search-provider secret is needed.
4. Use **Discover** to open search phrases in your browser, **Add supplier** to enter verified details, or **Import URLs / CSV** to import records or inspect permitted public company pages.
5. Use **Export** to download CSV/Excel or send the records to Google Sheets.

## Google Sheets export setup

1. In Google Cloud Console, create a project and enable **Google Sheets API**.
2. Create a service account. Share your target spreadsheet with the service account's `client_email` as an Editor.
3. For Streamlit Cloud, open your app's **Settings → Secrets** and add the service account JSON fields in TOML form, like this (replace all example values with the values from your downloaded service-account JSON):

   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@your-project-id.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
   ```

4. Copy the spreadsheet ID from its URL. In the app's Export tab, enter the ID and worksheet name, then click **Export to Google Sheets**.

Never commit credentials or private keys to GitHub. Google Cloud may ask you to review service-account key security policies.

## Important database persistence warning

The app uses SQLite in `data/suppliers.db`. This works as a database, but **Streamlit Community Cloud does not guarantee that files written to its local filesystem persist across restarts or redeployments**. Download backups regularly and export to Google Sheets. For a reliable long-term online database, connect the app to an external persistent database (for example, managed PostgreSQL) or build a controlled Google Sheets-backed storage layer before relying on this for important records.

## Collection and verification limits

- Search engine links are opened by you; the app does not automatically harvest search results.
- Public-page collection is limited to the URL(s) you provide; it does not crawl entire websites.
- The collector skips URLs when `robots.txt` disallows access or cannot be checked. Some sites may still prohibit automated collection in their terms.
- Never bypass logins, paywalls, CAPTCHAs, robots rules, or other access controls. Do not collect private data.
- A company website or search result is only a lead. Confirm company identity, contact details, and supplier status before using the record.
- This tool does not validate commercial registration or guarantee complete results. Review applicable Algerian law, privacy/data-protection requirements, and each site's terms before use.

## Dependencies

See `requirements.txt`. No Brave or other paid search API account is required.
