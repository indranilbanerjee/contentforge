# cf-style-guide — synthetic brand profile JSON example

Verbatim excerpt moved out of `skills/cf-style-guide/SKILL.md` Step 5 ("Generate Brand Profile
JSON") to keep the skill body within the ~500-line Agent Skills guidance. This is a synthetic
example only — the authoritative schema is `config/brand-registry-template.json`, referenced
from the SKILL.md body.

**SYNTHETIC EXAMPLE (excerpt):**
```json
{
  "brand_name": "AcmeMed",
  "industry": "Healthcare",

  "voice": {
    "primary_tone": "authoritative",
    "secondary_tone": "empathetic",
    "formality_level": 4,
    "personality_traits": ["data-driven", "trustworthy", "innovative", "empathetic", "precise"],
    "tone_by_content_type": {
      "article": "authoritative + data-driven",
      "blog": "authoritative + approachable",
      "whitepaper": "authoritative + academic",
      "faq": "clear + helpful",
      "research_paper": "academic + precise",
      "video_script": "energetic + spoken-word",
      "case_study": "narrative + evidence-led",
      "newsletter": "conversational + direct"
    }
  },

  "content_patterns": {
    "sentence_length": "medium",
    "paragraph_length": "3-5 sentences",
    "active_voice_target": 90,
    "person": {
      "article": "third",
      "blog": "second",
      "whitepaper": "third"
    },
    "contractions": {
      "article": false,
      "blog": true,
      "whitepaper": false
    },
    "rhetorical_questions": "sparingly",
    "statistics_usage": "heavy",
    "storytelling": "patient stories, anonymized"
  },

  "terminology": {
    "approved": [
      {"term": "AcmeMed", "note": "Never 'Acme Med' or 'ACMEMED'"},
      {"term": "healthcare", "note": "One word, not 'health care'"},
      {"term": "precision medicine", "note": "Preferred over 'personalized medicine'"}
    ],
    "banned": [
      {"term": "revolutionary", "replacement": "innovative"},
      {"term": "breakthrough", "replacement": "advancement"},
      {"term": "cure", "replacement": "treatment or therapy"},
      {"term": "guaranteed", "note": "Compliance violation in healthcare"}
    ],
    "conditional": [
      {"term": "FDA-cleared", "condition": "Only for products with actual FDA clearance"},
      {"term": "clinically validated", "condition": "Only with citation to clinical trial"}
    ],
    "acronyms": [
      {"acronym": "AI", "expansion": "Artificial Intelligence", "expand_on_first_use": true},
      {"acronym": "HIPAA", "expansion": "Health Insurance Portability and Accountability Act", "expand_on_first_use": false}
    ]
  },

  "guardrails": {
    "required_disclaimers": [
      {"context": "all_articles", "text": "This content is for informational purposes only and does not constitute medical advice."},
      {"context": "product_mentions", "text": "AcmeDiagnostics is pending FDA clearance for [specific use case]."}
    ],
    "prohibited_claims": [
      "No efficacy claims without peer-reviewed citation",
      "No 'FDA-approved' — use 'FDA-cleared' for 510(k) devices",
      "No cost savings claims without specific study reference"
    ],
    "compliance": {
      "hipaa": "Never include PHI",
      "fda": "Follow 510(k) promotional guidelines",
      "ftc": "Disclose sponsored or partnership content"
    },
    "sensitivity": {
      "language": "person-first",
      "avoid_metaphors": ["military metaphors for disease"],
      "inclusivity": "diverse, respectful, representative"
    }
  },

  "metadata": {
    "industry": "Healthcare",
    "sub_industry": "Health Technology / Medical Devices",
    "target_audiences": ["Healthcare Executives", "Clinical Decision Makers", "Health System IT Leaders"],
    "content_types_supported": ["article", "blog", "whitepaper", "faq", "research_paper", "video_script", "case_study", "newsletter"],
    "import_confidence": 94
  }
}
```
