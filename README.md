# Trade Command Center V2

Trade Command Center is a multi-asset, multi-broker trading platform.

## Initial broker rollout

1. PrimeXBT MT5 demo
2. PrimeXBT MT5 real
3. Binance

## Initial platforms

- Windows desktop
- Android

## Architecture

- Flutter client applications
- FastAPI backend
- Deterministic backend risk engine
- Separate Windows execution agent for MetaTrader 5
- Broker adapter architecture
- Audit trail for every trading decision and execution event

## Safety rule

AI analysis may propose a trade plan, but it must never directly execute a broker order. Every order must pass deterministic backend risk checks and the execution workflow.
