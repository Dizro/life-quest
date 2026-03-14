"""app.schemas — Pydantic v2 контракты API (DTO запросов и ответов)."""

from app.schemas.user import (           # noqa: F401
    UserCreate,
    UserRead,
    UserUpdate,
    UserProfile,
)
from app.schemas.task import (           # noqa: F401
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TaskComplete,
    TaskListResponse,
)
from app.schemas.achievement import (    # noqa: F401
    AchievementRead,
    UserAchievementRead,
)
from app.schemas.common import (         # noqa: F401
    HealthResponse,
    PaginationParams,
    PaginatedResponse,
    ErrorResponse,
)

from app.schemas.token import (          # noqa: F401
    Token,
    TokenPayload,
)