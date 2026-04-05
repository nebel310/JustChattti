import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import create_tables
from database import delete_tables
from router.auth import router as auth_router
from router.files import router as files_router
from router.chat import router as chat_router
from router.search import router as search_router
from router.admin import router as admin_router
from router.fcm import router as fcm_router  # <-- добавлено
from websocket.router import router as websocket_router
from utils.minio_client import minio
from utils.seed import create_admin




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""    
    await create_tables()
    print('База готова к работе')
    await create_admin()
    
    yield
    
    print('Выключение')



def custom_openapi():
    """Кастомная OpenAPI схема с настройками безопасности."""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="JustChattti API",
        version="1.0.0",
        description="""Бэкенд для мессенджера JustChattti с поддержкой чатов и WebRTC
    
**Разработчик:** Григорьев Владислав Алексеевич
**Контакты:** 
- Телеграм: @vlados7529
- Телефон: +7 (916) 054 44-35  
- GitHub: github.com/nebel310
- Email: vladislav75290@gmail.com""",
        routes=app.routes,
    )
    
    # Инициализируем components, если их нет
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
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
        ("/auth/user-update", "patch"): [{"Bearer": []}],
        ("/auth/users/{user_id}", "get"): [{"Bearer": []}],
        ("/auth/users/{user_id}/status", "get"): [{"Bearer": []}],
        ("/auth/role", "patch"): [{"Bearer": []}],
        ("/auth/user_storage_limit", "patch"): [{"Bearer": []}],
        ("/files/upload", "post"): [{"Bearer": []}],
        ("/files/{file_id}", "get"): [{"Bearer": []}],
        ("/files/{file_id}/download", "get"): [{"Bearer": []}],
        ("/files/{file_id}", "delete"): [{"Bearer": []}],
        ("/chats/", "get"): [{"Bearer": []}],
        ("/chats/", "post"): [{"Bearer": []}],
        ("/chats/{chat_id}", "get"): [{"Bearer": []}],
        ("/chats/{chat_id}", "delete"): [{"Bearer": []}],
        ("/chats/{chat_id}/messages", "get"): [{"Bearer": []}],
        ("/chats/{chat_id}/messages", "post"): [{"Bearer": []}],
        ("/chats/messages/{message_id}", "patch"): [{"Bearer": []}],
        ("/chats/messages/{message_id}", "delete"): [{"Bearer": []}],
        ("/chats/messages/mark-read", "post"): [{"Bearer": []}],
        ("/chats/{chat_id}/calls", "post"): [{"Bearer": []}],
        ("/search/users", "post"): [{"Bearer": []}],
        ("/search/users/username/{username}", "get"): [{"Bearer": []}],
        ("/search/messages/global", "post"): [{"Bearer": []}],
        ("/search/messages/chat/{chat_id}", "post"): [{"Bearer": []}],
        ("/search/messages/username/{username}", "post"): [{"Bearer": []}],
        ("/search/messages/sender/{user_id}", "get"): [{"Bearer": []}],
        ("/fcm/register", "post"): [{"Bearer": []}],
        ("/fcm/unregister", "delete"): [{"Bearer": []}],
    }
    
    for (path, method), security in secured_paths.items():
        if path in openapi_schema["paths"] and method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = security
    
    app.openapi_schema = openapi_schema
    
    return app.openapi_schema



app = FastAPI(lifespan=lifespan, debug=True)
app.openapi = custom_openapi



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth_router)
app.include_router(files_router)
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(websocket_router)
app.include_router(admin_router)
app.include_router(fcm_router)



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        log_level="debug",
        reload=True,
        port=1000,
        host="0.0.0.0"
    )