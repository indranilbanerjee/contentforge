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
**Prompts you for:**
1. Voice & Tone (select from presets or describe)
2. Formality level (1-5)
3. Personality traits (3-5 adjectives)
4. Approved terminology (comma-separated)
5. Banned terminology (comma-separated)
6. Guardrails and compliance requirements
7. Author profiles (name, title, credentials, profile URL — or explicitly skip for authorless output)

### Update Existing Profile
```
/contentforge:cf-style-guide AcmeMed --source=https://acmemed.com/updated-guidelines --update
```
Merges new information into the existing profile without overwriting unchanged fields.
