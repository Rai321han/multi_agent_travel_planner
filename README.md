# Multi-Agent Travel Planner

An AI-powered travel planning system built with [CrewAI](https://crewai.com), where a team of specialized agents collaborates to research destinations, plan budgets, design itineraries, and validate complete trip plans — all from a single prompt.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green)](https://crewai.com)
[![LLM](https://img.shields.io/badge/LLM-Groq%20%7C%20LLaMA--3.3--70B-orange)](https://groq.com)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Agents](#agents)
- [Tasks & Workflow](#tasks--workflow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output](#output)
- [Tools Used](#tools-used)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Multi-Agent Travel Planner is a CrewAI-based application that automates end-to-end travel planning using a pipeline of four AI agents. Each agent has a specialized role, from researching destinations to validating final plans, working sequentially to produce a comprehensive, personalized travel plan.

The system uses **Groq's LLaMA-3.3-70B** model for fast inference and integrates **Serper** for real-time web search, ensuring up-to-date recommendations for attractions, pricing, and logistics.

---

## Features

- **Destination Research** — Real-time web search for attractions, culture, weather, and local tips
- **Budget Planning** — Accurate cost breakdowns using live price data and a calculator tool
- **Itinerary Design** — Day-by-day plans with morning, afternoon, and evening schedules
- **Plan Validation** — Automated budget variance checks and schedule feasibility analysis
- **Merged Output** — All outputs combined into a single `full_trip_plan.md` report
- **Fast Inference** — Powered by Groq's ultra-low-latency API

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────┐
│               CrewAI Sequential Pipeline         │
│                                                  │
│  [1] Destination Researcher  ──►  research.md   │
│         │                                        │
│  [2] Budget Planner          ──►  budget.md     │
│         │                                        │
│  [3] Itinerary Designer      ──►  itinerary.md  │
│         │                                        │
│  [4] Validation Agent        ──►  validation.md │
│                                                  │
│         └──── @after_kickoff hook ────►          │
│                  full_trip_plan.md               │
└─────────────────────────────────────────────────┘
```

Each agent receives the outputs of previous agents as context, enabling grounded, consistent reasoning across the pipeline.

---

## Agents

| Agent | Role | Tools | Max Iterations |
|-------|------|-------|----------------|
| **Destination Researcher** | Researches attractions, culture, neighborhoods, and weather | Serper Search | 1 |
| **Budget Planner** | Builds itemized cost breakdowns with real pricing data | Serper Search, Calculator | 2 |
| **Itinerary Designer** | Designs a realistic day-by-day schedule aligned with the budget | Serper Search | 2 |
| **Validation Agent** | Validates budget accuracy, schedule feasibility, and flags risks | Calculator | 1 |

---

## Tasks & Workflow

The pipeline runs **sequentially** — each task passes context to the next:

1. **`research_task`** — Searches for top attractions, best areas to stay, local customs, and practical travel tips. Outputs a structured Markdown report.

2. **`budget_task`** *(uses research output)* — Looks up live prices for hotels, meals, and transport. Uses the Calculator tool to compute accommodation, food, transport, and activity totals. Flags PASS / WARNING / FAIL against the stated budget.

3. **`itinerary_task`** *(uses research + budget output)* — Designs a day-by-day plan with morning, afternoon, and evening slots. Ensures daily costs align with budget allocations and total spending is within ±10% of the budget.

4. **`validation_task`** *(uses all prior outputs)* — Verifies budget variance, schedule feasibility, identifies risk factors, and lists all assumptions made.

5. **`merge_all_task_outputs_hook`** *(post-kickoff)* — Automatically merges all four output files into `output/full_trip_plan.md`.

---

## Project Structure

```
multi_agent_travel_planner/
│
├── src/
│   └── multi_agent_travel_planner/
│       ├── config/
│       │   ├── agents.yaml          # Agent role definitions & goals
│       │   └── tasks.yaml           # Task descriptions & expected outputs
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── calculator.py        # Calculator tool implementation
│       │   └── custom_tool.py       # CalculatorTool wrapper
│       ├── __init__.py
│       ├── crew.py                  # Crew, agents, tasks, and merge hook
│       ├── main.py                  # Entry points: run, train, replay, test
│       └── rate_limit_llm.py        # LLM rate-limit wrapper
│
├── output/                          # Generated output files (auto-created)
│   ├── research.md
│   ├── budget.md
│   ├── itinerary.md
│   ├── validation.md
│   └── full_trip_plan.md            # Merged final plan
│
├── tests/
├── knowledge/
├── .env                             # Environment variables (not committed)
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Prerequisites

- Python **3.10+**
- A **Groq API key** — [Get one here](https://console.groq.com)
- A **Serper API key** — [Get one here](https://serper.dev)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rai321han/multi_agent_travel_planner.git
cd multi_agent_travel_planner
```

### 2. Install dependencies

Using `uv` (recommended):

```bash
uv sync
```

### 3. Create the output directory

```bash
mkdir -p output
```

---

## Configuration

Create a `.env` file in the project root:

```env
SERPER_API_KEY=your_serper_api_key_here
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME="groq/llama-3.3-70b-versatile"
MAX_TOKEN=2500
```

| Variable | Description | Default |
|----------|-------------|---------|
| `SERPER_API_KEY` | Serper.dev API key for web search | Required |
| `GROQ_API_KEY` | Groq API key for LLM inference | Required |
| `MODEL_NAME` | LiteLLM-compatible model identifier | `groq/llama-3.3-70b-versatile` |
| `MAX_TOKEN` | Maximum tokens per LLM response | `2500` |

---

## Usage

### Interactive Mode (CLI prompt)

Run the planner interactively and enter trip details when prompted:

```bash
crewai run
```

You'll be asked for:
- **Destination** (e.g., `Paris, France`)
- **Travel Dates** (e.g., `2025-08-01 to 2025-08-07`)
- **Total Budget in USD** (e.g., `3000`)
- **Preferences** (e.g., `adventure, food, culture`)
---

## Output

After a successful run, the `output/` directory will contain:

| File | Contents |
|------|----------|
| `research.md` | Destination overview, top attractions, neighborhoods, culture tips |
| `budget.md` | Itemized cost breakdown with PASS/WARNING/FAIL status |
| `itinerary.md` | Day-by-day schedule with timings, restaurants, and transport |
| `validation.md` | Budget variance check, schedule feasibility, risk factors |
| `full_trip_plan.md` | All sections merged into one complete travel document |

**Sample budget table (from `budget.md`):**

```
| Category        | Estimated Cost |
|-----------------|----------------|
| Accommodation   | $840           |
| Food            | $350           |
| Local Transport | $120           |
| Activities      | $210           |
| Miscellaneous   | $80            |
| **TOTAL**       | **$1,600**     |
```

---

## Tools Used

| Tool | Purpose |
|------|---------|
| [CrewAI](https://crewai.com) | Multi-agent orchestration framework |
| [Groq](https://groq.com) | Ultra-fast LLM inference (LLaMA-3.3-70B) |
| [Serper](https://serper.dev) | Real-time Google Search API |
| [LiteLLM](https://litellm.ai) | Unified LLM API abstraction |
| `CalculatorTool` | Custom tool for arithmetic budget computations |

---