---
field: "ENZYME"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 20
description_basis: "hand-authored by Perplexity; review recommended"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# ENZYME

## Technical definition

Cas enzyme or effector construct used (free text).

## Plain-language description

Which CRISPR protein tool was used.

## Where it goes in DeathMap

Screens.enzyme_reported


## Values

| Value | Screens | Technical description | Plain-language description | Normalized candidate |
|---|---:|---|---|---|
| `Cas9` | 2054 | Streptococcus pyogenes Cas9 nuclease (SpCas9), the standard knockout enzyme. | The standard CRISPR 'scissors' that cut DNA at the spot a guide points to. | knockout |
| `dCas9-KRAB` | 39 | dCas9 fused to the KRAB transcriptional repressor domain (standard CRISPRi). | A non-cutting CRISPR tool attached to an 'off switch' that turns genes down. | interference |
| `dCAS-VP64_Blast (Zhu, 2021)` | 26 | dCas9-VP64 activator in a blasticidin-selectable vector, as described by Zhu et al. 2021 (CRISPRa). | A CRISPR 'on switch' tool from a specific 2021 study. | activation |
| `SAM (NLS-dCas9-VP64/MS2-p65-HSF1)` | 25 | Synergistic Activation Mediator: dCas9-VP64 plus MS2-recruited p65-HSF1 activators (CRISPRa). | A strong CRISPR 'on switch' system that recruits several activator parts at once. | activation |
| `BE3` | 11 | Third-generation cytosine base editor (APOBEC1-nCas9-UGI), converts C:G to T:A. | A tool that swaps one DNA letter (C to T) without cutting both strands. | base_editing |
| `dCas9-VP64` | 9 | dCas9 fused to the VP64 transcriptional activator (first-generation CRISPRa). | A non-cutting CRISPR tool attached to an 'on switch' that turns genes up. | activation |
| `Cas9-v2` | 8 | SpCas9 delivered in a study-specific vector, version 2. | The standard CRISPR scissors, in a particular delivery version. | knockout |
| `dCas9-BFP-KRAB` | 8 | dCas9-KRAB with a BFP fluorescent marker. | The CRISPR 'off switch' tool, labeled with a blue glowing tag. | interference |
| `AncBE4max` | 6 | Optimized cytosine base editor (ancestral APOBEC, BE4max architecture). | An improved tool that swaps one DNA letter (C to T). | base_editing |
| `Cas9-v1` | 5 | SpCas9 delivered in a study-specific vector, version 1. | The standard CRISPR scissors, in a particular delivery version. | knockout |
| `sunCas9` | 5 | dCas9-SunTag CRISPRa system (ORCS label). | A CRISPR 'on switch' that attaches many activator copies to one spot. | activation |
| `dCas9-SunTag-P2A-HygR` | 4 | dCas9-SunTag scaffold recruiting multiple scFv-VP64 activators (CRISPRa). | A CRISPR 'on switch' that attaches many activator copies to one spot. | activation |
| `iCAS9` | 4 | Inducible Cas9 (expression switched on by a drug such as doxycycline). | CRISPR scissors that can be switched on at a chosen time. | knockout |
| `dCas9` | 3 | Catalytically dead Cas9 (no cutting); used here with separate activator components. | A CRISPR tool that can find a gene but cannot cut it; extra parts make it turn genes up. | activation |
| `dCas9-Mxi repressor domain` | 3 | dCas9 fused to the Mxi1 repressor domain (CRISPRi). | A CRISPR 'off switch' using a different repressor part. | interference |
| `dCas9-VP64 & p65-HSF1 (CRISPR SAM)` | 2 | SAM CRISPRa system (alternate ORCS spelling). | Same as the SAM 'on switch' system. | activation |
| `dCas9-VP64 + PP7-P65-HSF1` | 2 | dCas9-VP64 with PP7-recruited p65-HSF1 activators (SAM-like CRISPRa). | A SAM-like CRISPR 'on switch' system. | activation |
| `AsCpf1` | 1 | Acidaminococcus Cas12a (Cpf1) nuclease; uses different guide design and supports multiplexed guides. | A different type of CRISPR scissors that can cut several targets at once. | knockout |
| `Cas12a` | 1 | Cas12a (Cpf1) nuclease. | A different type of CRISPR scissors. | knockout |
| `dCas9–VPR` | 1 | dCas9 fused to the tripartite VP64-p65-Rta activator (CRISPRa). | A strong CRISPR 'on switch' built from three activator parts. | activation |
