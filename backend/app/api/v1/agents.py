from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.run import AgentRunResponse
from app.services.lead_service import (
    LeadService,
    RunTransitionError,
    get_lead_service,
)

router = APIRouter()


@router.get("", response_model=list[AgentRunResponse])
async def list_agent_runs(
    service: LeadService = Depends(get_lead_service),
) -> list[AgentRunResponse]:
    return await service.list_agent_runs()


@router.get("/{run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    run_id: str,
    service: LeadService = Depends(get_lead_service),
) -> AgentRunResponse:
    run = await service.get_agent_run(run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    return run


@router.post("/{run_id}/approve", response_model=AgentRunResponse)
async def approve_agent_run(
    run_id: str,
    service: LeadService = Depends(get_lead_service),
) -> AgentRunResponse:
    try:
        run = await service.approve_agent_run(run_id)
    except RunTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    return run


@router.post("/{run_id}/pause", response_model=AgentRunResponse)
async def pause_agent_run(
    run_id: str,
    service: LeadService = Depends(get_lead_service),
) -> AgentRunResponse:
    try:
        run = await service.pause_agent_run(run_id)
    except RunTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    return run
