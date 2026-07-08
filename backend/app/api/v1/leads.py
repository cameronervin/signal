from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_lead_intake_service
from app.schemas.lead import (
    LeadCreate,
    LeadDeleteResponse,
    LeadQueueItemResponse,
    LeadResponse,
)
from app.schemas.run import AgentRunResponse
from app.services.lead_intake_service import (
    LeadDeleteConflictError,
    LeadDeleteNotFoundError,
    LeadIntakeService,
    QueueDispatchError,
)

router = APIRouter()


@router.post(
    "",
    response_model=AgentRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_lead(
    payload: LeadCreate,
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> AgentRunResponse:
    try:
        return await service.create_and_enqueue(payload)
    except QueueDispatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent run could not be queued",
        ) from exc


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> list[LeadResponse]:
    return await service.list_leads()


@router.get("/queue", response_model=list[LeadQueueItemResponse])
async def list_lead_queue(
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> list[LeadQueueItemResponse]:
    return await service.list_lead_queue_items()


@router.delete("", response_model=LeadDeleteResponse)
async def delete_all_leads(
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> LeadDeleteResponse:
    return await service.delete_all_leads()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> LeadResponse:
    lead = await service.get_lead(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead


@router.delete("/{lead_id}", response_model=LeadDeleteResponse)
async def delete_lead(
    lead_id: UUID,
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> LeadDeleteResponse:
    try:
        return await service.delete_lead(lead_id)
    except LeadDeleteConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except LeadDeleteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        ) from exc
