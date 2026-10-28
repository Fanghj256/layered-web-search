# Layered Web Search Strategy

> A web-research methodology for AI agents: **knows how deep to search, degrades gracefully, and knows what to leave to humans.**

English | [中文](README.md)

This repo contains two installable files (rules + skill) and a complete setup guide that make your agent research the web with discipline instead of "search once and make things up".

Works with ZCode (verified on ZCode 3.x), Claude Code, Cursor, and any client supporting `AGENTS.md` / `CLAUDE.md` and Skills.

---

## What problem it solves

Without this setup, agents typically:

- **Conclude after a single search** — treating snippets as facts, inventing numbers, dates, and document IDs
- **Skip verification when they should search** — fabricating "plausible" citations and figures
- **Over-research trivial lookups / under-research important ones** — five search rounds for one fact, one search for something that goes into a document
- **Answer evaluative questions with unearned confidence** — AI cannot judge "is it worth using" for you, yet gives a definitive answer

This strategy addresses all four with **judgment rules + a tiered workflow + human-AI division of labor**.

---

## Core design

### 1. Four-tier degradation chain (ordered by acquisition cost)

| Tier | Tool | What you get | When to escalate |
|---|---|---|---|
| ① Coarse search | Exa `web_search_exa` | Leads + snippets | Snippets are insufficient |
| ② Full text | Exa `web_fetch_exa` | Body text (numbers, document IDs, dates) | Fetch fails (JS-rendered / anti-bot / login wall) |
| ③ Browser fallback | ③a `ego-browser`: needs login state / known site<br>③b `playwright-cli`: untrusted source / needs isolation | Rendered page content | — |
| ④ Site-specific channel | `gh` CLI / `curl` / dedicated APIs | Code, structured data | — |

**Principle: use the lightest tool that works.** You do not run all four tiers for every task — a single-fact lookup should stop at tier ①.

### 2. Verification tiers

- **Light check**: single fact, one authoritative source → one search + source verification, done
- **Full workflow**: content for external use / making judgments / deadlines · quotas · fees / conflicting sources / citing literature → run the full `web-research` skill

### 3. Human-AI division of labor (the most overlooked part)

| Need | Who | Why |
|---|---|---|
| Deterministic, verifiable (e.g. "the document number of regulation X") | AI search | Clear answer; retrieval + aggregation is efficient |
| Evaluative ("is it worth using") | Human: read issues, commits | LLMs get swayed by confident marketing |
| Exploratory (finding people, inspiration, benchmarks) | Human: forum highlights, user history | Depends on "a person's track record"; AI search is not good at it yet |

### 4. Output discipline

- Every conclusion carries a source link
- Labeled 「confirmed / unconfirmed / freshness unknown」(已证实 / 未证实 / 时效未知)
- Conflicting sources are flagged, not silently reconciled
- The user's explicit format requirements in the current message override default presentation preferences (conflict adjudication)

### 5. Why the browser fallback is split into two tools

The test is one question: **is this page worth opening with your real identity?**

|  | ③a `ego-browser` | ③b `playwright-cli` |
|---|---|---|
| What it is | The Chromium browser you use day to day; the agent attaches to the same instance | Playwright driven from the command line |
| Default profile | Yours — cookies and login state already there | In memory, wiped when the browser closes |
| Default visibility | A real window you can watch and take over | Headless, no trace left by default |
| Use it when | Known sites, pages behind a login, or cases where you must clear a captcha or scan a QR code yourself | Unknown links, short links, pages used once |
| Avoid it when | Opening an untrusted page — it runs under your real accounts | Pages that need login — you would re-authenticate every time |

They are not merged because their defaults point in opposite directions: ego defaults to "carry your identity", playwright-cli defaults to "carry none". One tool doing both would have to give ground on one side — either re-login inside a throwaway container, or open untrusted pages in your real session.

One more reason that is easy to miss: **tier ③ is the only channel that can borrow your own network position.** Search and fetch APIs such as Exa run on their own servers; your proxy, intranet or corporate VPN has no effect on what they can reach. ego and playwright-cli run locally, so they can open exactly what you can open. This tier is therefore not only an anti-bot fallback but also a "reach the page from my network" fallback.

**Why CLI rather than Playwright MCP**: MCP tool schemas sit in context every turn, while the browser fallback is a low-frequency operation; a CLI costs nothing until it is actually invoked, and is headless and trace-free by default. The MCP version also works if that is what you have — same capabilities, minus the constant schema overhead.

---

## Workflow

```text
User question
  │
  ├─ ① Judge (AGENTS.md: five questions + seven categories)
  │     ├─ No web needed → answer directly
  │     ├─ Evaluative / exploratory → suggest human search
  │     └─ Factual → continue
  │
  ├─ ② Tier the task
  │     ├─ Light check → one search + verify source, done
  │     └─ Full workflow → load the web-research skill
  │
  └─ ③ Full workflow (web-research)
        date / time range → coarse search → fetch full text → gap-driven second round
        → (if fetch fails) browser fallback → cross-verify → output with sources + labels
```

---

## Quick start

