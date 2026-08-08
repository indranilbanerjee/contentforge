# cf-style-guide — CLI usage examples

Verbatim usage examples moved out of `skills/cf-style-guide/SKILL.md` ("How to Use") to keep the
skill body within the ~500-line Agent Skills guidance.

### Import from URL
```
/contentforge:cf-style-guide AcmeMed --source=https://acmemed.com/brand-guidelines
```

### Import from Document
```
/contentforge:cf-style-guide AcmeMed --source=./AcmeMed-Style-Guide.docx
```

### Import from Notion Page
```
/contentforge:cf-style-guide AcmeMed --source=https://www.notion.so/acme/Brand-Guidelines-abc123
```

### Import Only Terminology
```
/contentforge:cf-style-guide AcmeMed --source=https://acmemed.com/terminology --scope=terminology
```

### Import Only Guardrails (Compliance)
```
/contentforge:cf-style-guide AcmeMed --source=./compliance-requirements.pdf --scope=guardrails
```

### Manual Input (No Document)
```
/contentforge:cf-style-guide AcmeMed --source=manual
```
The prompt sequence this mode walks through is listed in the skill body under **"From Manual Input"**.
That list is canonical — it carries the authorless opt-out that Step 5 (E-E-A-T) depends on — so it is
deliberately not duplicated here.

### Update Existing Profile
```
/contentforge:cf-style-guide AcmeMed --source=https://acmemed.com/updated-guidelines --update
```
Merges new information into the existing profile without overwriting unchanged fields.
