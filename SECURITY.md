# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in this project, **please do not open a public issue**. Instead, report it privately:

- **Email:** abhinaykrupa@gmail.com — subject line: `[SECURITY] vertical-procurement-toolkit`
- **GitHub:** use [private security advisories](https://github.com/abhinaykrupa/vertical-procurement-toolkit/security/advisories/new)

Please include:
- A description of the issue and where it lives in the code
- Steps to reproduce
- The impact you believe it has
- Any suggested fix you've identified

I aim to acknowledge reports within **3 business days** and provide a remediation timeline within **10 business days**.

## Scope

This toolkit is a reference architecture intended to be embedded in larger systems. Within this scope:

**In scope** — please report:
- Code execution via crafted CSV input (e.g. through pandas, YAML, or the matcher)
- Path traversal or arbitrary-file-read via the CLI / adapters
- Prompt injection in the real LLM judge (`vpt/llm_judge.py`) that exfiltrates data or breaks structured output
- Dependency vulnerabilities directly exploitable through the documented entry points

**Out of scope** — won't be treated as vulnerabilities:
- The mock Stripe/HubSpot data in `app/sync/` (it's deliberately fabricated for demo)
- Lack of authentication in the Streamlit demo (it's a POC, see `SECURITY_REVIEW.md`)
- Mocked LLM judge behavior — this is a development-time stub, not production
- Recommendations to "use environment variables for keys" — already documented

## Production deployments

If you embed this toolkit in a production system, the burden of additional hardening is on you. Start with:

- Read `SECURITY_REVIEW.md` for a full POC-vs-production security gap analysis
- Read `PRODUCTION_ARCHITECTURE.md` for the recommended production swap-ins (pgvector, real LLM, auth, audit log)
- Add input size limits before passing user files to adapters
- Run the LLM judge with structured output enforcement (already on for OpenAI provider)
- Treat any catalog data as sensitive — it represents negotiated commercial terms
