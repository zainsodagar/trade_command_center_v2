from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from backend.app.brokers.adapters.base import (
    BrokerInstrumentNotFoundError,
    BrokerNotConnectedError,
)
from backend.app.brokers.capabilities import BrokerCapabilities
from backend.app.brokers.manager import (
    BrokerAlreadyRegisteredError,
    BrokerNotRegisteredError,
)
from backend.app.brokers.schemas import (
    AssetClass,
    BrokerAccount,
    BrokerHealth,
    BrokerOrder,
    BrokerPosition,
    Candle,
    Instrument,
    Quote,
)
from backend.app.brokers.service import BrokerService

router = APIRouter(
    prefix="/api/v1/brokers",
    tags=["brokers"],
)

_broker_service = BrokerService()


class SimulatedConnectionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    connection_id: str = Field(
        min_length=1,
        max_length=100,
    )

    connect: bool = True
    replace: bool = False


def get_broker_service() -> BrokerService:
    return _broker_service


BrokerServiceDependency = Annotated[
    BrokerService,
    Depends(get_broker_service),
]


def _raise_http_error(
    exc: Exception,
) -> None:
    if isinstance(
        exc,
        BrokerNotRegisteredError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        BrokerInstrumentNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        BrokerAlreadyRegisteredError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        BrokerNotConnectedError,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    raise exc


@router.get(
    "",
    response_model=list[BrokerHealth],
)
def list_brokers(
    service: BrokerServiceDependency,
) -> list[BrokerHealth]:
    return service.get_all_health()


@router.post(
    "/simulated",
    response_model=BrokerHealth,
    status_code=status.HTTP_201_CREATED,
)
def create_simulated_broker(
    request: SimulatedConnectionRequest,
    service: BrokerServiceDependency,
) -> BrokerHealth:
    try:
        return service.create_simulated_connection(
            request.connection_id,
            connect=request.connect,
            replace=request.replace,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/health",
    response_model=BrokerHealth,
)
def get_broker_health(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerHealth:
    try:
        return service.get_health(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.post(
    "/{connection_id}/connect",
    response_model=BrokerHealth,
)
def connect_broker(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerHealth:
    try:
        return service.connect(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.post(
    "/{connection_id}/disconnect",
    response_model=BrokerHealth,
)
def disconnect_broker(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerHealth:
    try:
        return service.disconnect(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.delete(
    "/{connection_id}",
    response_model=BrokerHealth,
)
def remove_broker(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerHealth:
    try:
        return service.remove_connection(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/capabilities",
    response_model=BrokerCapabilities,
)
def get_broker_capabilities(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerCapabilities:
    try:
        return service.get_capabilities(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/account",
    response_model=BrokerAccount,
)
def get_broker_account(
    connection_id: str,
    service: BrokerServiceDependency,
) -> BrokerAccount:
    try:
        return service.get_account(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/instruments",
    response_model=list[Instrument],
)
def get_broker_instruments(
    connection_id: str,
    service: BrokerServiceDependency,
    search: str | None = None,
    asset_class: AssetClass | None = None,
    tradable_only: bool = True,
) -> list[Instrument]:
    try:
        return service.get_instruments(
            connection_id,
            search=search,
            asset_class=asset_class,
            tradable_only=tradable_only,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/instrument",
    response_model=Instrument,
)
def get_broker_instrument(
    connection_id: str,
    service: BrokerServiceDependency,
    symbol: Annotated[
        str,
        Query(min_length=1),
    ],
) -> Instrument:
    try:
        return service.get_instrument(
            connection_id,
            symbol,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/quote",
    response_model=Quote,
)
def get_broker_quote(
    connection_id: str,
    service: BrokerServiceDependency,
    symbol: Annotated[
        str,
        Query(min_length=1),
    ],
) -> Quote:
    try:
        return service.get_quote(
            connection_id,
            symbol,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/candles",
    response_model=list[Candle],
)
def get_broker_candles(
    connection_id: str,
    service: BrokerServiceDependency,
    symbol: Annotated[
        str,
        Query(min_length=1),
    ],
    timeframe: Annotated[
        str,
        Query(min_length=1),
    ],
    count: Annotated[
        int,
        Query(
            ge=1,
            le=5000,
        ),
    ] = 200,
) -> list[Candle]:
    try:
        return service.get_candles(
            connection_id,
            symbol,
            timeframe,
            count=count,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/positions",
    response_model=list[BrokerPosition],
)
def get_broker_positions(
    connection_id: str,
    service: BrokerServiceDependency,
) -> list[BrokerPosition]:
    try:
        return service.get_positions(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise


@router.get(
    "/{connection_id}/orders",
    response_model=list[BrokerOrder],
)
def get_broker_orders(
    connection_id: str,
    service: BrokerServiceDependency,
) -> list[BrokerOrder]:
    try:
        return service.get_open_orders(
            connection_id,
        )
    except Exception as exc:
        _raise_http_error(exc)
        raise