from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_lead_intake_service
from app.schemas.lead import LeadCreate, LeadResponse
from app.schemas.run import AgentRunResponse
from app.services.lead_intake_service import LeadIntakeService, QueueDispatchError

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
