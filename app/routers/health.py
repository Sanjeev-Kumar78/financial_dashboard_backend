from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    # Simplest possible liveness check.
    # A load balancer or CI pipeline can hit this to confirm the app is running.
    return {"status": "ok"}
