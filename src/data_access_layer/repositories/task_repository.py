from src.data_access_layer.models.task_model import Task
from src.data_access_layer.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session):
        super().__init__(session, Task)

    async def get_by_title(self, title: str) -> Task | None:
        return await self.get_by_field("title", title)
