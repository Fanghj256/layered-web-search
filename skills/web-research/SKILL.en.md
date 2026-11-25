---
name: web-research
description: "Use when a task depends on facts that may have changed or that I have not verified: whether a role is still open and its deadline, policies and official announcements (including document numbers), organizations and personnel, current products and services, numbers and sources in external material, and any \"is this still true?\" question. Search in a tiered workflow, cross-verify, and output with source links and freshness labels. Do not use for reading local files, editing copy, writing code, or pure reasoning."
when_to_use: Load this skill before answering a time-sensitive question from memory, or before putting a number, quotation, or organization name into external material.
---

# Layered Web Research

**English** | [中文](SKILL.md)

> Reference translation of `SKILL.md`. The installed skill still reads `SKILL.md`; if the two versions disagree, `SKILL.md` is authoritative. To run the skill with English instructions, save this file as `SKILL.md` (or point your agent at this file).

Used for cases that `AGENTS.md`'s "verification tiers" classifies as a **full workflow**. If it is only a single fact and one authoritative source (official site, official announcement) can settle it, one search plus source verification is enough; you do not need all the steps below.

## Workflow

0. **Classify the question first**: for evaluative questions ("is it worth using / buying / applying to") and exploratory questions (finding people, inspiration, benchmarks), first remind me to search manually; do not conclude from search results alone.
1. **Confirm the time range**: first use `date` to confirm the current date; if the request is vague, ask me first.
2. **Coarse search**: send 1–2 broad queries with `web_search_exa`. Describe "the page I want" in natural language; do not pile up keywords.
3. **Read the full text**: for highly relevant links, use `web_fetch_exa` to fetch the body. Numbers, announcement/document IDs, dates, and quotations must come from the body text, not just search snippets.
4. **Gap-driven second round**: after reading, decide what is still missing and refine with `web_search_advanced_exa` — add organization entity names, constrain time with `startPublishedDate` / `endPublishedDate`, and lock authoritative sources with `includeDomains` (e.g. gov.cn, official organization sites).
5. **Tool fallback**: when `web_fetch_exa` cannot fetch (dynamic rendering, anti-bot, login wall), split by source type. For known sites that need a login state, use `ego-browser` (shares the local login state; scripts run `ego-browser nodejs`; get the body with `page.evaluate()` on `document.body.innerText`). For suspicious sources that need isolation, use `playwright-cli` (headless by default, profile only in memory, cleared on close). If neither gets it, label it "unverified"; do not force an answer. For code questions use the `gh` CLI (`gh search code`, clone then grep); do not use a search engine to search code.
6. **Cross-verification**: key facts need at least 2 independent sources; when sources conflict, flag the disagreement and do not reconcile it yourself.
7. **Output**: group by category, use tables where useful; every conclusion gets a source link and a label of "confirmed / unconfirmed / freshness unknown" (已证实 / 未证实 / 时效未知).

## Hold these three lines

- **Provenance**: quotations and literature (who proposed it, what year, which journal, which report the data comes from) must be verified against the original; prefer "unverified" over a plausible-looking citation.
- **High risk**: for health, legal, financial, and safety questions, prefer authoritative sources, note uncertainty, and state that this is not professional advice.
- **Checkable**: a conclusion must fit into one checkable sentence — source + time + conclusion — not "the internet says".