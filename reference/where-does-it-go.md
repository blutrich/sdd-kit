# Reference: Where Does It Go?

The single question that decides where a decision belongs: **is it
technology-independent or technology-dependent?**

- Technology-independent (true regardless of framework/language/DB) →
  `domain-spec.md`
- Technology-dependent (specific to your stack choices) → `engineering-spec.md`
- Sequencing (what gets built when) → `roadmap.md`
- Per-feature scope/decisions/criteria → `requirements.md`
- Per-feature task sequence → `plan.md`
- Per-feature completion proof → `validation.md`

A confidence threshold of 0.6 is technology-independent — it's a business rule
that exists whether you build in FastAPI or Rails. The fact that you implement it
with a specific ORM query is technology-dependent.

| Content | File |
|---|---|
| What the system does | domain-spec.md |
| Domain workflow and states | domain-spec.md |
| Which transitions/failures must be observable | domain-spec.md |
| Business rules and conditions | domain-spec.md |
| "Unknown is never success" invariant | domain-spec.md |
| Stakeholder requirements | domain-spec.md |
| Top-line KPIs and success metrics | domain-spec.md |
| Technology choices | engineering-spec.md |
| API endpoints and contracts | engineering-spec.md |
| Data schemas (DB, Pydantic, TypeScript) | engineering-spec.md |
| Algorithms (computational steps) | engineering-spec.md |
| Pipeline implementation | engineering-spec.md |
| Error handling (incl. external-dependency/quota failures) | engineering-spec.md |
| Observability/instrumentation design (the seam + invariants) | engineering-spec.md |
| Dependencies and project layout | engineering-spec.md |
| What gets built when | roadmap.md |
| Feature scope and decisions | requirements.md |
| Feature success criteria | requirements.md |
| Observability impact (per feature) | requirements.md |
| Failure modes & unknowns (per feature) | requirements.md |
| Analytics events + metered-call usage (definition) | requirements.md |
| Implementation task sequence | plan.md |
| How to verify completion | validation.md |
| Grounding evidence + real-data Definition of Done | validation.md |
| Analytics/observability + failure/unknown verification | validation.md |

## The right level of detail

- **Too much (oversteer):** variable names, function signatures, exact CSS. The
  agent's job.
- **Too little (underdetermined):** "Build authentication." "Add a form."
  Nothing to anchor on.
- **Right level:** "No client-side JS — form submits via standard HTML POST.
  POST/redirect/GET pattern. Email is optional, stored as nullable. Rating
  accepts only 1–5 as an integer."

The test: if the agent could reasonably make two different choices at a decision
point, that decision belongs in the spec.
