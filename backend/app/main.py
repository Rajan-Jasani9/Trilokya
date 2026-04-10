import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.routes import auth, users, projects, ctes, trl, evidence, approvals, admin, audit, technologies
from app.database import engine, Base

# Create tables (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trilokya",
    description="Technology Readiness Level Monitoring and Governance System",
    version="1.0.0"
)

# Mount media directory for serving technology icons and other static assets
MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")
os.makedirs(os.path.join(MEDIA_DIR, "technologies"), exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["*"],  # includes OPTIONS for preflight
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(ctes.router, prefix="/api/ctes", tags=["CTEs"])
app.include_router(trl.router, prefix="/api/trl", tags=["TRL Assessment"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["Approvals"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(technologies.router, prefix="/api/technologies", tags=["Technologies"])


@app.get("/")
def root():
    return {"message": "Trilokya API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
