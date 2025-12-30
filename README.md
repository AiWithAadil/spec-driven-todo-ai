# Spec-Driven Todo AI 🚀

A multi-phase Todo application built using **Spec-Driven Development** — where **requirements come first and code follows**.  
This repository demonstrates how traditional software engineering discipline can be combined with modern AI-assisted development.

The project evolves step-by-step from a simple CLI application to a full AI-powered, cloud-deployed system.

---

## 🎯 Purpose of This Repository

- Demonstrate **Spec-Driven Development** in practice
- Show how AI (Claude Code) can reliably generate code **from specs**
- Build the same product across **multiple phases**, each with increasing complexity
- Follow hackathon rules: clarity, discipline, and reproducibility

**Golden Rule:**  
> If something is wrong, fix the **spec**, not the code.

---

## 🧠 What is Spec-Driven Development?

Instead of directly writing code, we:
1. Write **Specifications** (what the system should do)
2. Create an **Architecture Plan**
3. Break it into **Atomic Tasks**
4. Let AI **implement strictly from specs**

This ensures:
- No feature creep
- Predictable results
- Easy iteration and auditing

---

## 📂 Repository Structure

spec-driven-todo-ai/
│
├── phase-1-cli/ # Python CLI Todo App (in-memory)
├── phase-2-web/ # Web App (FastAPI + Next.js + DB)
├── phase-3-ai-chat/ # AI Chat-based Todo (Agents + Tools)
├── phase-4-k8s/ # Docker + Kubernetes (local)
└── phase-5-cloud/ # Cloud deployment & advanced features


Each phase has its **own specs, plans, tasks, and implementation**.

---

## ✅ Phases Overview

### Phase 1 — CLI Todo App
- Python CLI
- In-memory storage
- 5 basic features (CRUD + complete)
- No database, no frameworks

### Phase 2 — Web Application
- Backend: FastAPI
- Frontend: Next.js
- Authentication (JWT)
- Postgres database

### Phase 3 — AI Chat Todo
- Natural language task management
- Tool calling via AI agents
- Conversation history storage

### Phase 4 — Kubernetes
- Dockerized services
- Local Kubernetes (Minikube)
- AI-assisted DevOps tools

### Phase 5 — Cloud & Scale
- Event-driven features (Kafka, Dapr)
- Cloud deployment (AKS / GKE / OCI)
- Production-ready architecture

---

## 🛠 Tools & Technologies
- Python
- Spec-Kit / SpecifyPlus
- Claude Code (Bonsai)
- FastAPI, Next.js
- PostgreSQL
- Docker, Kubernetes
- AI Agents & Tool Calling

---

## 🏁 Status
- ✅ Phase 1: Completed
- ⏳ Phase 2–5: In progress

---

## 📌 Final Note
This repository is intentionally structured for **clarity, review, and learning**.  
It reflects how modern engineers should think:  
**Architect first. Automate second. Code last.**
