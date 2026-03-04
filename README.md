# Clara Automation Pipeline

## Table of Contents

- Overview
- Quick Start
- Architecture
- Requirements
- Repository Structure
- How to Run the Pipeline
- Output Structure
- Pipeline Summary Report
- Change Diff Viewer
- Account Memo Schema
- Agent Prompt Behavior
- Retell Agent Draft Specification
- Orchestration Workflow
- Idempotent Execution
- Zero-Cost Design
- Production Deployment Design
- Summary

---

# Overview

This project implements a **zero-cost automation pipeline** that converts demo call transcripts into preliminary AI voice agent configurations and then updates those configurations using onboarding call information.

The pipeline mirrors the operational workflow used during **Clara Answers deployments**:

- A demo call transcript is analyzed to generate an initial Retell agent configuration (**v1**).
- An onboarding call transcript refines the configuration with confirmed operational rules.
- The system produces an updated agent configuration (**v2**) along with a changelog that records what changed.

The pipeline processes a dataset of **5 demo call transcripts and 5 onboarding call transcripts**, generating structured account configurations and versioned agent specifications for each account.

The goal of the system is to convert **unstructured conversations into structured operational logic** that can be used to configure an AI voice agent reliably.

---

# Quick Start

Run the full automation pipeline locally:

```bash
git clone <your_repo_url>
cd clara-automation
python scripts/run_pipeline.py
```

After execution, generated outputs will appear in:

```
outputs/accounts/
```

Each account will contain:

```
v1/  → initial agent configuration generated from demo call
v2/  → updated configuration after onboarding
changes.json → changelog describing updates between versions
```

---

# Architecture

Pipeline stages:

```
                +----------------------+
                | Demo Call Transcript |
                +----------+-----------+
                           |
                           v
                   extract_demo.py
                           |
                           v
                Account Memo JSON (v1)
                           |
                           v
                 generate_agent_spec.py
                           |
                           v
               Retell Agent Draft Spec (v1)
                           |
                           v
                Onboarding Transcript
                           |
                           v
                 process_onboarding.py
                           |
                           v
        Account Memo (v2) + Agent Spec (v2)
                           |
                           v
                 Changelog + Summary
```

Design goals:

- Repeatable execution
- Version-controlled outputs
- Idempotent processing
- Zero-cost tooling

---

# Requirements

- Python **3.9+**
- No external paid APIs or services
- Runs locally using standard Python libraries

---

# Repository Structure

```
clara-automation/

dataset/
  demo/
    demo_001.txt
    demo_002.txt
    demo_003.txt
    demo_004.txt
    demo_005.txt

  onboarding/
    onboarding_acme_electrical_services.txt
    onboarding_evergreen_facilities_maintenance.txt
    onboarding_metro_fire_systems.txt
    onboarding_northside_hvac.txt
    onboarding_prime_sprinkler_co.txt

scripts/
  extract_demo.py
  generate_agent_spec.py
  process_onboarding.py
  run_pipeline.py
  show_changes.py

outputs/
  accounts/
    <account_id>/
      v1/
        account_memo.json
        agent_spec.json
      v2/
        account_memo.json
        agent_spec.json
      changes.json

workflows/
  clara_pipeline.json

README.md
```

---

# How to Run the Pipeline

### 1. Clone the repository

```
git clone <your_repo_url>
cd clara-automation
```

### 2. Place demo transcripts inside

```
dataset/demo/
```

Example:

```
demo_001.txt
demo_002.txt
```

### 3. Place onboarding transcripts inside

```
dataset/onboarding/
```

Files must follow the naming format:

```
onboarding_<account_id>.txt
```

Example:

```
onboarding_metro_fire_systems.txt
```

### 4. Run the pipeline

```
python scripts/run_pipeline.py
```

Pipeline steps:

1. Extract structured account information from demo transcripts  
2. Generate preliminary Retell agent configurations (**v1**)  
3. Process onboarding transcripts to refine configurations  
4. Generate updated agent configurations (**v2**) and changelogs  

---

# Output Structure

Example output for a single account:

```
outputs/accounts/metro_fire_systems/

v1/
  account_memo.json
  agent_spec.json

v2/
  account_memo.json
  agent_spec.json

changes.json
```

