# Trade Command Center — Windows MT5 Agent

The Windows MT5 Agent is the controlled boundary between the
Trade Command Center backend and MetaTrader 5.

## Architecture

Trade Command Center Backend
    |
Windows MT5 Agent
    |
MetaTrader 5 Terminal
    |
PrimeXBT

The main backend does not communicate directly with MetaTrader 5.

## Current Phase

Phase 4 — PrimeXBT MT5 Demo Read-Only

Checkpoint 4.1 establishes the Windows agent foundation.

Actual MetaTrader 5 initialization begins in Checkpoint 4.2.

## Current Endpoints

- GET /health
- GET /api/v1/agent/status
- GET /api/v1/mt5/status

## Network Binding

The development agent listens only on:

127.0.0.1:8765

It is therefore not exposed to other machines on the network.

## Safety Defaults

- MT5 enabled: false
- terminal available: false
- initialized: false
- account logged in: false
- execution enabled: false
- live trading enabled: false

No trading endpoints currently exist.

## Run

Start:

    .\scripts\start_execution_agent.ps1

Test:

    .\scripts\run_execution_agent_tests.ps1

Swagger:

    http://127.0.0.1:8765/docs

## Development Environment

Dependencies:

    execution_agent\requirements.txt

Pinned dependency versions:

    execution_agent\requirements-lock.txt

Virtual environment:

    execution_agent\.venv

The virtual environment is excluded from Git.