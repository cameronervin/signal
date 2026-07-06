from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.lead import LeadCreate, LeadResponse, SeedLeadsResponse
from app.services.lead_service import LeadService, get_lead_service

router = APIRouter()
seed_router = APIRouter()


@seed_router.post(
    "/leads/seed",
    response_model=SeedLeadsResponse,
    status_code=status.HTTP_201_CREATED,
)
async def seed_leads(
    service: LeadService = Depends(get_lead_service),
) -> SeedLeadsResponse:
    return await service.seed_demo_leads()


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    return await service.create_and_enrich(payload)


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    service: LeadService = Depends(get_lead_service),
) -> list[LeadResponse]:
    return await service.list_leads()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    lead = await service.get_lead(lead_id)
    if lead is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    return lead
