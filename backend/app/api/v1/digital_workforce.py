from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_digital_worker_service
from app.schemas.digital_worker import (
    DigitalWorkerAssignmentCreate,
    DigitalWorkerAssignmentResponse,
    DigitalWorkerInboundEmailCreate,
)
from app.services.digital_worker_service import (
    DigitalWorkerDispatchError,
    DigitalWorkerEligibilityError,
    DigitalWorkerNotFoundError,
    DigitalWorkerService,
    DigitalWorkerTransitionError,
)

router = APIRouter()


@router.post(
    "/assignments",
    response_model=DigitalWorkerAssignmentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_assignment(
    payload: DigitalWorkerAssignmentCreate,
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> DigitalWorkerAssignmentResponse:
    try:
        return await service.assign_lead(payload)
    except DigitalWorkerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (DigitalWorkerEligibilityError, DigitalWorkerTransitionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except DigitalWorkerDispatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Digital worker run could not be queued",
        ) from exc


@router.get(
    "/assignments",
    response_model=list[DigitalWorkerAssignmentResponse],
)
async def list_assignments(
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> list[DigitalWorkerAssignmentResponse]:
    return await service.list_assignments()


@router.get(
    "/assignments/{assignment_id}",
    response_model=DigitalWorkerAssignmentResponse,
)
async def get_assignment(
    assignment_id: UUID,
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> DigitalWorkerAssignmentResponse:
    try:
        return await service.get_assignment(assignment_id)
    except DigitalWorkerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/assignments/{assignment_id}/inbound-email",
    response_model=DigitalWorkerAssignmentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def record_inbound_email(
    assignment_id: UUID,
    payload: DigitalWorkerInboundEmailCreate,
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> DigitalWorkerAssignmentResponse:
    try:
        return await service.record_inbound_email(
            assignment_id=assignment_id,
            payload=payload,
        )
    except DigitalWorkerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DigitalWorkerTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except DigitalWorkerDispatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Digital worker run could not be queued",
        ) from exc


@router.post(
    "/assignments/{assignment_id}/pause",
    response_model=DigitalWorkerAssignmentResponse,
)
async def pause_assignment(
    assignment_id: UUID,
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> DigitalWorkerAssignmentResponse:
    try:
        return await service.pause_assignment(assignment_id)
    except DigitalWorkerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DigitalWorkerTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/assignments/{assignment_id}/resume",
    response_model=DigitalWorkerAssignmentResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def resume_assignment(
    assignment_id: UUID,
    service: DigitalWorkerService = Depends(get_digital_worker_service),
) -> DigitalWorkerAssignmentResponse:
    try:
        return await service.resume_assignment(assignment_id)
    except DigitalWorkerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DigitalWorkerTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except DigitalWorkerDispatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Digital worker run could not be queued",
        ) from exc
