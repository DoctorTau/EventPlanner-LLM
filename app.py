from fastapi import FastAPI

from routers import plan_router


def create_app() -> FastAPI:
    app = FastAPI(title="Event Planner AI")
    app.include_router(plan_router.router)

    @app.get("/health")
    async def health() -> str:
        return "ok"

    return app
