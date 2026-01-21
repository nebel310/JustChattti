import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import create_tables
from database import delete_tables
from router.auth import router as auth_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    await delete_tables()
    print('База очищена')
    
    await create_tables()
    print('База готова к работе')
    
    yield
    
    print('Выключение')




def custom_openapi():
    """Кастомная OpenAPI схема с настройками безопасности."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="FastAPI Base Template - Разработано Григорьевым Владиславом Алексеевичем",
        version="1.0.0",
        description="""Базовый шаблон FastAPI с JWT аутентификацией
    
**Разработчик:** Григорьев Владислав Алексеевич
**Контакты:** 
- Телеграм: @vlados7529
- Телефон: +7 (916) 054 44-35  
- GitHub: github.com/nebel310
- Email: m2316174@edu.misis.ru

*Этот бэкенд был создан как базовый шаблон для быстрого старта проектов*""",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    secured_paths = {
        ("/auth/me", "get"): [{"Bearer": []}],
        ("/auth/logout", "post"): [{"Bearer": []}],
    }
    
    for (path, method), security in secured_paths.items():
        if path in openapi_schema["paths"] and method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = security
    
    app.openapi_schema = openapi_schema
    
    return app.openapi_schema




app = FastAPI(lifespan=lifespan)
app.openapi = custom_openapi




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(auth_router)




if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        port=3001,
        host="0.0.0.0"
    )