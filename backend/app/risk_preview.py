from typing import Literal

from fastapi import APIRouter

from backend.app.risk.risk_evaluation import (
    RiskEvaluationResult,
    evaluate_risk,
)
from backend.app.risk.schemas import (
    RiskEvaluationInput,
    RiskSchema,
)

router = APIRouter(
    prefix="/api/v1/risk",
    tags=["risk"],
)


class RiskPreviewResponse(RiskSchema):
    """
    Read-only HTTP representation of a deterministic risk evaluation.

    Safety flags make it explicit that this endpoint performs analysis
    only and cannot enable or perform trade execution.
    """

    read_only: Literal[True] = True
    execution_enabled: Literal[False] = False
    live_trading_enabled: Literal[False] = False

    evaluation: RiskEvaluationResult


@router.post(
    "/preview",
    response_model=RiskPreviewResponse,
)
def preview_risk(
    request: RiskEvaluationInput,
) -> RiskPreviewResponse:
    """
    Calculate a deterministic risk preview without mutating system state.

    This endpoint performs no persistence, broker communication,
    order submission, or execution.
    """

    return RiskPreviewResponse(
        evaluation=evaluate_risk(
            request,
        ),
    )
