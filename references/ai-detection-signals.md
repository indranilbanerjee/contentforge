# How AI-Text Detectors Work — and How ContentForge Writes So There Is Nothing to Detect

This is the knowledge base behind Phase 6.5 (humanizer), the `--ai-tell-scan` metric in
`scripts/text-metrics.py`, and the reviewer's Readability dimension. The strategy is
**internalized**: we understand what detectors measure and write genuinely human-grounded
expert prose from the start. External detector tools are never required and never trusted
as a gate.

## The four signal families

### 1. Perplexity — predictability. The master lever.
Perplexity measures how "surprised" a language model is by each next word. AI text is too
predictable: models pick high-probability words, producing smooth, generic phrasing. Human
expert writing is less predictable — specific numbers, named entities, domain jargon used
naturally, unexpected-but-correct word choices.
**Implication → raise real specificity.** A sentence carrying an event + date + named source
("the agency finalized its guidance in June 2024") is high-perplexity because no model would
predict those exact tokens — and it is also simply better writing. Grounding IS the
humanizing move. Fabricating a specific to fake perplexity is forbidden (and Phase 4 catches it).

### 2. Burstiness — variation in sentence length and complexity.
Uniform sentences read as AI; varied ones read as human. **The trap:** inserting batches of
short punchy one-liners raises the burstiness *number* while creating a new uniformity (a
run of polished maxims) that detectors and readers both flag. Genuine irregularity comes
from content: a caveat, an embedded example, a source clause, a mid-sentence qualification.
Never insert content-free sentences to move a metric.

### 3. Stylometric / fine-tuned classifiers.
Trained on human-vs-AI corpora; they recognize the LLM fingerprint: favored vocabulary,
phrase templates ("From X to Y", "It's not just X, it's Y"), participial openers,
rule-of-three rhythm, over-even structure, low epistemic texture (uniform confidence, no
calibrated caveats), impersonal assertion ("...is well documented" — by whom?). These are
patterns 01–41 in `config/humanization-patterns.json`; the deterministic proxies are in
`text-metrics.py --ai-tell-scan`.

### 4. Watermarking (e.g. SynthID-Text).
A statistical signal embedded at generation time by some model providers. Out of scope: we
do not attempt to strip watermarks, and no ContentForge feature may claim to.

## What the evidence says about evasion (be honest)
Detection-guided *iterative* rewriting reduces detection dramatically (~64–99% across
detectors — Adversarial Paraphrasing, arXiv:2506.07001, NeurIPS 2025), while one-shot
static tricks do little and naive paraphrasing can INCREASE detection. Durable results come
from genuine quality that raises perplexity — which is what this pipeline optimizes.
Detectors also have real false positives (uniform *human* text gets flagged). Therefore:
**a detector score is advisory, never a publish gate.**

## The positive model — what human-expert prose does (emulate)
1. **Journalistic grounding:** event + date + named source, inline.
2. **Technical–broad balance:** a technical detail paired with a plain-language explanation
   in the same sentence.
3. **Factual clarity:** plain, specific statements of requirements — no literary devices.
4. **Calibrated expert voice:** specific, defensible caveats — not vague hedging, not
   uniform confidence. (For regulated industries these caveats are also compliance-positive.)
5. **Content-derived variation:** sentence lengths vary because the content varies.

## Two hard guardrails
1. **Never hard-optimize to any specific detector.** Arms race + false positives.
2. **Regulated-content integrity first.** Never trade a verified fact, number, citation, or
   disclaimer for "sounding human." If no grounding exists in the verified research, add a
   calibrated caveat or leave the sentence — never invent a specific.

Sources: GPTZero methodology (gptzero.me/news/how-ai-detectors-work) · Adversarial
Paraphrasing (arXiv:2506.07001, NeurIPS 2025) · Google DeepMind SynthID public documentation.
