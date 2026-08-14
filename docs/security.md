# Security Principles

- Never commit broker passwords, API keys, JWT secrets, or private keys.
- Never allow Binance API keys to have withdrawal permission.
- Never store live credentials directly in Flutter source code or ordinary SQLite fields.
- Require deterministic backend validation before execution.
- Keep demo and live modes visibly and technically separate.
- Record every order intent, risk decision, broker response, and reconciliation event.
