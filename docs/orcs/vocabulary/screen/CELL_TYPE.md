---
field: "CELL_TYPE"
entity: screen
source: BioGRID ORCS cached metadata (data/orcs/screen-index.json, 2,217 screens, retrieved 2026-09-04)
unique_values: 145
description_basis: "Perplexity rule-based + hand-authored"
generated: 2026-10-04
generated_by: Perplexity (DeathMap-AI vocabulary pass v1)
tags: [deathmap-ai, orcs, vocabulary, screen]
---

# CELL_TYPE

## Technical definition

ORCS free-text description of the cell line's tissue or disease origin.

## Plain-language description

A short description of what kind of cell was used, such as 'Melanoma Cell Line' (skin cancer cells).

## Where it goes in DeathMap

Screens.disease_context_normalized (candidate); supports the cancer-cell fallback in profile v02


`Cancer-derived` is the value used by the profile v02 fallback: `yes` = cancer by name; `no` = not cancer; `check` = ORCS uses the label for both cancer and non-cancer lines.

## Values

| Value | Screens | Cancer-derived | Plain-language description |
|---|---:|---|---|
| `acute lymphoblastic leukemia cell line` | 7 | yes | Lab-grown cancer cells; a fast-growing blood cancer of immature lymphocytes. |
| `Acute Myeloid Leukemia Cell Line` | 67 | yes | Lab-grown cancer cells; a fast-growing blood cancer of myeloid cells, which normally become certain white blood cells. |
| `Adrenal Gland Neuroblastoma` | 2 | yes | Lab-grown cancer cells; a childhood cancer of developing nerve cells. |
| `African green monkey kidney cell line` | 34 | no | Monkey kidney cells (e.g., Vero), mostly used to grow viruses. |
| `Anaplastic Large Cell Lymphoma Cell Line` | 1 | yes | Lab-grown cancer cells; a cancer of lymphocytes, a type of immune cell. |
| `Anaplastic Thyroid Cancer Cell Line` | 1 | yes | Lab-grown cancer cells; a cancer. |
| `Askin Tumor` | 1 | yes | Lab-grown cancer cells; a nerve-related tumor in the Ewing sarcoma family. |
| `Astrocytoma Cell Line` | 7 | yes | Lab-grown cancer cells; a brain cancer that starts in glial cells, the support cells of the brain. |
| `B-cell non-Hodgkin lymphoma cell line` | 3 | yes | Lab-grown cancer cells; a lymphoma (cancer of lymphocytes). |
| `B-lymphoblastoid cell line` | 2 | no | B cells (antibody-making immune cells) made to grow forever by Epstein-Barr virus; not from a tumor. |
| `B-lymphoma cell line` | 4 | yes | Lab-grown cancer cells; a cancer of lymphocytes, a type of immune cell. |
| `Bladder Carcinoma` | 10 | yes | Lab-grown cancer cells; a cancer that starts in the cells lining organs or skin. |
| `Bladder Transitional Cell Carcinoma Cell Line` | 3 | yes | Lab-grown cancer cells; a cancer of the lining of the bladder or urinary tract. |
| `bone marrow cell line` | 1 | no | Bone-marrow cells. |
| `Breast Adenocarcinoma Cell Line` | 29 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Breast Cancer Cell Line` | 37 | yes | Lab-grown cancer cells; breast cancer. |
| `breast epithelium` | 3 | no | Non-cancer breast-lining cells. |
| `Burkitt Lymphoma Cell Line` | 13 | yes | Lab-grown cancer cells; a fast-growing B-cell lymphoma. |
| `Caki-1` | 1 | yes | Cancer cell line (renal cell carcinoma): a kidney cancer. |
| `Cancer Cell Line` | 103 | yes | Lab-grown cancer cells; a cancer. |
| `cardiac muscle cell line` | 2 | no | Heart muscle cells. |
| `Cecum Cancer Cell Line` | 8 | yes | Lab-grown cancer cells; a cancer. |
| `Cervical Adenocarcinoma Cell Line` | 62 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `cervical squamous cell carcinoma` | 3 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Cholangiocarcinoma Cell` | 1 | yes | Lab-grown cancer cells; a bile-duct cancer. |
| `Chondrosarcoma` | 1 | yes | Lab-grown cancer cells; a cartilage cancer. |
| `Chronic Myelogenous Leukemia Cell Line` | 72 | yes | Lab-grown cancer cells; a slow-growing blood cancer of myeloid cells, usually driven by the BCR-ABL gene fusion. |
| `Chronic Myeloid Leukemia Cell Line` | 74 | yes | Lab-grown cancer cells; a slow-growing blood cancer of myeloid cells, usually driven by the BCR-ABL gene fusion. |
| `Colonic Adenocarcinoma Cell Line` | 46 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Colonic Cancer Cell Line` | 36 | yes | Lab-grown cancer cells; a cancer. |
| `Colorectal Adenocarcinoma Cell Line` | 4 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Colorectal Cancer Cell Line` | 25 | yes | Lab-grown cancer cells; a cancer. |
| `Cytotoxic T-lymphocyte (CD8+ T cells)` | 2 | no | Killer T cells: immune cells that destroy infected or cancer cells. Here they are the cells being changed, not the target. |
| `Diffuse Large B-cell Lymphoma Cell` | 13 | yes | Lab-grown cancer cells; the most common aggressive B-cell lymphoma. |
| `Drosophila melanogaster cell line` | 3 | no | Fruit fly cells. |
| `Embryonic Cell Line` | 5 | no | Cells from an embryo. |
| `Embryonic Fibroblast Cell Line` | 15 | no | Connective-tissue cells from an embryo (often mouse MEFs). |
| `Embryonic Kidney Cell Line` | 101 | no | HEK293-type cells: human embryonic kidney cells transformed in the lab; used as an easy-to-grow workhorse, not a cancer model. |
| `Embryonic Stem Cell Line` | 5 | no | Embryonic stem cells, which can become any cell type. |
| `Endometrial Cancer Cell Line` | 17 | yes | Lab-grown cancer cells; a cancer. |
| `Eosinophilic Leukemia Cell Line` | 1 | yes | Lab-grown cancer cells; a blood cancer of eosinophils, a white blood cell type. |
| `Epstein-Barr Virus (EBV)+ Burkitt lymphoma cell line (EBV latency I state)` | 3 | yes | Lab-grown cancer cells; a fast-growing B-cell lymphoma. |
| `Epstein-Barr Virus (EBV)+ lymphoblastoid cell line (EBV latency III state)` | 1 | no | B cells made to grow forever by Epstein-Barr virus, in a specific viral state. |
| `Erythroleukemia Cell Line` | 9 | yes | Lab-grown cancer cells; a blood cancer of red-blood-cell precursors. |
| `Esophageal Cancer Cell Line` | 12 | yes | Lab-grown cancer cells; a cancer. |
| `Esophageal Squamous Cell Carcinoma Cell Line` | 18 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Ewing's Sarcoma Cell Line` | 9 | yes | Lab-grown cancer cells; a bone or soft-tissue cancer that mostly affects children and young adults. |
| `Fibroblast Cell Line` | 5 | no | Connective-tissue cells (fibroblasts). |
| `Fibrosarcoma Cell Line` | 3 | yes | Lab-grown cancer cells; a cancer of connective-tissue cells called fibroblasts. |
| `forebrain assembloids (hFA)` | 1 | no | Combined mini-brain tissues grown in 3D. |
| `Gall Bladder Cancer Cell Line` | 1 | yes | Lab-grown cancer cells; a cancer. |
| `Gastric Adenocarcinoma Cell Line` | 10 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Gastric Cancer Cell Line` | 11 | yes | Lab-grown cancer cells; a cancer. |
| `Gastric tumor organoid model` | 5 | yes | Lab-grown cancer cells; a cancer. |
| `Gingival Cancer Cell Line` | 1 | yes | Lab-grown cancer cells; a cancer. |
| `Glioblastoma Cell Line` | 67 | yes | Lab-grown cancer cells; the most aggressive type of brain cancer. |
| `Glioma Cell Line` | 25 | yes | Lab-grown cancer cells; a brain cancer that starts in glial cells, the support cells of the brain. |
| `Gliosarcoma` | 2 | yes | Lab-grown cancer cells; a brain cancer with glial and connective-tissue parts. |
| `Head and Neck Squamous Cell Carcinoma Cell Line` | 6 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `HeLa` | 7 | yes | Cancer cell line (cervical adenocarcinoma): a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Hepatitis B virus genome integrated cell line` | 4 | no | Liver-derived cells carrying hepatitis B virus DNA. |
| `Hepatoblastoma Cell Line` | 1 | yes | Lab-grown cancer cells; a childhood liver cancer. |
| `Hepatocellular Carcinoma` | 2 | yes | Lab-grown cancer cells; a liver cancer. |
| `Hepatoma Cell Line` | 55 | yes | Lab-grown cancer cells; a liver cancer. |
| `hiPSC-derived astrocyte` | 6 | no | Brain support cells (astrocytes) made from stem cells. |
| `HIV-1 Latency Cell Line` | 1 | no | Cells carrying a dormant HIV infection, used to study how HIV hides. |
| `Huh-7 Cell` | 22 | yes | Cancer cell line (hepatocellular carcinoma): a liver cancer. |
| `Hypopharyngeal Squamous Cell Carcinoma Cell Line` | 3 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Immortal Cell Line` | 1 | no | Cells made to grow indefinitely in the lab. |
| `immortal human bone marrow-derived cell line` | 1 | no | Bone-marrow cells made to grow indefinitely. |
| `Immortal Human Peripheral Neuron Cell Line` | 1 | no | Human nerve cells made to grow indefinitely. |
| `Immortal mouse chromaffin cells` | 1 | no | Mouse adrenal (hormone-releasing) cells made to grow indefinitely. |
| `Immortal Mouse Liver-derived Cell Line` | 2 | no | Mouse liver cells made to grow indefinitely. |
| `Intestinal organoid model` | 4 | no | Mini-intestines grown in 3D from stem cells. |
| `iPSC derived cell line` | 2 | no | Cells made from induced pluripotent stem cells. |
| `Kidney Cell Line` | 3 | no | Kidney cells. |
| `Large Cell Lung Cancer Cell Line` | 9 | yes | Lab-grown cancer cells; a cancer. |
| `Liver cell line` | 1 | no | Liver cells. |
| `Lung Adenocarcinoma Cell Line` | 57 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Lung Cancer Cell Line` | 99 | yes | Lab-grown cancer cells; a cancer. |
| `Lung Squamous Cell Carcinoma Cell Line` | 17 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Lymphoblastoid Cell Line` | 1 | no | B cells made to grow forever by Epstein-Barr virus; not from a tumor. |
| `Lymphoma Cell Line` | 54 | yes | Lab-grown cancer cells; a cancer of lymphocytes, a type of immune cell. |
| `Lymphoma or Leukaemia Cell Line` | 23 | yes | Lab-grown cancer cells; a blood cancer that starts in the bone marrow. |
| `macrophage` | 4 | no | Macrophages, immune cells that swallow ('eat') debris, microbes, and sometimes cancer cells. |
| `Malignant Peripheral Nerve Sheath Tumor (MPNST) cancer cell` | 3 | yes | Lab-grown cancer cells; a cancer of the protective covering around nerves. |
| `Mammary Epithelial Cell Line` | 71 | check | Breast-lining cells. Often non-cancer (e.g., HMEC, MCF-10A), but ORCS also uses this label for some cancer lines, so check the cell line. |
| `Mammary Gland Tumor Cell Line` | 23 | yes | Lab-grown cancer cells; breast cancer. |
| `MDA-MB-435 cell` | 1 | yes | Cancer cell line (melanoma (originally labeled breast cancer)): a cancer of pigment-making skin cells. |
| `Medulloblastoma Cell Line` | 7 | yes | Lab-grown cancer cells; a childhood brain cancer in the cerebellum. |
| `Melanoma Cell Line` | 100 | yes | Lab-grown cancer cells; a cancer of pigment-making skin cells. |
| `Meningioma Cell Line` | 1 | yes | Lab-grown cancer cells; a tumor of the brain's protective membranes. |
| `Microglial Cell Line` | 16 | no | Microglia, the immune cells of the brain. |
| `microvascular endothelial cell line` | 2 | no | Cells lining small blood vessels. |
| `Monocytic Leukemia Cell Line` | 25 | yes | Lab-grown cancer cells; a blood cancer of monocytes, the precursors of macrophages. |
| `Mouse cell` | 2 | no | Mouse cells (unspecified). |
| `Mouse Embryonic Stem Cell` | 1 | no | Mouse embryonic stem cells. |
| `Mouse kidney carcinoma cell` | 12 | yes | Lab-grown cancer cells; a cancer that starts in the cells lining organs or skin. |
| `Multiple Myeloma Cell Line` | 6 | yes | Lab-grown cancer cells; a cancer of plasma cells, the immune cells that make antibodies. |
| `myoblast cell line` | 7 | no | Muscle precursor cells. |
| `nasopharyngeal carcinoma cell line` | 1 | yes | Lab-grown cancer cells; a cancer that starts in the cells lining organs or skin. |
| `Neural Stem Cell Line` | 4 | no | Brain stem cells that can become nerve or support cells. |
| `Neuroblastoma Cell Line` | 32 | yes | Lab-grown cancer cells; a childhood cancer of developing nerve cells. |
| `Neuroepithelioma Cell Line` | 1 | yes | Lab-grown cancer cells; a nerve-related tumor in the Ewing sarcoma family. |
| `NMC-G1 cell` | 1 | yes | Cancer cell line (NUT midline carcinoma): a rare, aggressive cancer driven by a NUT gene fusion. |
| `Non-Small Cell Lung Adenocarcinoma Cell Line` | 15 | yes | Lab-grown cancer cells; a fast-growing lung cancer of nerve-like cells. |
| `Non-Small Cell Lung Cancer Cell Line` | 25 | yes | Lab-grown cancer cells; a fast-growing lung cancer of nerve-like cells. |
| `Oral Squamous Cell Carcinoma Cell Line` | 26 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Osteosarcoma Cell Line` | 11 | yes | Lab-grown cancer cells; a bone cancer. |
| `Ovarian Cancer Cell Line` | 49 | yes | Lab-grown cancer cells; a cancer. |
| `Ovary Adenocarcinoma Cell Line` | 29 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `OVCAR-8` | 1 | yes | Cancer cell line (ovarian adenocarcinoma): a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Pancreatic Adenocarcinoma Cell Line` | 36 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `pancreatic beta cell line` | 1 | no | Insulin-making pancreas cells. |
| `Pancreatic Cancer Cell Line` | 21 | yes | Lab-grown cancer cells; a cancer. |
| `Pancreatic Cell Line` | 8 | check | Pancreas cells (check whether cancer or normal). |
| `Pancreatic Ductal Adenocarcinoma Cell Line` | 19 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `pancreatic islet` | 1 | no | Insulin-making pancreas tissue. |
| `Pre-B Acute Lymphoblastic Leukemia Cell Line` | 26 | yes | Lab-grown cancer cells; a fast-growing blood cancer of immature lymphocytes. |
| `Pre-B-Lymphocyte Cell Line` | 5 | no | Early-stage B cells. |
| `Primary Effusion Lymphoma Cell Line` | 17 | yes | Lab-grown cancer cells; a rare lymphoma caused by the KSHV virus. |
| `pro-B-lymphocyte` | 1 | no | Early-stage B cells (future antibody-making cells). |
| `Prostate Cancer Cell Line` | 17 | yes | Lab-grown cancer cells; a cancer. |
| `Regulatory T cell` | 10 | no | ORCS label for some primary T-cell screens; regulatory T cells (Tregs) calm down immune responses. Check the source, since ORCS also uses this label for CD8+ T-cell screens. |
| `Renal Cancer Cell Line` | 2 | yes | Lab-grown cancer cells; a cancer. |
| `Renal Cell Carcinoma Cell Line` | 18 | yes | Lab-grown cancer cells; a kidney cancer. |
| `renal medulla cell line` | 1 | no | Inner-kidney cells. |
| `Retinal Pigment Epithelium Cell Line` | 70 | no | RPE1-type cells: normal eye-lining cells made to divide indefinitely; a common non-cancer model. |
| `Rhabdomyosarcoma Cell Line` | 7 | yes | Lab-grown cancer cells; a cancer of cells that normally become muscle. |
| `Saccharomyces cerevisiae` | 25 | no | Yeast. |
| `Salivary Gland Cancer Cell` | 1 | yes | Lab-grown cancer cells; a cancer. |
| `small cell lung cancer` | 4 | yes | Lab-grown cancer cells; a fast-growing lung cancer of nerve-like cells. |
| `Squamous cell carcinoma cell line` | 1 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Subpallial organoid model` | 1 | no | Mini-brain tissue grown in 3D from stem cells. |
| `T cell` | 14 | no | T cells, immune cells that recognize and attack threats. Here they are the cells being changed. |
| `T-lymphoblastic leukemia cell line` | 10 | yes | Lab-grown cancer cells; a fast-growing blood cancer of immature lymphocytes. |
| `T-lymphoma cell line` | 3 | yes | Lab-grown cancer cells; a cancer of lymphocytes, a type of immune cell. |
| `Thoracic SMARCA4-deficient undifferentiated tumor` | 3 | yes | Lab-grown cancer cells; a cancer. |
| `Tongue Cancer Cell Line` | 13 | yes | Lab-grown cancer cells; a cancer. |
| `Umbilical cord erythroid progenitor` | 3 | no | Red-blood-cell precursors from umbilical cord blood. |
| `umbilical vein endothelial cell line` | 1 | no | Cells lining umbilical-cord blood vessels (e.g., HUVEC). |
| `Urinary Bladder Cancer Cell Line` | 7 | yes | Lab-grown cancer cells; a cancer. |
| `Urinary Bladder Squamous Cell Carcinoma Cell Line` | 1 | yes | Lab-grown cancer cells; a cancer of flat surface cells, like those of the skin or the lining of the mouth, lung, or esophagus. |
| `Uterine Adenocarcinoma Cell Line` | 2 | yes | Lab-grown cancer cells; a cancer that starts in gland-forming cells, which make mucus or other fluids. |
| `Uterine Carcinosarcoma Cell Line` | 1 | yes | Lab-grown cancer cells; a mixed cancer with both lining-cell and connective-tissue parts. |