1. **Get an Exa API key** (free credits are enough)  
   Open <https://dashboard.exa.ai> → API Keys → Create Key.  
   New accounts get $20 (~2,800 searches); the free tier adds $10 every month.  
   *No signup? The Exa MCP works anonymously with rate limits — skip the key.*

2. **Install the two files**

   ```bash
   # Rules (user scope, applies to every workspace)
   cp AGENTS.md ~/.zcode/AGENTS.md

   # Skill
   mkdir -p ~/.zcode/skills/web-research
   cp skills/web-research/SKILL.md ~/.zcode/skills/web-research/
   ```

3. **Configure the Exa MCP** (ZCode example)

   Edit `~/.zcode/cli/config.json` and add under `mcp.servers`:

   ```json
   "exa": {
     "type": "http",
     "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa",
     "timeoutMs": 60000,
     "headers": { "x-api-key": "YOUR_EXA_API_KEY" }
   }
   ```

4. **Start a new session** — you should see `web_search_exa` / `web_fetch_exa` / `web_search_advanced_exa`.

Full steps (including three pitfalls, a verification checklist, troubleshooting, and an uninstall list) are in the **[Setup Guide](docs/setup-guide.md)**.

---

## Repository layout

```text
.
├── README.md / README.en.md       # This file (Chinese / English)
├── LICENSE                        # MIT
├── AGENTS.md                      # Standing judgment rules (install to ~/.zcode/AGENTS.md)
├── skills/
│   └── web-research/SKILL.md      # On-demand full research workflow
├── examples/
│   ├── config/zcode-mcp.json      # Exa MCP config example (placeholder key)
│   ├── commands/research.md       # Optional: /research manual force command
│   └── hook/research-trigger.py   # Optional: keyword-injection hook
└── docs/
    ├── 配置教程.md                # Setup guide (Chinese)
    └── setup-guide.md             # Setup guide (English)
```

---

## Design trade-off: why soft triggering by default

Two ways to trigger this strategy; this repo uses the first:

| | Soft trigger (default) | Hard trigger (optional) |
|---|---|---|
| Mechanism | `AGENTS.md` rules + the model loads the skill itself | hook keyword injection / `/research` command |
| Strength | Built-in light/heavy tiering; zero extra config; portable across clients | Deterministic triggering, independent of model judgment |
| Weakness | Depends on model compliance (may drift in long sessions) | No tiering: light lookups run the full flow |

**Controlled experiment** (same model, same task, 4 runs each): both matched on trigger rate, workflow completeness, and output quality; soft triggering was cheaper — in a "composite task with an embedded lookup" scenario, versus a no-strategy baseline, soft was +24% tokens and hard was +43% (the hard injection ran a full research flow for a single-value lookup). Small sample, single model — a directional conclusion.

Hence: **soft triggering by default; enable the `examples/` hook or command only when you need "any message containing the trigger word must run the full flow".**

---

## Cost

See Exa pricing (<https://exa.ai/pricing>):

| Item | Price |
|---|---|
| Search | $7 / 1k requests (up to 10 results; $1 / 1k extra results) |
| Full-text fetch | $1 / 1k pages (text / highlights / summary billed separately) |
| Free credits | $20 for new accounts (~2,800 searches); $10/month on the free tier |
| One light check | ≈ $0.007 |
| One full research run | ≈ $0.03–0.10 |

Standing context cost: `AGENTS.md` is ~1.3k characters (~1k tokens); the skill is loaded only when invoked.

---

## Other clients

The rule file and skill are client-agnostic; only the MCP config differs:

| Client | Config file | Syntax |
|---|---|---|
| **ZCode** | `~/.zcode/cli/config.json` | nested `mcp.servers`, `"type": "http"` + `url` |
| **Claude Code** | project `.mcp.json` | top-level `mcpServers`, `"type": "http"` + `url`; or `claude plugin install exa@claude-plugins-official` |
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers` + `url` |
| **VS Code** | `.vscode/mcp.json` | one-click install, or hand-written `url` |
| Clients without remote MCP | — | `npx -y mcp-remote https://mcp.exa.ai/mcp` |

Rule file: `AGENTS.md` for ZCode, `CLAUDE.md` for Claude Code (same content, rename it).

---

## FAQ

- **Tools don't appear?** Start a new session (MCP servers and skills load at session start). In ZCode, check Settings → MCP.
- **Cannot connect from mainland China?** `mcp.exa.ai` is unstable without a proxy; set `HTTPS_PROXY` in your terminal.
- **Want another search provider?** Tavily / Firecrawl / Brave all have MCP servers; replace tier ① and update the tool names in the skill. The rules stay unchanged.
- **Do I need both browser tools?** No. Either one alone can serve tier ③: with `ego-browser` you always use your real identity, with `playwright-cli` you always run in a disposable container. Splitting them just keeps the choice of "should this page run as me" available.
- **`date` shows the wrong day?** Container / sandbox clocks may be skewed; use the date injected by the session.

---

## Acknowledgements

The core idea comes from a public post by 黑猫道 (coarse search → full-text fetch → browser fallback → site-specific channels). This repo packages it as installable rules and a skill, and validates the soft/hard trigger trade-off with a controlled experiment.
