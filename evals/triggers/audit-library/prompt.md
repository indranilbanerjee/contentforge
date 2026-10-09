---
description: "Near-miss: a list of URLs to score in parallel must route to audit-library, not to cf-audit."
tags: [trigger, near-miss, workflow]
runs: 5
max_turns: 1
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---

Here are the eight blog posts we published last year: https://example.com/blog/zero-trust-banks, https://example.com/blog/cold-chain-pharma, https://example.com/blog/invoice-financing, https://example.com/blog/freight-faq, https://example.com/blog/logistics-automation, https://example.com/blog/warehouse-trends, https://example.com/blog/vaccine-storage, https://example.com/blog/supply-chain-risk. Score each one for freshness in parallel and record a single audit we can plan the refreshes from.
