# Citation Formatter — ContentForge Utility

## Purpose
Standardize citation formatting across all content types based on brand preferences (APA, MLA, Chicago, IEEE).

## Supported Formats

### APA 7th Edition (Default)
**In-text:** (Author, Year) or Author (Year)
**Reference:**
```
Author, A. A. (Year). Title of article. Journal Name, volume(issue), pages. https://doi.org/xxxxx
```

### MLA 9th Edition
**In-text:** (Author page) or Author (page)
**Works Cited:**
```
Author, First. "Title of Article." Journal Name, vol. XX, no. X, Year, pp. XX-XX., doi:xxxxx.
```

### Chicago 17th (Notes-Bibliography)
**Footnote:** Author, "Title," Journal XX, no. X (Year): pages, https://doi.org/xxxxx.
**Bibliography:**
```
Author, First Last. "Title of Article." Journal Name XX, no. X (Year): XX-XX. https://doi.org/xxxxx.
```

### IEEE
**In-text:** [1], [2], etc.
**Reference:**
```
[1] A. Author, "Title of article," Journal Abbrev., vol. XX, no. X, pp. XX-XX, Mon. Year, doi: xxxxx.
```

## Usage in Pipeline

**Phase 3 (Drafter):** Insert inline citations in brand's preferred style
**Phase 5 (Structurer):** Format bibliography/references section
**Phase 7 (Reviewer):** Verify citation format consistency

## Brand Profile Field
```json
"citation_rules": {
  "format": "APA | MLA | Chicago | IEEE",
  "inline_citation_format": "numbered | author_year | footnote"
}
```
