from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_lead_intake_service
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.lead_intake_service import LeadIntakeService

router = APIRouter()


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> LeadResponse:
    return await service.create_and_enrich(payload)


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> list[LeadResponse]:
    return await service.list_leads()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> LeadResponse:
    lead = await service.get_lead(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead
