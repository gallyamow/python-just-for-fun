import datetime
from typing import Union, List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates

"""
FastAPI - простой, быстрый, современный web-framework.
FastAPI сравним по скорости с Node.js и Go, потому что: асинхронность, Uvicorn / Hypercorn, Pydantic на С и очень быстрый.

Для чего:
1) Создания REST API
2) Высокопроизводительных асинхронных приложений
3) Валидации данных “из коробки”
4) Автоматической документации API
5) Использования современных технологий

Используется в:
- REST API
- Backend для SPA (React / Vue / Angular)
- Telegram / Discord ботов
- Микросервисов
- ML-моделей (инференс)
- Full-stack приложений (с шаблонами Jinja2)
- WebSocket приложений (чаты, стриминг)

Как реализован:
- Starlette — для веб-части (роутинг, middleware, веб-сокеты).
- Pydantic — для валидации и сериализации данных.
- Работает как приложение, а не как request->response.

fastapi[standard] — это вариант установки FastAPI с дополнительными пакетами:
- uvicorn[standard]	Сервер ASGI (с поддержкой uvloop и httptools)
- pydantic-settings	Управление настройками через переменные окружения
- python-multipart	Работа с формами и загрузкой файлов
- email-validator	Валидация email в Pydantic
- jinja2	Шаблоны HTML
- python-dotenv	Загрузка переменных окружения из .env

Поддерживается типизация как параметров, так и responses.

Dev запуск:
fastapi dev main.py
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
"""
app = FastAPI()
templates = Jinja2Templates(directory="templates")


class TodoItem(BaseModel):
    """
    Pydantic сам генерирует __init__.
    Это аналог dataclass, поэтому поля просто перечисляются.

    Доступны след. типы:
    1. Базовые примитивы (Python)
    2. Коллекции, например:
        tags: list[str]
        prices: dict[str, float]
    3. Nullable / Optional значения
        is_offer: Optional[bool] = None
        или тоже самое
        is_offer: bool | None = None
    4. Специальные типы Python
        datetime	дата и время
        date	дата
        time	время
        timedelta	интервал
        Enum	перечисление
    6. Сложные типы
    | Тип            | Значение          |
    | -------------- | ----------------- |
    | `Union[A, B]`  | одно из двух      |
    | `Literal[...]` | строгое значение  |
    | `Annotated`    | тип + ограничения |
    | `TypedDict`    | словарь с типами  |
    5. Типы Pydantic
        | Тип                            | Описание                   |
        | ------------------------------ | -------------------------- |
        | `EmailStr`                     | проверка email             |
        | `AnyUrl`, `HttpUrl`            | проверка URL               |
        | `UUID4`                        | UUID                       |
        | `SecretStr`, `SecretBytes`     | безопасные данные (пароли) |
        | `PositiveInt`, `NegativeFloat` | числа с ограничениями      |
        | `constr`, `conint`, `conlist`  | ограниченные типы          |
        | `FilePath`, `DirectoryPath`    | путь к файлу/каталогу      |
    7. Вложенные модели
    8. По умолчанию — любое значение (когда нужно отключит строгую типизацию)
        data: Any
    """

    item_id: UUID
    title: str
    description: Union[str, None] = None
    created_at: datetime.datetime


storage: dict[UUID, TodoItem] = {}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> List[TodoItem]:
    """
    Теперь возвращаем ответ в виде html.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "todos": list(storage.values())}
    )


@app.post("/create")
def create_item(title: str = Form(...), description: str = Form(None)):
    item = TodoItem(
        item_id=uuid4(),
        title=title,
        description=description,
        created_at=datetime.datetime.now(),
    )
    storage[item.item_id] = item
    return RedirectResponse(url="/", status_code=303)


@app.get("/items/{item_id}")
def read_item(item_id: UUID) -> TodoItem:
    if item_id not in storage:
        raise HTTPException(404, detail="Item not found.")

    return storage[item_id]


@app.put("/items/{item_id}")
def update_item(item_id: UUID, item: TodoItem) -> TodoItem:
    if item_id not in storage:
        raise HTTPException(404, detail="Item not found.")

    storage[item_id] = item
    return item


@app.delete("/todos/{item_id}")
def delete_todo(item_id: UUID) -> None:
    if item_id not in storage:
        raise HTTPException(404, detail="Item not found.")

    del storage[item_id]
