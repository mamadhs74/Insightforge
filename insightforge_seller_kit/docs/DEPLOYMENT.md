# Deployment Guide

## Local use

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Push the project to a private GitHub repository.
2. Connect the repository in Streamlit Community Cloud.
3. Set `app.py` as the entry point.
4. Deploy.

## Docker-style deployment idea

For production, deploy behind a reverse proxy and add authentication. The current edition is designed as a self-hosted local/internal tool.

Recommended hosted additions before SaaS launch:

- authentication
- file-size limits
- upload deletion policy
- database history
- user workspaces
- payment system
- privacy policy
- terms of service
