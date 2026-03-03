Clara Answers – Zero-Cost Onboarding Automation Pipeline
Overview

This project implements a fully automated, zero-cost onboarding pipeline that converts demo and onboarding call transcripts into structured Retell agent configurations.

It simulates Clara’s real production workflow:

Demo Call → Preliminary Agent (v1)
Onboarding Update → Versioned Agent Revision (v2, v3, …)

The system is deterministic, idempotent, version-controlled, and batch-capable.

No paid APIs or external LLMs were used.

Architecture
Pipeline A – Demo → v1

For each demo transcript in:

dataset/demo/

The system:

Extracts structured account data (rule-based)

Generates memo.json

Generates agent_spec.json

Saves under:

outputs/accounts/<account_id>/v1/

The system auto-detects the company name from transcript and slugifies it into a deterministic account_id.

It skips already processed accounts (idempotent behavior).

Pipeline B – Onboarding → Versioned Update

For each onboarding transcript in:

dataset/onboarding/

The system:

Derives account_id from filename
Example:

onboarding_metro_fire_systems.txt
→ metro_fire_systems

Loads latest version (v1, v2, v3…)

Extracts updates (business hours, emergency triggers, transfer timeout, etc.)

Applies patch only to changed fields

Creates next version folder:

v2/
v3/
v4/

Regenerates agent_spec from updated memo

Saves versioned changelog:

changes_v2.md

If onboarding arrives for unknown account, system logs warning safely.

Folder Structure
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
How To Run
Step 1 – Process Demo Calls
python scripts/extract_demo.py

Creates v1 for all demo transcripts.

Step 2 – Process Onboarding Updates
python scripts/process_onboarding.py

Creates new version automatically.

Key Design Decisions
Deterministic Account Mapping

Onboarding files use naming convention:

onboarding_<account_id>.txt

This ensures:

No fragile transcript parsing

Fully deterministic mapping

Safe automation

Version Lifecycle Management

The system:

Never overwrites old versions

Always loads latest version

Auto-increments version numbers

Generates versioned changelogs

Example:

v1 → v2 → v3
Idempotency

Running pipelines multiple times:

Does not duplicate data

Does not recreate versions unnecessarily

Skips already processed demo accounts

Detects “No changes” for onboarding

Zero-Cost Implementation

No paid APIs

No paid LLM usage

Pure Python

Rule-based extraction

Fully reproducible

Prompt Hygiene

Generated agent_spec includes:

Business hours flow

After-hours flow

Emergency confirmation logic

Transfer protocol

Fallback protocol

Professional voice style

No hallucinated values are inserted.
Missing values are marked as “Not specified”.

Error Handling

The system safely handles:

Unknown accounts

Missing demo transcripts

Missing versions

No changes detected

Re-runs

Limitations

Rule-based extraction (not ML-based)

Limited NLP pattern coverage

No UI dashboard (CLI-based execution)

Future Improvements (Production Vision)

With production access, improvements would include:

Structured onboarding form ingestion

Diff visualization UI

Supabase-backed persistent storage

Webhook-triggered automation

LLM-based semantic extraction (controlled environment)

Retell API auto-deployment

What This Demonstrates

Systems thinking

Version control architecture

Deterministic automation design

Safe configuration lifecycle management

Production-aware engineering decisions

This implementation behaves like a small internal onboarding automation product.