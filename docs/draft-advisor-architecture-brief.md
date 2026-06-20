# Phase-2 Agentic Advisor — Architecture Brief (2026-06-19)

Deep-research synthesis answering the five-part Phase-2 advisor design question:
retrieval/grounding, KB schema, agentic design, serving/cost, and evaluation.
Built on top of the decisions already in `docs/draft-advisor-kb-design.md` and the
implemented `data/build_advisor_context.py` — this brief **validates** those with
external evidence, **corrects** two stale assumptions (Fly.io GPU; serving plan),
and **fills the open gaps** (single-prompt vs agent, the cost decision, and the
eval harness, which does not yet exist).

Bottom line up front:

- **No vector RAG.** Deterministic key-select by (map, mode, picked/banned) + full-record
  injection is the textbook-correct choice at this corpus size — the research is unanimous.
  (Already the project's decision; now externally confirmed.)
- **Single grounded prompt, not a tool-using agent.** 8B-class tool-calling reliability sits
  in the "cliff zone"; every hop compounds failure. Compute the candidate shortlist
  deterministically (the scorer already exists) and give the LLM **one** grounded call.
- **Serving: serverless open-8B (Groq or DeepInfra), NOT self-hosted, NOT Fly.io GPU.**
  Fly.io GPUs are **deprecated as of July 31, 2026** — the CLAUDE.md "Fly.io ~$5/mo for the
  advisor" plan is dead. At your volume a metered API is ~3 orders of magnitude cheaper than
  a dedicated GPU. **Honest flag:** at low early volume, `gpt-4o-mini` (~$0.75/1k drafts) is so
  cheap and so much more reliable at grounded JSON + citation that it is the smarter *bring-up*
  default; keep open-8B as the steady-state cost play behind the same interface.
- **Highest-leverage first build: the eval harness + a 30–50-draft golden set**, before any
  serving work. You cannot tune grounding or justify a model choice without it.

---

## 1. Retrieval / grounding architecture

**Verdict: deterministic structured lookup + full-record injection. No embeddings.**

The KB is tens-to-low-hundreds of records keyed by `(map, mode)` plus a sparse
brawler-pair matrix — queried by keys you already hold at draft time. This is the
canonical case where a vector pipeline is pure overhead:

- For small, structured corpora with consistent terminology, a custom vector/RAG pipeline
  is overkill — you spend more on infrastructure than on the agent, and keyword/structured
  retrieval performs as well because structured data lacks the slang/paraphrase that
  embeddings exist to absorb. ([Towards Data Science — "You probably don't need a vector
  database for your RAG yet"](https://towardsdatascience.com/you-probably-dont-need-a-vector-database-for-your-rag-yet/))
- Vector DBs earn their keep on **operational** triggers — persistence, high-frequency CRUD,
  metadata-filtered scale — not row count. 1M 384-dim vectors is ~1.5 GB RAM; ~73k chunks run
  fine on brute-force scikit-learn. A KB of hundreds of records never hits a scale wall. (ibid.)
- RAG's real failure is *data selection* (`SELECT … WHERE <what matters>`), not similarity;
  generic embeddings crowd together (~0.1 cosine between arbitrary docs) and miss domain terms —
  so deterministic filtering beats embedding retrieval for "understood" queries like a map+mode key.
  ([softwaredoug — "RAG users want affordances, not vectors"](https://softwaredoug.com/blog/2025/12/09/rag-users-want-affordances-not-vectors))

**Inject the whole matched record, don't chunk it.** Long-context (full relevant content in
the prompt) generally beats RAG on factual QA; RAG only wins on open-ended dialogue and on its
cost/latency, which is negligible when the record is small.
([arXiv 2501.01880](https://arxiv.org/abs/2501.01880),
[Vellum — RAG vs long-context](https://www.vellum.ai/blog/rag-vs-long-context)).
**Caveat for the open-model plan:** Llama 3.1 / Qwen 2.5 have weaker long-context capacity than
frontier models and degrade well before their 128k windows — so inject the *tight selected set*,
never the whole KB. (arXiv 2501.01880; matches the project's own observation that 8B F1 cliffs at
~40–50% of the window.)

**Hybrid retrieval is not worth it here.** On structured data, BM25+vector with RRF gave only
~7% nDCG lift over BM25 alone, and on exact-match needs (entity/map names) BM25 dominates outright.
([digitalapplied — hybrid search reference 2026](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026)).
The only future embedding candidate is **long-form pro prose notes**, and only once key-filtered
prose for one (map, mode) regularly exceeds the budget — and even then, rerank *within* the
key-filtered set, never a global index. (Already the project's stance; confirmed.)

**Citation / attribution pattern.** Two viable routes, with a real conflict between them:

- *Native structured citations* (Anthropic Citations API) return guaranteed-valid pointers —
  `cited_text` + `document_index` + char/block range — far more reliable than prompt-only "please
  cite." Each KB record becomes its own citable custom-content block.
  ([Claude Citations docs](https://platform.claude.com/docs/en/docs/build-with-claude/citations)).
  **But** the Citations API is *incompatible with Structured Outputs* (HTTP 400 if both on). (ibid.)
- *Prompt-enforced citation* (cite the `record_id` present in context) works on any model incl.
  open-8B and composes with JSON output — at the cost of fabrication risk that you must verify.

**Recommendation: prompt-enforced `record_id` citation + JSON output + a post-hoc validator**
that checks every cited id exists in the supplied context and every numeric claim is traceable to
a supplied field. This keeps the open-model path and the structured-output path both open, and the
validator is the actual guarantee — model-generated citations are fabricated at high rates
(reports up to 78–90% in some settings; LLM-judge citation validation only ~16–17% recall),
so **citations must be checked against supplied ids, never trusted**.
([arXiv 2510.17853](https://arxiv.org/html/2510.17853v4)).

**Keeping the LLM from overriding the KB with stale training knowledge** — the central risk for a
meta-drifting game. The evidence says instruction alone is insufficient:

- Even told to answer only from context, LLMs cannot fully suppress parametric memory, and *more
  factual* models get *worse* at faithfulness when context conflicts with what they "know" — a
  documented factuality-vs-faithfulness tradeoff.
  ([arXiv 2404.00216](https://arxiv.org/pdf/2404.00216), [arXiv 2503.10996](https://arxiv.org/html/2503.10996v1)).
- Faithfulness is task-dependent: models adhere to context on *context-reading* tasks but fall
  back to parametric memory on *knowledge-recall* tasks. ([arXiv 2506.06485](https://arxiv.org/pdf/2506.06485)).
  → **Frame the prompt as reading the supplied dossier, not "what's the best brawler."**
- Opinion-framing ("according to the curator's notes, …") and counterfactual demos measurably
  improve faithfulness under knowledge conflict (context fidelity ~92–94% on Llama3-70B in the
  best case). ([arXiv 2303.11315](https://arxiv.org/abs/2303.11315)). Cheap to apply; worth it.

---

## 2. KB schema design

The existing `data/kb/` schema (v1 in kb-design §4) is well-aligned with how every comparable
tool structures its data. External patterns that confirm and sharpen it:

- **`(mode, map)` is the right partition key**, not a global ranking. Brawltime and Brawlify both
  organize their entire tier list around the `(mode, map)` tuple, ranking brawlers *within* that
  context. ([brawltime.ninja](https://brawltime.ninja/tier-list/mode/brawl-ball), [brawlify.com/maps](https://brawlify.com/maps)).
- **Counters/synergies as signed-delta edge-lists, absence = neutral** — exactly DraftGap/Dota
  Terminal's pattern: counter = head-to-head WR − base WR; synergy = combined WR − avg(base);
  pairs with <20 games treated as neutral, not fabricated.
  ([Dota Terminal](https://www.dotaterminal.com/draft)). Your `matrix.json` already does this.
- **Tier and ban-priority are separate axes.** Competitive lists add an `S+` "must-pick or priority
  ban" band that collapses two things; keep them split. ([mmonster — BS meta](https://mmonster.co/blog/brawl-stars-meta)).
- **Power-by-phase + free-text win condition** (Mobalytics pattern): ordinal `early/mid/late`
  strength plus a one-line strategic statement. ([Mobalytics power spikes](https://mobalytics.gg/blog/how-to-understand-power-spikes-using-mobalytics/),
  [win conditions](https://mobalytics.gg/blog/how-to-recognize-your-win-conditions-in-league-of-legends/)).
- **Snapshot-per-patch versioning** (Riot Data Dragon pattern): immutable complete snapshot per
  patch, effective-dated by `gameVersion`. Old advice stays queryable; staleness detection is a
  version compare. ([wombocombo — Riot API](https://www.wombocombo.gg/blog/game-analytics/league-api-how-it-works)).
  Your per-record `patchVersion`+`lastVerified` + git snapshot already implements this.

**Low-friction authoring** (the "not a chore" goal) — the design literature is consistent:

- Minimal required fields: a 5–8 field MVP, only the truly essential marked `required`, everything
  else optional-by-default. ([JSON Schema MVP guidance](https://nimblebrain.ai/method/schemas--designing-business-schemas/)).
- Volatile vocabularies (the brawler roster, which changes every patch) live in a **separate
  versioned enum source**, not inline in the schema.
  ([json-schema-org discussion](https://github.com/orgs/json-schema-org/discussions/142)).
- Nullable unions (`string | null`) let a curator mark "unknown" without fabricating — the same
  mechanism that stops an LLM bootstrap pass from hallucinating into empty fields.
  ([schema features](https://claudecertified.io/knowledge/foundations/f6-2-schema-features/)).
- Curated/vetted content is the hallucination control itself: one 2025 study found a RAG system on
  curated content had near-zero hallucination vs fabricating answers to 52% of out-of-scope
  questions on unvetted data — so **provenance/confidence must be a first-class required field**.
  ([atlan — LLM knowledge base](https://atlan.com/know/what-is-an-llm-knowledge-base/)). Your
  `confidence: pro|stats|community|llm-draft` + `source` already does this.

### Proposed concrete schema (v2 — extends the shipped v1)

Keeps everything in v1 and adds the phase/win-condition/ban-priority axes the comparable tools
expose. **Bold = required; rest optional/nullable.** Pros only ever fill the un-derivable parts.

```jsonc
// data/kb/maps/<InternalName>.json  — one (map, mode) entry
{
  "map": "Gemgrab_42",            // **required** — partition key part 1
  "mode": "Gemgrab",              // **required** — partition key part 2
  "patchVersion": "67.301",       // **required** — effective-dated snapshot key
  "lastVerified": "2026-06-10",   // **required**
  "confidence": "pro",            // **required** — pro|stats|community|llm-draft

  "archetype": ["open-mid", "double-bush-flank"],     // controlled vocab (separate enum file)
  "descriptors": { "bushPct": 0.18, "wallPct": 0.22, "chokeCount": 3 },  // AUTO-DERIVED, not authored

  "pickPriority": [               // ranked; pros author `tier`+`why`, stats fill `winRate`
    { "brawler": "Gene", "tier": "S+", "banPriority": "high",
      "winRate": 0.61, "adjustedWinRate": 0.58,        // adjusted = Bayesian-smoothed (nullable)
      "powerByPhase": { "early": "high", "mid": "high", "late": "mid" },  // nullable
      "winCondition": "control mid via center-wall pull; deny enemy gem carrier",  // free-text, nullable
      "lane": "mid",              // nullable enum
      "why": "mid control + pull through center wall",
      "recordId": "Gemgrab_42#Gene" }   // stable id for citation
  ],

  "comps": [
    { "name": "double thrower siege", "brawlers": ["Tick","Barley","Gene"],
      "why": "...", "recordId": "Gemgrab_42#comp#double-thrower-siege" }
  ],
  "banNotes": "Gene first-ban on first-pick side; otherwise contest mid sniper."  // free-text, nullable
}
```

```jsonc
// data/kb/matrix.json — one signed-delta edge (unchanged from v1, with recordId added)
{ "a": "Piper", "b": "Mortis", "type": "counter",   // directional: b beats a
  "deltaRating": -0.35,                              // log-odds delta vs independence baseline
  "reason": "Mortis closes the gap on Piper's long reload; no escape once dashed on",
  "modeContext": ["Knockout","Wanted"],             // null = mode-agnostic
  "confidence": "pro", "statsCheck": "SUPPORTED: pair WR 0.63 vs mean 0.60 (n=7416)",
  "patchVersion": "67.301", "lastVerified": "2026-06-10",
  "recordId": "edge#Mortis>Piper" }                 // stable id for citation
```

Every `recordId` is what the LLM cites and the validator checks. Auto-derived attributes
(thrower/range/HP/mobility per kb-design §3) stay machine-generated — pros never touch them.

---

## 3. Agentic design

**Verdict: single grounded prompt, not a tool-using agent. The scorer does the retrieval/ranking
deterministically; the LLM makes exactly one grounded call to rank-and-explain among the shortlist.**

8B-class models are in the unreliable middle of the tool-calling capability cliff:

- Llama 3.1 8B scores ~76% on BFCL overall (vs 88.5% for 405B in the same family), and the gap
  *widens* on the multi-turn / agentic categories. ([llm-stats BFCL](https://llm-stats.com/benchmarks/bfcl),
  [Gorilla leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html)).
- Tool-invocation reliability is a capacity cliff: catastrophic in ≤3B, near-solved only at 14B+,
  closed-source parity ~32B. An 8B sits in the unreliable middle.
  ([arXiv 2601.16280](https://arxiv.org/pdf/2601.16280)).
- Multi-tool flows compound failure and latency — each hop is another fallible call; per-call
  reliability <0.95 degrades sharply over 3–5 hops, and plan-execute agents added ~34s/task in one
  measurement. ([tool-use survey](https://arxiv.org/pdf/2603.22862)).

So **don't make the 8B orchestrate KB-lookup / tier-fetch / synergy-query as tools.** Do those
deterministically in code (the `build_advisor_context.py` assembler + the ~50-line signed-delta
scorer already do exactly this), inject the result, and spend the model's single call on the one
thing the deterministic scorer provably can't do: comp-identity judgement + the natural-language
explanation. This is also the cheaper pattern — a 7B is ~10–30× cheaper/lower-latency per call
than a 70B+, which only pays off if you're not multiplying calls.
([NVIDIA SLM-agentic position via arXiv 2510.03847](https://arxiv.org/pdf/2510.03847)).

**Division of labor (already in kb-design §2, confirmed):** scorer proposes the shortlist and
supplies *every number*; LLM picks among the top candidates and writes the citation-bearing
rationale; a validator flags any numeric claim or citation not traceable to a supplied field.

**Structured JSON output.** Use constrained/grammar decoding, then validate-and-repair:

- Grammar-constrained decoding raises schema compliance to 96–98%+ vs 90–94% unconstrained, and
  the gap explodes on hard schemas (41% vs 13%). ([JSONSchemaBench, arXiv 2501.10868](https://arxiv.org/html/2501.10868v1)).
- It does **not** hurt task quality — slightly *improves* it (GSM8K 83.8% vs 80.1%). (ibid.) This
  kills the "grammar-forcing dumbs the model down" worry.
- But "compiles" ≠ "valid": XGrammar showed over-permissive failures in 38 categories, so you still
  need a **post-hoc JSON-schema validation pass + bounded retry/repair loop**. (ibid.,
  [Red Hat vLLM structured outputs](https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses)).
  Groq exposes JSON mode; vLLM exposes guided decoding (XGrammar/Guidance) — pick whichever the
  chosen host supports; the validator is the real guarantee regardless.

**Forced citation + refusal path.** Instruct answer-only-from-context, cite `recordId` per claim,
and explicitly **refuse** ("the supplied notes don't cover this") rather than fill gaps — small
models default to filling gaps with internal (stale) knowledge. ([RAG grounding tests](https://medium.com/@Nexumo_/rag-grounding-11-tests-that-expose-fake-citations-30d84140831a)).
Refusal is itself a measurable weakness, so it must be a *benchmarked* held-out case, not assumed.
([RefusalBench, arXiv 2510.10390](https://arxiv.org/pdf/2510.10390)).

**Faithfulness reality for 8B.** Small models hallucinate materially more than frontier on grounded
generation — best frontier models cluster ~1–5% on Vectara's leaderboard; small open models are
worse and default to internal knowledge when context is incomplete.
([Vectara hallucination leaderboard](https://www.vectara.com/blog/introducing-the-next-generation-of-vectaras-hallucination-leaderboard),
[FaithBench, arXiv 2410.13210](https://arxiv.org/pdf/2410.13210)).
The reliability win therefore comes from the **architecture** (deterministic shortlist + constrained
output + per-claim citation check + refusal path), not the base model — small grounded models reach
competitive faithfulness only when paired with an explicit verification layer.
([HalluGuard, arXiv 2510.00880](https://arxiv.org/pdf/2510.00880)).

---

## 4. Open-model serving & cost

**Per-draft assumption:** ~3000 input + 500 output tokens → 1k drafts = 3.0M in + 0.5M out;
10k drafts/mo = 30M in + 5M out. (Matches the measured ~1.8K-token Hard Rock Mine context with
headroom for KB growth.)

### $/1k-drafts (verified pricing, May–June 2026)

| Option | $/M in | $/M out | **$/1k drafts** | Notes |
|---|---|---|---|---|
| **DeepInfra Llama 3.1 8B (FP8)** | 0.03 | 0.05 | **~$0.12** | cheapest 8B |
| **Groq Llama 3.1 8B Instant** | 0.05 | 0.08 | **~$0.19** | 560–840 tok/s; *verified* |
| **GPT-4o-mini** | 0.15 | 0.60 | **~$0.75** | cheapest frontier-grade |
| **DeepInfra Llama 70B** | 0.23 | 0.40 | **~$0.89** | quality headroom, cheap |
| **GPT-5-mini** | 0.25 | 2.00 | **~$1.75** | |
| **Gemini 2.5 Flash** | 0.30 | 2.50 | **~$2.15** | |
| **Groq Llama 3.3 70B** | 0.59 | 0.79 | **~$2.16** | 280–394 tok/s |
| **Claude Haiku 4.5** | 1.00 | 5.00 | **~$5.50** | strongest cheap frontier |
| **Self-host A100 (vLLM)** | — | — | **~$1,500/mo fixed** | break-even ~256M tok/mo |

Sources: [Groq/aipricing.guru](https://www.aipricing.guru/groq-pricing/) (Groq 8B $0.05/$0.08 *re-verified*),
[CloudZero Groq](https://www.cloudzero.com/blog/groq-pricing/), [DeepInfra](https://deepinfra.com/llama),
[OpenAI pricing](https://openai.com/api/pricing/), [Gemini compare](https://langcopilot.com/gemini-3-flash-vs-gpt-5-mini-pricing),
[CloudZero Claude](https://www.cloudzero.com/blog/claude-pricing/),
[self-host vs API](https://devtk.ai/en/blog/self-hosting-llm-vs-api-cost-2026/).

### Self-hosting / Fly.io — two corrections to CLAUDE.md

- **Fly.io GPUs are deprecated as of July 31, 2026** (unavailable after Aug 1) — *re-verified
  against Fly's own community migration post*. The CLAUDE.md "Fly.io ~$5/mo for the advisor"
  plan and the kb-design "runs on the existing Fly.io box" assumption are **dead for GPU serving**.
  ([Fly.io GPU deprecation](https://community.fly.io/t/gpu-migration-fly-io-gpus-will-be-deprecated-as-of-july-31-2026/27110),
  [Fly pricing](https://fly.io/docs/about/pricing/)). (The Fly.io box is still fine for the Y.js sync
  server and the stats self-collector — CPU workloads. Only GPU serving is affected.)
- **Self-hosting breaks even ~256M tokens/month** (vLLM 70B on 1×A100 ≈ $1,500/mo vs blended
  frontier ~$5.63/M) — that's ~7–25× your stated <10k-drafts/mo volume, before counting idle-GPU
  billing and ops/on-call. Under ~50k req/mo serverless is "not even close to debatable."
  ([self-host vs API](https://devtk.ai/en/blog/self-hosting-llm-vs-api-cost-2026/),
  [aipricingmaster](https://www.aipricingmaster.com/blog/self-hosting-ai-models-cost-vs-api)).

### Recommendation (and the honest frontier-API flag)

**Steady state:** serverless open-8B (Groq for speed on a pick clock, or DeepInfra for absolute
cheapest) at **~$1–2/mo at 10k drafts**. The CLAUDE.md "open LLM to save cost" rationale is valid —
**but only via serverless hosts, never self-hosted, and not on Fly.io GPU.**

**Honest flag — at low early volume a metered frontier mini is the smarter *bring-up* default.**
The whole-system cost gap is trivial (GPT-4o-mini ~$7.50/mo vs Groq-8B ~$1.90/mo at 10k drafts —
a $5–6/mo difference), while §3's evidence says the 8B is materially worse at exactly what this
system needs: grounded JSON, faithful citation, and clean refusal. Spending an extra ~$6/mo to
remove the dominant quality risk during bring-up is the correct early trade. So:

- **Build behind a provider-agnostic interface** (the assembler already emits provider-neutral
  context). Bring up on **`gpt-4o-mini`** (or Haiku 4.5 if you want the strongest cheap grounding),
  get the eval harness green, *then* A/B swap in **Groq Llama 3.1 8B** and keep it only if it holds
  groundedness/citation/refusal scores within tolerance. A **hybrid** also works: open-8B for the
  common path, frontier-mini fallback for hard drafts — still well under $60/mo at 10k.
- **Is 8B strong enough?** For *ranking-and-explaining over a pre-built shortlist with everything
  injected* — plausibly yes, *with* the verification architecture. For *unaided* grounded reasoning
  it is not (§3). The eval harness, not intuition, decides the swap.

---

## 5. Evaluation

No eval harness exists yet. This is the highest-leverage thing to build — you cannot tune grounding,
justify the model choice, or survive a balance patch without it. Three orthogonal scoring axes:

**(a) Groundedness / citation faithfulness** — reference-free, runs in CI without labels:

- **RAGAS faithfulness** decomposes the rationale into atomic claims and scores the fraction
  entailed by the supplied context — no human ground-truth needed.
  ([RAGAS metrics](https://docs.ragas.io/en/v0.1.21/concepts/metrics/)).
- **FActScore** — fraction of atomic facts supported by the KB; automated estimator agrees with
  humans within <2%. ([arXiv 2305.14251](https://arxiv.org/abs/2305.14251),
  [github](https://github.com/shmsw25/factscore)).
- **ALCE citation precision/recall** — does the cited `recordId` actually support the statement,
  measured *separately* from answer correctness. ([ALCE, ACL 2023](https://aclanthology.org/2023.emnlp-main.741)).
- Critical: **correctness ≠ faithfulness** — answers can be right yet cite a non-supporting source
  (post-rationalization found in up to ~57% of citations), so measure at the claim→source link,
  not answer-level. ([arXiv 2412.18004](https://arxiv.org/pdf/2412.18004)). Cheapest impl: an NLI
  entail/neutral/contradict pass per atomic claim vs its cited record.

**(b) Expert match** — needs a maintained held-out pro-labeled set:

- **Recall@k / top-k accuracy / NDCG@k** of the advisor's suggestions vs the held-out expert pick
  (NDCG@k credits rank order). ([Evidently — recsys ranking metrics](https://www.evidentlyai.com/ranking-metrics/evaluating-recommender-systems)).
  You already have a labeled corpus to seed this: `data/pro_drafts.json` (1737 Liquipedia pro games)
  — held-out next-pick prediction is the natural top-k metric.
- **Cohen's kappa** for the categorical "agree/disagree with expert" framing and to validate
  annotator reliability on the golden set (chance-corrected). (ibid.)

**(c) Preference vs baseline** — LLM-as-judge, with the known biases controlled:

- A strong judge (GPT-4) hits >80% agreement with human pairwise preference, matching the ~81%
  human–human baseline. ([MT-Bench, arXiv 2306.05685](https://arxiv.org/pdf/2306.05685)).
- **Control position bias** (judges favor first response up to ~70% of the time) by swapping order
  and averaging / counting only consistent verdicts; **control verbosity bias** (longer preferred
  >90% of the time) with length control. (ibid., [length-controlled AlpacaEval](https://arxiv.org/pdf/2404.04475)).
- Aggregate with **Bradley–Terry** (not online Elo) for stable ratings + CIs; watch for
  non-transitive judgments. ([LMSYS leaderboard](https://www.lmsys.org/blog/2023-12-07-leaderboard/),
  [arXiv 2502.14074](https://arxiv.org/pdf/2502.14074)). Baseline to beat = the deterministic
  signed-delta scorer alone — this is exactly how you measure "did the LLM add anything" before
  paying for the KB/serving.

**Regression testing — "evals as unit tests," and the patch problem is a versioning problem:**

- Versioned **golden dataset** (representative drafts + expected picks/rubrics) re-run on every PR
  in CI to gate deploys. Tooling: **promptfoo** or **DeepEval** for the CI gate (no vendor lock-in,
  bundles RAG faithfulness), optionally Braintrust/LangSmith for dashboards.
  ([LLM eval tools comparison](https://inference.net/content/llm-evaluation-tools-comparison/),
  [regression pipeline](https://testquality.com/llm-regression-testing-pipeline/)).
- **Eval drift is a named failure mode**: a balance patch makes prior "correct picks" obsolete, so
  passing offline evals can mask wrong live advice. The fix is continuous curation — add edge cases,
  re-label, drop obsolete rows. ([coverge — LLM regression testing](https://coverge.ai/blog/llm-regression-testing),
  [getmaxim — dataset challenges](https://www.getmaxim.ai/articles/challenges-in-managing-high-quality-datasets-for-llm-evaluation/)).
- **Pin the KB snapshot to the golden set.** Test three drift axes separately: prompt drift, model
  drift, and **KB/data drift** (a patch). A patch must *invalidate and re-derive the affected eval
  rows*, not silently re-run stale labels.
  ([futureagi — regression testing](https://futureagi.com/glossary/llm-regression-testing/)).
  Concretely: tag every golden row with `patchVersion`; on a new patch, the CI flags rows whose
  `patchVersion < live` as "needs re-label" and excludes them from the pass-rate until re-verified —
  reusing the exact coverage-drift trigger the pro-curator track already has.

### Proposed eval harness (concrete)

```
data/eval/
  golden/<patch>/drafts.jsonl   # {map, mode, partial_draft, expert_next_pick, expert_bans, patchVersion}
                                #   seeded from pro_drafts.json held-out games; pros confirm/correct
  run_eval.py                   # promptfoo/DeepEval driver
  metrics/
    groundedness.py             # per-claim NLI entailment vs cited recordId (faithfulness, ALCE-style)
    expert_match.py             # Recall@k / NDCG@k vs expert_next_pick; Cohen's kappa
    preference.py               # swap-averaged, length-controlled LLM-judge; Bradley-Terry vs scorer baseline
  report.md                     # CI artifact; gates merges + model swaps
```

CI gate on every PR + every KB/model change: (1) **groundedness** (every cited id exists; every
number traceable; faithfulness ≥ threshold) — *hard gate, reference-free*; (2) **expert match**
Recall@k vs the held-out set — *tracked, regression-alerting*; (3) **preference win-rate** vs the
scorer baseline — *the "is the LLM earning its cost" gate*. On a patch: re-label flagged golden rows
before trusting the pass rate.

---

## Recommended end-to-end architecture

```
draft turn {partial draft, map, mode}
  │
  ▼  [deterministic, in code — no model, no embeddings]
1. KEY-SELECT      build_advisor_context.py: select (map,mode) record + draft-relevant
                   brawler rows + counter/synergy edges + patch-tagged stats; budget ~4–8K tok
2. SCORE/SHORTLIST ~50-line signed-delta scorer ranks candidates, supplies EVERY number,
                   emits top-8 + contributing terms   ← also the eval baseline
  │
  ▼  [ONE grounded model call — serverless, provider-agnostic]
3. RANK + EXPLAIN  inject dossier (opinion-framed, "read these notes, don't recall");
                   constrained JSON out; cite recordId per claim; refuse if unsupported
                   bring-up: gpt-4o-mini  →  steady state: Groq Llama 3.1 8B (A/B-gated)
  │
  ▼  [deterministic]
4. VALIDATE        JSON-schema validate → every cited recordId exists, every number traceable
                   → bounded repair/retry; on fail, fall back to scorer-only output
  │
  ▼
5. EVAL (CI)       groundedness (hard) + expert-match Recall@k + preference vs scorer baseline;
                   golden set pinned to patchVersion; patch ⇒ re-label flagged rows
```

Degrades gracefully: if the model call/validation fails or budget is blown, ship the scorer's
ranked shortlist with canned reason-chips. The LLM is an *enhancement layer over a correct
deterministic core*, never a single point of failure.

---

## The single highest-leverage thing to build first

**The eval harness + a 30–50-draft golden set held out from `pro_drafts.json` (pro-confirmed),
with the deterministic signed-delta scorer as the baseline.**

Rationale: it's the only way to answer every open question objectively — is 8B strong enough vs a
frontier mini? does the LLM beat the scorer at all? did a balance patch break us? Without it,
model choice and prompt tuning are vibes, and you'd risk paying for the long-pole KB/serving work
before knowing the LLM adds value. The scorer + assembler already exist, so the baseline is free;
the eval harness turns every subsequent decision into a measurement.

## Phased build order

1. **Eval harness + golden set + scorer baseline.** (Highest leverage; unblocks every decision below.)
   Reuse `pro_drafts.json`; CI gate = groundedness + Recall@k vs held-out picks.
2. **Single grounded prompt on a frontier mini (`gpt-4o-mini`), behind a provider-agnostic route.**
   Opinion-framed dossier from `build_advisor_context.py`; constrained JSON; cite `recordId`;
   validate-and-repair. Get all three eval axes green.
3. **A/B swap in Groq Llama 3.1 8B.** Keep it only if groundedness/citation/refusal hold within
   tolerance vs the mini; else hybrid (8B common path, mini fallback). Lock the steady-state ~$1–2/mo.
4. **KB schema v2 + pro review loop.** Add phase/win-condition/ban-priority fields; pros review the
   llm-draft seed (10× cheaper than blank authoring); confidence upgrades to `pro`. Re-run eval —
   this is where expert-match Recall@k should climb.
5. **Patch-drift automation.** Wire the `patchVersion`-tagged golden rows into the coverage-drift
   trigger; a new patch flags stale rows for re-label and badges stale KB in the UI.
6. **(Deferred) embedding rerank for long-form prose notes** — only if key-filtered prose per
   (map, mode) regularly exceeds the budget; rerank within the key-filtered set, never globally.

---

### Notes / corrections logged

- **Fly.io GPU is deprecated (July 31, 2026)** — update CLAUDE.md's "Fly.io ~$5/mo for the advisor"
  and kb-design §7's "runs on the existing Fly.io box" (the box stays for the CPU sync server +
  stats collector; GPU serving moves to serverless).
- Several pricing figures come from aggregator/blog sources (provider pages gate behind JS); the two
  load-bearing ones — **Groq 8B $0.05/$0.08** and **Fly.io GPU deprecation** — were independently
  re-verified. Cerebras moved to subscription tiers in 2026; treat its per-token numbers as
  2024–2025 reference only.
- A few quantitative claims from arXiv PDFs that only parsed via abstract/HTML (long-context deltas,
  best-case faithfulness percentages, the Qwen2.5-7B FaithBench category figure) are directional, not
  exact — don't quote the 70%-category number as a general hallucination rate.
```
