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

---

# Architecture

## Pipeline A – Demo → v1

For each demo transcript inside:

```
dataset/demo/
```

The system:

1. Extracts structured account data (rule-based extraction)
2. Generates `memo.json`
3. Generates `agent_spec.json`
4. Saves output under:

```
outputs/accounts/<account_id>/v1/
```

### Account ID Strategy

The system automatically extracts the company name from the transcript and converts it into a deterministic `account_id` using slug formatting.

Example:
```
"Metro Fire Systems" → metro_fire_systems
```

This ensures:

- Idempotent processing  
- No duplicate accounts  
- Clean folder structure  
- Safe re-runs  

Already processed demo accounts are skipped.

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
3. Extracts structured updates:
   - Business hours
   - Emergency triggers
   - Transfer timeouts
   - Integration constraints
4. Applies a patch only to changed fields
5. Creates next version folder:

```
v2/
v3/
v4/
```

6. Regenerates `agent_spec.json`
7. Saves structured changelog:

```
changes_v2.md
```

If onboarding arrives for an unknown account, the system logs a safe warning.

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

This creates `v1` for all demo transcripts.

---

## Step 2 – Process Onboarding Updates

```bash
python scripts/process_onboarding.py
```

This creates the next version automatically (v2, v3, etc.).

---

# Key Design Decisions

## Deterministic Account Mapping

Onboarding files follow the naming convention:

```
onboarding_<account_id>.txt
```

This ensures:

- No fragile transcript parsing
- Fully deterministic mapping
- Safe automation
- Clean batch processing

---

## Version Lifecycle Management

The system:

- Never overwrites old versions
- Always loads latest version
- Auto-increments version numbers
- Generates versioned changelogs

Example:

```
v1 → v2 → v3
```

---

## Idempotency

Running pipelines multiple times:

- Does not duplicate data
- Does not recreate versions unnecessarily
- Skips already processed demo accounts
- Detects "No changes" for onboarding

---

## Zero-Cost Implementation

- No paid APIs
- No paid LLM usage
- Pure Python implementation
- Rule-based extraction
- Fully reproducible locally

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
Missing values are marked as:

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

This implementation behaves like a small internal onboarding automation product rather than a one-off script.
