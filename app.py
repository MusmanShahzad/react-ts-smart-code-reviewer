import textwrap

import streamlit as st


EXAMPLE_TSX = """import React, { useEffect, useState } from "react";

type User = { id: string; name: string };

export function UserSearch({ query }: { query: string }) {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch("/api/users?q=" + query)
      .then((r) => r.json())
      .then((data) => setUsers(data))
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div>
      {loading ? "Loading..." : null}
      <ul>
        {users.map((u, idx) => (
          <li key={idx}>{u.name}</li>
        ))}
      </ul>
    </div>
  );
}
"""


def build_prompt(language: str, context: str, code: str) -> str:
    system_prompt = textwrap.dedent(
        """
        You are a senior TypeScript/React code reviewer with 10+ years experience. Feedback prioritizes correctness > security > maintainability > performance. Always actionable, minimal, and includes missing tests.

        ## Core Principles
        - Correctness first: bugs, type errors, security before optimization
        - Simple > clever: readable > patterns
        - Explicit failures: validate inputs, handle errors/timeouts/fallbacks
        - No silent failures: no empty catches, handle rejections
        - Single responsibility: extract helpers/hooks for complex logic
        - Untrusted input: validate API/query/localStorage at boundaries
        - Minimal changes: no rewrites unless BLOCKER
        - Measurable perf: re-renders, waterfalls, large lists only
        - No secret logging: never tokens/passwords/headers

        If you must assume context, add an "Assumptions" section with at most 3 bullets.

        ## Output Format (MANDATORY — use exactly these headings)

        ### 1) Summary
        1–2 sentences + ✅ Well done: 1 specific strength
        Risk: Safe | Moderate | Risky

        ### 2) Blockers [bug/security/data-loss/crash/type]
        Only true merge blockers.

        ### 3) Important [edge-case/error-handling/perf/a11y/dx/test-gap]
        Should-fix items that reduce production risk and future churn.

        ### 4) Suggestions [readability/refactor/dx]
        Nice-to-have improvements. Keep it short.

        ### 5) Missing tests (checklist)
        Provide 3–10 tests. Each item MUST include:
        - type: unit | component | integration | e2e
        - Given / When / Then
        - Regression prevented (1 line)
        Prefer React Testing Library for components and test behavior (not implementation details).

        ### 6) Minimal patches (unified diff)
        Only changed lines. Multiple small diffs are OK.

        For every item you list in Blockers/Important/Suggestions, include:
        - What/why (1–2 sentences)
        - Smallest safe fix
        - A tag from the section header (e.g., [bug], [perf])

        Minimal patch format (unified diff). Example:
        ```diff
        - old line
        + new line
        ```

        React/TypeScript checklist (use only what applies; don’t dump the list):
        - TypeScript: avoid any; prefer unknown + narrowing; minimize unsafe casts; exhaustive checks for unions; validate external data.
        - React correctness: no side-effects in render; effect deps correct; cleanup/cancellation for async; avoid state update after unmount.
        - Performance: identify unnecessary re-renders (unstable props, inline objects/functions, context value identity); stable list keys (avoid index keys when order can change); virtualization for large lists.
        - Data fetching: avoid waterfalls; dedupe requests; handle loading/error/empty; avoid race conditions.
        - Accessibility/UX: semantic HTML, labels, keyboard/focus, correct ARIA, good empty/loading states.
        - Security: XSS risks (`dangerouslySetInnerHTML`), URL handling/sanitization, no secret logging.

        What NOT to do:
        - Don’t rewrite everything.
        - Don’t add large frameworks/dependencies unless absolutely necessary.
        - Don’t produce long essay-style feedback.
        - Don’t test implementation details; test behavior.
        """
    ).strip()

    user_prompt = textwrap.dedent(
        f"""
        Context:
        - Language/runtime: {language}
        {context.strip() if context.strip() else "- Repo/framework:\\n- Intended behavior:\\n- Constraints (perf, bundle size, compat):\\n- Data sources:\\n- What worries you most:\\n"}

        Code:
        ```text
        {code.rstrip()}
        ```

        Review goals:
        - Prioritize readability/structure/maintainability/performance
        - Call out hidden risks
        - Provide minimal patches
        - Recommend missing tests (checklist with Given/When/Then)
        """
    ).strip()

    return f"{system_prompt}\n\n---\n\n{user_prompt}\n"


st.set_page_config(page_title="Smart Code Reviewer", layout="wide")

st.title("Smart Code Reviewer")
st.caption("Paste TS/React (or any code) → get a ready-to-copy review prompt (no API keys required).")

col1, col2 = st.columns([1, 1])

with col1:
    language = st.selectbox(
        "Language/runtime",
        [
            "JavaScript (Node.js)",
            "TypeScript (Node.js)",
            "TypeScript + React (TSX)",
            "Python",
            "Go",
            "Java",
            "C#",
            "Other",
        ],
    )
    context = st.text_area(
        "Context (optional, recommended)",
        placeholder="- Intended behavior:\n- Constraints (perf, compat, API):\n- Known edge cases:\n",
        height=140,
    )
    code = st.text_area("Code", placeholder="Paste your code here…", height=420)

    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        generate = st.button("Generate prompt", type="primary", use_container_width=True)
    with btn_col2:
        load_example = st.button("Load TSX example", use_container_width=True)
        if load_example:
            code = EXAMPLE_TSX
            language = "TypeScript + React (TSX)"

with col2:
    st.subheader("Copy/paste into your AI reviewer")
    if generate:
        if not code.strip():
            st.error("Please paste some code first.")
        else:
            prompt = build_prompt(language, context, code)
            st.code(prompt, language="markdown")
            st.download_button(
                "Download prompt as .md",
                data=prompt.encode("utf-8"),
                file_name="smart-code-review-prompt.md",
                mime="text/markdown",
                use_container_width=True,
            )
    else:
        st.info("Fill in the left side, then click “Generate prompt”.")

st.divider()
with st.expander("What this is"):
    st.write(
        "A small helper UI that generates a high-signal code review prompt. "
        "Use it with ChatGPT, Claude, Gemini, etc., to get consistent pre-review feedback."
    )

