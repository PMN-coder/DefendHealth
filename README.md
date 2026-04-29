# DefendHealth AI - AI FRAUD INSURANCE CLAIM DETECTION

> Proactive AI Escrow & Multimodal Fraud Detection for Health and Auto Insurance.

## What is this
DefendHealth AI is a full-stack, enterprise-grade desktop application built with Electron and Python (FastAPI). It actively intercepts fraudulent insurance claims and digital forgeries (deepfakes/altered bills) using an Isolation Forest ML model and a Vision AI Authenticator, instantly freezing high-risk funds in a simulated banking escrow.

## Why we built this
* **Motivation:** Every year, billions are drained from public schemes (like PM-JAY) and private insurers due to organized fraud rings and cryptographically altered document forgeries. Current systems act *after* the payout. We built a system to stop the money *before* it leaves the bank.
* **Goals:** - Provide a zero-latency verification portal for clinics and garages.
  - Automatically freeze high-risk transactions in an Escrow sandbox.
  - Authenticate uploaded images for EXIF tampering and deepfakes.
  - Generate instant IRDAI-compliant PDF audit reports.

## Repository structure
* `frontend/` — Electron desktop application (UI, Chart.js, Vis-network, jsPDF).
* `backend/` — Python FastAPI server, ML training pipeline, Vision AI, and MySQL database logic.
* `challenges/` — Mock datasets, burst-attack scripts, and testing payloads.
* `docs/` — System architecture and judging criteria details.
* `scripts/` — Helper scripts for automated setup.
* `.devcontainer/` — GitHub Codespaces configuration (Enables GUI/Electron in the cloud).

## Key links
* Project board / scoreboard: [SCOREBOARD.md](SCOREBOARD.md)
* Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## Architecture diagram

```mermaid
flowchart LR
    subgraph Users
        A[Hospital / Garage]
    end
    subgraph App
        direction TB
        B[Electron Desktop UI]
        C[FastAPI Backend & ML Model]
        F[Vision AI Authenticator]
        D[(MySQL Database)]
    end
    subgraph Banking
        E[NPCI Escrow Gateway]
    end
    
    A -- Submits Claim & Image --> B
    B -- JSON Payload --> C
    B -- Image Upload --> F
    F -- Forgery Score --> C
    C -- Validates & Hashes --> D
    C -- Triggers Payout/Freeze --> E
    E -- Returns Txn ID --> C
