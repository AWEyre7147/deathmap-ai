# Specification structure

Status: adopted for local template organization; lifecycle rules remain pending.

Keep the authoritative specification set small:

| Document             | Responsibility                                                                |
| -------------------- | ----------------------------------------------------------------------------- |
| Project vision       | Purpose, scientific target, outcomes, exclusions and success criteria         |
| Module specification | Entity boundaries, evidence rules, inputs/outputs and supported behavior      |

Use the established project-vision and module-specification section structures.
Keep each template standalone: no links to or requirements to consult other
documents. Fill placeholders with project-specific content; do not present
unresolved assumptions as accepted requirements.

A current-work-session specification is not part of this template structure.
An AI agent may record session activity as a log; a log is a record of actions
and outcomes, not an additional specification or source of new authorization.

Keep iteration notes, decisions, research and open questions in development.
Keep reusable collaboration rules and writing standards in workflow.
Rules for when to create new versions, revise existing specifications, add
specifications or retire superseded specifications are still to be agreed.
Do not infer automatic versioning or migration rules from this structure.

Distinguish an accepted specification from a draft. An idea note, research result
or assistant recommendation does not authorize implementation. A new-session
handoff should identify accepted decisions, unresolved questions and exactly
what the next agent may do.
