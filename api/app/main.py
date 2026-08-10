from collections import defaultdict, deque
from contextlib import asynccontextmanager
from time import monotonic
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .demo_data import DEMO_BRIEF
from .domain import BriefInput, ComposeResponse, ReviewInput, ReviewResponse
from .service import ComposerService


class RequestRateLimiter:
    def __init__(self, requests: int, window_seconds: int) -> None:
        self.requests = requests
        self.window_seconds = window_seconds
        self.requests_by_ip: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client_ip: str) -> bool:
        now = monotonic()
        request_times = self.requests_by_ip[client_ip]
        while request_times and request_times[0] <= now - self.window_seconds:
            request_times.popleft()
        if len(request_times) >= self.requests:
            return False
        request_times.append(now)
        return True


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    service = ComposerService(active_settings)
    limiter = RequestRateLimiter(
        requests=active_settings.rate_limit_requests,
        window_seconds=active_settings.rate_limit_window_seconds,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        service.startup()
        yield
        service.shutdown()

    app = FastAPI(
        title="Delivery Composer API",
        version="0.1.0",
        description="Synthetic-data MVP API. Database and AI credentials stay server-side.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "database_configured": bool(active_settings.database_url),
            "gemini_configured": active_settings.has_gemini,
            "demo_mode": active_settings.demo_mode,
        }

    @app.get("/api/demo-brief")
    def demo_brief() -> dict[str, str]:
        return {"brief": DEMO_BRIEF}

    @app.post("/api/compose", response_model=ComposeResponse)
    def compose(brief_input: BriefInput, request: Request) -> ComposeResponse:
        client_ip = request.client.host if request.client else "unknown"
        if not limiter.allow(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demo request limit reached. Please wait before running another composition.",
            )
        try:
            return service.compose(brief_input)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
        except RuntimeError as error:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Analysis service is unavailable.") from error

    @app.post("/api/runs/{run_id}/review", response_model=ReviewResponse)
    def record_review(run_id: UUID, review: ReviewInput) -> ReviewResponse:
        # The endpoint intentionally accepts only bounded, non-sensitive demonstration notes.
        service.record_review(run_id, review)
        return ReviewResponse(run_id=run_id, status=review.status)

    return app


app = create_app()