### account_memo.json

Contains structured operational information extracted from transcripts.

### agent_spec.json

Contains the generated Retell agent configuration including prompt, routing logic, and transfer behavior.

### changes.json

Tracks updates introduced during onboarding.

---

# Pipeline Summary Report

After the pipeline completes, a summary file is generated:

```
outputs/summary_report.json
```

Example:

```json
{
  "total_accounts": 5,
  "accounts": [
    "acme_electrical_services",
    "evergreen_facilities_maintenance",
    "metro_fire_systems",
    "northside_hvac",
    "prime_sprinkler_co"
  ]
}
```

---

# Change Diff Viewer

To make onboarding updates easier to review, the repository includes a simple **CLI diff viewer**.

This tool reads the `changes.json` file and displays a **human-readable summary of updates between v1 and v2 configurations.**

Run:

```
python scripts/show_changes.py <account_id>
```

Example:

```
python scripts/show_changes.py metro_fire_systems
```

Example output:

```
Account: metro_fire_systems
Version: v1 → v2

Changes Detected

Business Hours
  start: Not specified → 9AM
  end: Not specified → 6PM

Emergency Definitions Added
  sprinkler leak
  fire alarm trigger
```

---

# Account Memo Schema

Each account memo contains structured fields including:

- account_id
- company_name
- business_hours
- office_address
- services_supported
- emergency_definition
- emergency_routing_rules
- non_emergency_routing_rules
- call_transfer_rules
- integration_constraints
- after_hours_flow_summary
- office_hours_flow_summary
- questions_or_unknowns
- notes

If information is missing in transcripts, it is recorded under **questions_or_unknowns** rather than being inferred.

---

# Agent Prompt Behavior

Generated agent prompts follow two primary call flows.

### Business Hours Flow

- Greeting  
- Ask caller purpose  
- Collect name and phone number  
- Route or transfer the call  
- If transfer fails, collect details and notify dispatch  
- Ask if anything else is needed  
- Close call  

### After Hours Flow

- Greeting  
- Ask caller purpose  
- Determine if the request is an emergency  
- If emergency, collect name, number, and address immediately  
- Attempt transfer to emergency contact  
- If transfer fails, assure follow-up  
- If non-emergency, collect request details for the next business day  
- Ask if anything else is needed  
- Close call  

---

# Retell Agent Draft Specification

The pipeline generates a JSON representation of the agent configuration including:

- agent name
- voice style
- system prompt
- business hours and timezone
- emergency routing behavior
- call transfer protocol
- fallback protocol
- configuration version (**v1 or v2**)

This JSON mirrors how a Retell voice agent would be configured in production.

---

# Orchestration Workflow

The repository includes an exported workflow:

```
workflows/clara_pipeline.json
```

This workflow can be imported into **n8n** to demonstrate how the pipeline would run automatically in a production environment.

---

# Idempotent Execution

The pipeline is designed to be safe to run multiple times.

- If an account already has a generated **v1 configuration**, the demo extraction step is skipped.
- If onboarding updates were already applied, the system avoids recreating duplicate versions.

---

# Zero-Cost Design

The implementation strictly follows the assignment constraint of **zero spend**.

Key decisions:

- Rule-based transcript parsing instead of paid LLM APIs
- Local JSON storage instead of paid databases
- Local script orchestration
- Retell agent creation simulated via JSON specification output

---

# Production Deployment Design

In a production environment, this pipeline could be extended with:

- Whisper-based speech-to-text transcription
- Direct Retell API integration
- ServiceTrade integration
- PostgreSQL or Supabase storage
- Monitoring and alerting for failed onboarding updates
- Dashboard for reviewing configuration diffs
- Queue-based processing for large-scale onboarding pipelines

---

# Summary

This project implements an automated pipeline that converts demo and onboarding conversations into structured Retell agent configurations.

The system generates an initial configuration from demo calls (**v1**) and updates it with confirmed operational rules from onboarding (**v2**) while preserving version history and change tracking.

The architecture emphasizes **automation reliability, reproducibility, and zero-cost tooling**.
