# Smart Code Reviewer (React/TypeScript + Perf + Tests)

Paste TypeScript/React code and get a **ready-to-copy** prompt you can paste into ChatGPT/Claude/Gemini to receive a structured code review:
- Summary
- Blockers / Important / Suggestions
- Missing tests (checklist)
- Minimal patches (unified diff)

## How to use
1) Paste code + optional context in the left panel
2) Click **Generate prompt**
3) Copy the generated prompt into your AI tool
4) Paste the AI’s output into your PR description or as a pre-review checklist

## Notes
- No API keys required (this app generates a strong review prompt).
- Built for React/TypeScript best practices, performance pitfalls, and test coverage gaps.

## Hugging Face Spaces (Docker)
If your Space is created with **SDK = Docker**, ensure the repo includes:
- `Dockerfile`
- `app.py`
- `requirements.txt`
- `README.md`

This repo is Docker-ready and runs Streamlit on `0.0.0.0:7860` (what Spaces expects).

