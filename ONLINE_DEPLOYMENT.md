# Browser-only deployment (no installation on your work PC)

1. Create/sign in to GitHub in your browser and create a repository.
2. Upload the project files at the repository root. Do not upload `.env`, database files, service-account JSON keys, or private datasets.
3. Visit https://share.streamlit.io/, sign in with GitHub, choose **Create app**, select your repository, branch `main`, and main file `app.py`.
4. Deploy. Supplier searches do not need an API key or paid search service.
5. To export to Google Sheets, configure `[gcp_service_account]` in Streamlit App settings → Secrets using the example in `README.md` and share the spreadsheet with the service-account email.

## Important

The app uses SQLite. Streamlit Community Cloud does not guarantee local-file persistence across restarts or redeployments. Export CSV/Excel backups and/or Google Sheets regularly. For important long-term records, configure a persistent external database before relying on the hosted app as the only copy.
