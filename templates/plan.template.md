# Plan — <YYYY-MM-DD-feature-name>

> How to build it. The agent executes this sequentially. Numbered task groups,
> each with a theme. Concrete steps referencing real file paths — specific enough
> that there's no ambiguity about what to create, not so granular you're
> specifying variable names (that's the agent's job).

## 1. Database
- [ ] <schema change / migration / seed data / type definition / CRUD helper>
- [ ] …

## 2. Components
- [ ] <UI component / prop / rendering / empty state>
- [ ] …

## 3. Page & Route
- [ ] <page composition / GET + POST handlers / router registration>
- [ ] …

## 4. Navigation
- [ ] <link the feature into existing navigation>

## 5. Tests (always last)
- [ ] <unit / integration / component test>
- [ ] At least one test that exercises real collaborators (doesn't mock both
      ends) and asserts the result persists and reads back.

---

<!-- Instrumentation is part of the task group that owns the behavior, NOT a
bolt-on. When a group adds an action, delivery, or external call that the
Observability Impact named, the recording/emit for it is a step IN that group.
Wiring observability in last is how it gets dropped. -->
