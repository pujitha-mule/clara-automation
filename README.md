# Clara Answers – Zero-Cost Onboarding Automation Pipeline

## Overview

This project implements a fully automated, zero-cost onboarding pipeline that converts demo and onboarding call transcripts into structured Retell agent configurations.

It simulates Clara’s real production workflow:

**Demo Call → Preliminary Agent (v1)**  
**Onboarding Update → Versioned Agent Revision (v2, v3, …)**

The system is:

- Deterministic  
- Idempotent  
- Version-controlled  
- Batch-capable  
- Fully reproducible  
- Zero-cost (no paid APIs or LLMs used)

This implementation behaves like a small internal onboarding automation product rather than a one-off script.

---

# Architecture

## Pipeline A – Demo → v1

For each demo transcript inside:

```
dataset/demo/
```

The system:

1. Extracts structured account data using rule-based logic  
2. Validates against a strict schema  
3. Generates `memo.json`  
4. Generates `agent_spec.json`  
5. Saves output under:

```
outputs/accounts/<account_id>/v1/
```

### Account ID Strategy

The system extracts the company name from the transcript and converts it into a deterministic `account_id` using slug formatting.

Example:
```
"Metro Fire Systems" → metro_fire_systems
```

This ensures:

- Idempotent processing  
- No duplicate accounts  
- Clean folder structure  
- Safe re-runs  

Already processed demo accounts are skipped automatically.

---

## Pipeline B – Onboarding → Versioned Update

For each onboarding transcript inside:

```
dataset/onboarding/
```

The system:

1. Derives `account_id` from filename  
   Example:
   ```
   onboarding_metro_fire_systems.txt → metro_fire_systems
   ```

2. Loads the latest version (v1, v2, v3…)  
3. Extracts structured updates into a patch object  
4. Applies field-level updates only to changed fields  
5. Creates the next version folder:

```
v2/
v3/
v4/
```

6. Regenerates `agent_spec.json`  
7. Generates a structured changelog:
   ```
   changes_v2.md
   ```

If onboarding arrives for an unknown account, the system logs a safe warning without breaking execution.

---

# Version Semantics

- **v1 (Demo-derived):** Exploratory configuration based strictly on what is explicitly mentioned during the demo call.
- **v2+ (Onboarding-derived):** Operationally confirmed configuration that overrides demo assumptions while preserving version history.

This separation mirrors Clara’s real onboarding lifecycle and prevents silent assumption drift.

---

# Data Integrity Policy (No Hallucination)

The system never invents or assumes missing configuration details.

If information is not explicitly stated in the transcript:

- Fields remain structured-null (within a strict schema)
- Missing details are added to `questions_or_unknowns`
- No defaults are silently applied

This ensures safe configuration generation and prevents hallucinated operational rules.

---

# Schema Discipline

All account data follows a strict structured schema.

Onboarding updates are first extracted into a `patch` object and then merged field-by-field into the latest version.

The system never regenerates the entire memo blindly.

This preserves configuration stability and enables safe version evolution.

---

# Folder Structure

```
dataset/
    demo/
    onboarding/

outputs/
    accounts/
        <account_id>/
            v1/
                memo.json
                agent_spec.json
            v2/
                memo.json
                agent_spec.json
                changes_v2.md

scripts/
    extract_demo.py
    process_onboarding.py
    generate_agent_spec.py

README.md
.gitignore
```

---

# How To Run

## Step 1 – Process Demo Calls

```bash
python scripts/extract_demo.py
```

Creates `v1` for all demo transcripts.

---

## Step 2 – Process Onboarding Updates

```bash
python scripts/process_onboarding.py
```

Creates the next version automatically (v2, v3, etc.).

The system is batch-capable and processes all transcripts in the respective folders.

---

# Idempotency

Running pipelines multiple times:

- Does not duplicate data  
- Does not recreate versions unnecessarily  
- Skips already processed demo accounts  
- Detects “No changes” for onboarding  

This ensures safe re-execution in production-like environments.

---

# Prompt Hygiene

Generated `agent_spec.json` includes:

- Business hours flow  
- After-hours flow  
- Emergency confirmation logic  
- Transfer protocol  
- Fallback protocol  
- Professional voice style  

No hallucinated values are inserted.

If data is missing, it is clearly marked as:

```
"Not specified"
```

---

# Error Handling

The system safely handles:

- Unknown accounts  
- Missing demo transcripts  
- Missing previous versions  
- No changes detected  
- Safe re-runs  

Errors are logged without breaking batch execution.

---

# Zero-Cost Implementation

- No paid APIs  
- No paid LLM usage  
- Pure Python implementation  
- Rule-based extraction  
- Fully reproducible locally  

The entire pipeline can be executed without external subscriptions.

---

# Limitations

- Rule-based extraction (not ML-based)  
- Limited NLP pattern coverage  
- No UI dashboard (CLI-based execution)

---

# Future Improvements (Production Vision)

With production access, improvements would include:

- Structured onboarding form ingestion  
- Diff visualization UI  
- Supabase-backed persistent storage  
- Webhook-triggered automation  
- LLM-based semantic extraction (controlled environment)  
- Retell API auto-deployment  

---

# What This Demonstrates

- Systems thinking  
- Version-controlled architecture  
- Deterministic automation design  
- Safe configuration lifecycle management  
- Production-aware engineering decisions  

This implementation reflects how an internal onboarding automation engine would be designed for reliability and scale.
