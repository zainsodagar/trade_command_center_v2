# Architecture

```text
Flutter Windows / Android
          |
          v
     FastAPI Backend
          |
          +--> Market data and account services
          +--> Deterministic risk engine
          +--> Audit and execution-intent service
                         |
                         v
              Windows Execution Agent
                         |
                         v
               PrimeXBT MT5 Terminal
```

Binance will later use a broker adapter while preserving the same normalized backend contracts.
