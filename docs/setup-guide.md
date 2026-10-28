# Setup Guide: From Zero to Working

This guide uses **ZCode** (3.x, desktop or CLI) for the most specific paths; differences for other clients are in §8.
Takes about 10 minutes; no accounts are required except the optional Exa signup.

---

## 0. Prerequisites

| Item | Requirement |
|---|---|
| Agent client | ZCode 3.x (verified); Claude Code / Cursor etc. — see §8 |
| Network | Reachable `mcp.exa.ai` (a proxy is required from mainland China) |
| Exa account | Optional. Anonymous mode works but is rate-limited; a free account gives steadier quota |
| Node.js | Only needed if you use the browser fallback (`playwright-cli`) or `mcp-remote` |

---

## 1. Register with Exa and get an API key (recommended, ~5 min)

1. Open <https://dashboard.exa.ai> and sign up (Google / GitHub account works)
2. Left menu → **API Keys** → **Create Key**
3. Copy the key (UUID format, e.g. `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) and store it in your password manager

**Credits and pricing** (see <https://exa.ai/pricing> for the authoritative numbers):

| Item | Notes |
|---|---|
| New-account credits | $20 (~2,800 searches) |
| Free tier | $10 more every month (~1,400 searches) |
| Search | $7 / 1k requests (up to 10 results each; $1 / 1k extra results) |
| Full-text fetch | $1 / 1k pages (text / highlights / summary billed separately) |
| Advanced search | Same price as regular search; filters cost nothing extra |
| `agent_run` (optional) | $0.012–$1 per request (multi-step research agent; unavailable on the free tier) |

> For personal daily research you will rarely exhaust the free credits.

---

## 2. Configure the Exa MCP

### 2.1 Config file location

| Scope | Path | Applies to |
|---|---|---|
| User (recommended) | `~/.zcode/cli/config.json` | Every workspace |
| Workspace | `<project>/.zcode/config.json` | That project only |

### 2.2 Write the config

Open `~/.zcode/cli/config.json` and add `exa` under `mcp.servers` (alongside any other entries you already have):

```json
{
  "mcp": {
    "servers": {
      "exa": {
        "type": "http",
        "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa",
        "timeoutMs": 60000,
        "headers": {
          "x-api-key": "YOUR_EXA_API_KEY"
        }
      }
    }
  }
}
```

**Anonymous mode** (no key): remove the entire `headers` field.

> `examples/config/zcode-mcp.json` in this repo is the same template.

### 2.3 Three pitfalls you will hit

1. **The key is `mcp.servers` (nested), not top-level `mcpServers`**  
   ZCode's config file uses a nested structure; `mcpServers` is the `.agents/mcp.json` compatibility format. Wrong location = the server never appears.

2. **The schema is strict; unknown fields silently drop the server**  
   HTTP servers accept only `type` / `url` / `headers` / `enabled` / `timeoutMs` and a few others. One unknown key and the whole server is discarded (no error shown in Settings).

3. **`?tools=` *replaces* the default tool list, it does not append**  
   By default only `web_search_exa` and `web_fetch_exa` are exposed. To use advanced search you must list everything explicitly:  
   `?tools=web_search_exa,web_fetch_exa,web_search_advanced_exa`  
   (`agent_run` requires OAuth or an API key and is unavailable on the free tier.)

### 2.4 Restart and check

1. Start a new session (MCP servers connect at session start)
2. Open **Settings → MCP**; `exa` should be connected
3. Ask the agent something that needs the web and watch for `web_search_exa` calls

---

## 3. Install the rules file (AGENTS.md)

```bash
# User scope (recommended: applies to every workspace)
cp AGENTS.md ~/.zcode/AGENTS.md

# Or workspace scope (that project only)
cp AGENTS.md <project-root>/AGENTS.md
```

**What it is**: standing judgment rules loaded at session start. It contains the five-question preamble, seven categories, the do-not-search list, verification tiers, and hard rules (including conflict adjudication). ~1.3k characters; negligible context cost.

**Note**: if an `AGENTS.md` already exists at the destination, **do not overwrite it** — merge this "web search" section into your existing personal rules.

---

## 4. Install the skill (web-research)

```bash
mkdir -p ~/.zcode/skills/web-research
cp skills/web-research/SKILL.md ~/.zcode/skills/web-research/
```

| Scope | Path |
|---|---|
| User | `~/.zcode/skills/web-research/SKILL.md` |
| Workspace | `<project>/.zcode/skills/web-research/SKILL.md` |

- Skills are discovered **at session start** — start a new session after installing.
- When the same skill name exists in several places, the user scope wins (workspace copies are shadowed).

### 4.1 Browser fallback tools (optional)

Step 5 of the skill splits the browser fallback into two tools. The test is "is this page worth opening with your real identity?". You can run the first two tiers without either of them; only tier ③ needs one.

```bash
# ③a Sites that need login state: ego lite
# Download from https://lite.ego.app/ and finish onboarding on first launch
# (it registers the ego-browser command)

# ③b Untrusted sites that need isolation: playwright-cli
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

- If `playwright-cli install --skills` only writes to `.claude/skills/`, copy the whole `playwright-cli` directory from there into `~/.zcode/skills/` so ZCode picks it up.
- See "Why the browser fallback is split into two tools" in the README for the division of labour and the reasoning. Playwright MCP can substitute if that is what you have; the workflow logic is unchanged.

---

## 5. Verify the whole chain

Start a new session and tick each row:

| # | Check | How | Expected |
|---|---|---|---|
| 1 | MCP connected | Settings → MCP | `exa`: connected |
| 2 | Search tool works | Ask "what's new in AI today?" | `web_search_exa` is called |
| 3 | Trigger word works | Type "联网搜索 <a time-sensitive question>" | Full workflow runs (coarse search → fetch → second round) |
| 4 | Tiering works | Ask a single-fact question (e.g. "the document number of …") | Stops after one search, no full workflow |
| 5 | Output discipline | Look at the answer | Source links + 「confirmed / unconfirmed / freshness unknown」 labels |
| 6 | Human-AI split | Ask "is X worth using?" | Flags it as evaluative and suggests a human search |

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `exa` missing from the tool list | Config not applied / no new session | Check it is under `mcp.servers`; start a new session; restart the client if needed |
| Settings shows `failed` | Invalid schema (extra fields) or bad url | Trim the entry to match §2.2 |
| Search hangs, then times out | Free quota exhausted (429 swallowed by the client) | Add `x-api-key` |
| HTTP 429 | Quota / rate limit | Register for a key, or wait for the monthly refresh |
| Cannot connect from mainland China | Network unreachable | Enable a proxy; set `HTTPS_PROXY` in the terminal |
| Advanced search unavailable | url lacks `?tools=` or lists only some tools | Use the full url from §2.2 |
| Rules have no effect | AGENTS.md in the wrong place / shadowed | User scope wins; verify the path and start a new session |
| Skill does not appear | No new session / wrong directory depth | It must be `skills/<name>/SKILL.md` (two levels) |

---

## 7. Optional: hard trigger (hook + command)

**Not needed by default.** A controlled experiment showed soft and hard triggering tie on quality while soft is cheaper; hard triggering only matters when you need guaranteed triggering.

### 7.1 Manual command (try this first)

Copy `examples/commands/research.md` into `~/.zcode/commands/`, then:

```
/research 2026 export tax rebate latest announcement
```

The command expands the full workflow as instructions, forcing the complete flow. Cost: one line in the command list.

### 7.2 Keyword hook (automated, optional)

1. Copy the script:

   ```bash
   mkdir -p ~/.zcode/hooks
   cp examples/hook/research-trigger.py ~/.zcode/hooks/
   ```

2. In `~/.zcode/cli/config.json`, at the top level (sibling of `mcp`), add:

   ```json
   "hooks": {
     "enabled": true,
     "events": {
       "UserPromptSubmit": [
         {
           "matcher": "联网搜索",
           "hooks": [
             {
               "type": "process",
               "command": "C:/Users/you/AppData/Local/Programs/Python/Python312/python.exe",
               "args": ["C:/Users/you/.zcode/hooks/research-trigger.py"],
               "timeoutMs": 10000
             }
           ]
         }
       ]
     }
   }
   ```

3. Replace `command` / `args` with the real paths on your machine:
   - Windows: absolute path to `python.exe` (`where python`)
   - macOS / Linux: `/usr/bin/python3` or `python3`
4. Start a new session and send a message containing 「联网搜索」 to verify

**Notes**:

- `hooks.enabled: true` is required (config-file hooks are disabled by default)
- The matcher is a **case-sensitive regex**; the four characters must appear consecutively
- The script must print valid JSON (this repo's script already handles it, emitting ASCII-safe output)

### 7.3 Roll back the hard trigger

Delete the `hooks` block from the config, plus `~/.zcode/hooks/research-trigger.py` and `~/.zcode/commands/research.md`.

---

## 8. Other clients

Rules and skill are portable; only the MCP config changes:

| Client | MCP config location | Key syntax |
|---|---|---|
| **ZCode** | `~/.zcode/cli/config.json` | nested `mcp.servers`; `"type": "http"` + `url` |
| **Claude Code** | project root `.mcp.json` | top-level `mcpServers`; `"type": "http"` + `url` (or `claude plugin install exa@claude-plugins-official`) |
| **Cursor** | `~/.cursor/mcp.json` | `mcpServers`; the key is `url` |
| **VS Code** | `.vscode/mcp.json` | one-click install, or hand-written `url` |
| Clients without remote MCP | — | `npx -y mcp-remote https://mcp.exa.ai/mcp` |
| Local Exa MCP | — | `npx -y exa-mcp-server` with env `EXA_API_KEY` |

Rule file: `AGENTS.md` for ZCode, `CLAUDE.md` for Claude Code (same content, rename it).
Skill layout: both use `skills/<name>/SKILL.md`.

---

## 9. Uninstall / rollback checklist

This repo only adds things; uninstalling means deleting what you added:

| Change | Location |
|---|---|
| Rules file | `~/.zcode/AGENTS.md` (deleting just the "web search" section also works) |
| Skill | `~/.zcode/skills/web-research/` |
| MCP config | `mcp.servers.exa` inside `~/.zcode/cli/config.json` |
| Optional command | `~/.zcode/commands/research.md` |
| Optional hook | the `hooks` block in `~/.zcode/cli/config.json` + `~/.zcode/hooks/research-trigger.py` |

Back up `config.json` and `AGENTS.md` before making changes.

---

## 10. Security

- **Never commit your API key**: it belongs only in the local user config (`~/.zcode/cli/config.json`). This repo contains no keys; `.gitignore` excludes common local config files.
- If a key leaks, revoke and recreate it at <https://dashboard.exa.ai>.
- The "human-AI division of labor" rule exists to stop AI from being overconfident on evaluative questions, but it is not professional advice — for health / legal / financial matters, rely on authoritative sources.
