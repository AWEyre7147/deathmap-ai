# ChatGPT–Perplexity workflow

## [WF-6] Current owner-led native-interface workflow, 2026-10-07

The current sequence is in [repository research](../resources/README.md), following [handoff 17](../specifications/18%20Repository%20Native%20Discovery%20Release%20Preparation.md). Start with one repository's native filter menu and your chosen values. Bring the literal browser search, counts and a few representative records when available. ChatGPT checks programmatic equivalence and drafts a small implementation contract. Use Perplexity for targeted documentation gaps as needed; the four-file OmicsDI inquiry below is historical and should not be resent as the current task. Finding cards remain useful for preserving source evidence and decisions.

## [WF-1] What the owner does now
Give Perplexity the contents or attachments of these four files:
1. docs/development/v02 - ORCS refinement + OmicsDi/Perplexity research request.md — the task and limits.
2. docs/development/v02 - ORCS refinement + OmicsDi/Implementation baseline.md — current code status, including subsequent retirement.
3. docs/development/v02 - ORCS refinement + OmicsDi/Repository coverage.md — seven primary families and deferred sources.
4. docs/workflow/finding-cards/Finding Card Instructions.md — evidence and card format.

Include any existing F-numbered cards. If none exist, say so. Local paths alone do not give Perplexity access; attach or paste actual contents. Archived field guides are optional source evidence: supply relevant excerpts if accessible, or tell Perplexity they were not supplied. Do not require Perplexity to access the external archive independently.

Ask it to return Markdown cards, the seven-family capability matrix with card IDs, and the short completion handoff required by the instructions. It must disclose partial coverage and unavailable materials. No full search, benchmark run or implementation is requested.

## [WF-2] What to bring back
Bring all returned cards, the capability matrix, and the completion summary into this ChatGPT chat, plus any supplied response evidence files. Attach them or paste their contents. You may save card files under docs/workflow/finding-cards, but you do not need to manually file them: ask ChatGPT to save attached cards there. If Perplexity cannot create files, pasted Markdown is sufficient.

Do not mark cards Accepted merely to transfer them. New findings remain Proposed unless you explicitly review them. When starting another research task, supply the existing card IDs so identifiers are not reused.

## [WF-3] What ChatGPT does next
Read and catalog the findings; check citations/evidence and compare them with the implementation baseline. Separate source facts from proposed scientific or engineering rules. Identify contradictions, gaps and the smallest useful next implementation step. Return only the questions that need owner scientific or scope decisions. Draft any follow-up research request so the owner can transfer it without reconstructing the context.

Do not implement until the owner approves the concrete implementation handoff. Acceptance of a source observation is not authorization to code.

## [WF-4] What the owner decides
Review scientific eligibility, screen-group meaning, attribution requirements and material scope choices when they arise. Reply using stable point/card IDs. The owner need not adjudicate every API field or manually synthesize the matrix; ChatGPT handles that comparison and surfaces material uncertainty.

For this immediate capability inquiry, no new scientific eligibility decision is required. Wait for findings before choosing the first source/filter route.

## [WF-5] Completion and learning checkpoint
The research exchange is complete when findings are accessible here, uncertainties are explicit, and a small implementation proposal is ready for owner review. The owner transports information between systems; the finding cards preserve why a proposed change is justified. There is no automatic communication or shared local filesystem between assistants.
