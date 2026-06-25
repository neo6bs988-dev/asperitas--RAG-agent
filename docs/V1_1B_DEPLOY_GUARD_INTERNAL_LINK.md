# V1.1B Deploy Guard Internal Link

## Scope

This document describes a controlled internal dogfood deployment path for the Streamlit dogfood UI. The page remains dry-run only, has no real answer provider wired, is not public SaaS, and is not production deployment.

Do not enter secrets or sensitive private data.

## Local Run

```powershell
streamlit run apps/internal_dogfood_app.py --server.address 127.0.0.1 --server.port 8501
```

If no access key is configured, the app shows: `Access key not configured; local-only use recommended.`

## Internal Link Deployment Path

Use Streamlit Community Cloud or an equivalent controlled internal demo host.

Deployment notes:

- Use `requirements-streamlit.txt` as the deployment dependency file.
- Configure `ASPERITAS_DOGFOOD_ACCESS_KEY` in the platform secrets/settings.
- Never commit secrets, passwords, tokens, API keys, credentials, or `.streamlit/secrets.toml`.
- Share only as a controlled internal dogfood link for feedback/testing.

## Team Sharing Message

Use this message when sharing the internal link:

```text
This is a controlled internal dogfood link for feedback/testing only.
Dry-run only. No real answer provider is wired.
Do not enter confidential, sensitive, secret, credential, or private data.
Save failure logs only after completing the redaction check.
This is not public SaaS and not production deployment.
```

## Explicit Non-Goals

- No real RAG answer provider.
- No public SaaS.
- No production deployment.
- No autonomous wet-lab claims.
- No clinical, regulatory, or commercial claims.
- No proven bio-model capability claims.

## Behavioral Non-Change Statement

This deploy guard does not change retrieval, chunking, source registry, evaluation fixtures, embeddings, vector database behavior, reranking, answer generation, or default runtime behavior. It does not ingest new sources and does not mutate registry or chunk artifacts.

## Next Step

Deploy controlled internal dogfood link, collect 20-50 tests, then start V1.1C real RAG answer provider.
