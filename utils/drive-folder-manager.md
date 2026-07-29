# Drive Folder Manager — ContentForge Utility

> REFERENCE DOC — pseudocode/algorithm guidance for agents; not an executable module.

## Purpose
Auto-organize output files in Google Drive with consistent folder structure.

## Folder Structure

Folder names are produced by `build_folder_path()` in `scripts/drive-uploader.py`
(`content_type.replace("_", " ").title() + "s"`), which is the implementation of
record. Do not invent alternative spellings.

```
ContentForge/
├── {Brand Name}/
│   ├── Articles/
│   │   └── 2026/
│   │       └── 02-February/
│   │           ├── topic-slug.docx
│   │           └── another-topic_v1.0.docx
│   ├── Blogs/
│   ├── Whitepapers/
│   ├── Faqs/
│   ├── Research Papers/
│   └── Video Scripts/
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

    # Same transform as scripts/drive-uploader.py build_folder_path():
    # article -> Articles, blog -> Blogs, faq -> Faqs,
    # research_paper -> Research Papers, video_script -> Video Scripts
    content_type_folder = content_type.replace("_", " ").title() + "s"

    base = "ContentForge"
    path = f"{base}/{brand_name}/{content_type_folder}/{year}/{month}/"

    # Create folders if they don't exist (Google Drive MCP)
    ensure_folder_exists(path)

    # Filenames carry no timestamp — the year/month folders already do.
    # Versioned outputs use the _v{major}.{minor} suffix.
    filename = f"{topic_slug}.docx"

    return f"{path}/{filename}"
```

## Usage
- **Phase 8:** Call before uploading final .docx
- Creates all parent folders automatically
- Returns full path for MCP upload operation
