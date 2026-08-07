# cf-style-guide — Troubleshooting

Verbatim troubleshooting entries moved out of `skills/cf-style-guide/SKILL.md` to keep the
skill body within the ~500-line Agent Skills guidance.

### "Could not extract voice characteristics"
**Cause:** Style guide doesn't have explicit voice/tone section, or the page structure is too unstructured.
**Solution:** Use `--source=manual` to provide voice characteristics interactively, then import terminology and guardrails from the document separately.

### "0 approved terms found"
**Cause:** Terminology is embedded in prose rather than structured lists.
**Solution:** Check if the style guide has a terminology table or glossary section. If not, use `--source=manual --scope=terminology` to add terms interactively.

### "URL fetch failed"
**Cause:** Page requires authentication (private Notion, Google Doc not published, login-required page).
**Solution:** If the page is in Notion, use the Notion MCP to access it instead of URL fetch. For Google Docs, use the published web link (File > Share > Publish to Web). For login-required pages, download the page as .docx or .pdf and use the document source.

### "Profile validation failed — Phase 5 incompatible"
**Cause:** Terminology lists contain conflicts (same term in approved and banned lists) or the profile JSON is malformed.
**Solution:** Review the profile JSON for conflicts. Use `--update` mode to fix specific fields without reimporting the entire guide.

### "Import confidence below 70%"
**Cause:** Style guide was vague, lacked structure, or covered primarily visual identity (not content voice).
**Solution:** Supplement with manual input for low-confidence sections. The profile will flag which sections have low confidence so you know what to manually verify.
