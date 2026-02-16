# Drive Folder Manager — ContentForge Utility

## Purpose
Auto-organize output files in Google Drive with consistent folder structure.

## Folder Structure

```
ContentForge/
├── {Brand Name}/
│   ├── Articles/
│   │   └── 2026/
│   │       └── 02-February/
│   │           ├── topic-slug-2026-02-16.docx
│   │           └── another-topic-2026-02-17.docx
│   ├── Blog-Posts/
│   ├── Whitepapers/
│   ├── FAQs/
│   └── Research-Papers/
```

## Auto-Creation Logic

**Phase 8 (Output Manager) Implementation:**

```python
def get_output_path(brand_name, content_type, topic_slug):
    """
    Create folder structure if it doesn't exist
    Return full path for file upload
    """
    year = current_year()  # "2026"
    month = current_month_padded()  # "02-February"

    base = "ContentForge"
    path = f"{base}/{brand_name}/{content_type}/{year}/{month}/"

    # Create folders if they don't exist (Google Drive MCP)
    ensure_folder_exists(path)

    timestamp = current_date()  # "2026-02-16"
    filename = f"{topic_slug}-{timestamp}.docx"

    return f"{path}/{filename}"
```

## Usage
- **Phase 8:** Call before uploading final .docx
- Creates all parent folders automatically
- Returns full path for MCP upload operation
