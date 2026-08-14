from backend.app.accounts.models import TradingAccount, User
from backend.app.audit.models import AuditEvent
from backend.app.brokers.models import BrokerConnection
from backend.app.execution.models import ExecutionRecord
from backend.app.risk.models import RiskProfile

MODEL_CLASSES = (
    User,
    BrokerConnection,
    TradingAccount,
    RiskProfile,
    AuditEvent,
    ExecutionRecord,
)

__all__ = [
    "AuditEvent",
    "BrokerConnection",
    "ExecutionRecord",
    "MODEL_CLASSES",
    "RiskProfile",
    "TradingAccount",
    "User",
]