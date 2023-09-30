from typing import Optional

from llm_task_handler.handler import TaskHandler
from llm_task_handler.select import TaskSelector


MAX_SELF_ITERATIONS = 10


class TaskDispatcher:
    def __init__(self, task_handlers: list[TaskHandler]):
        self.selector = TaskSelector(task_handlers)

    async def reply(self, prompt: str) -> Optional[str]:
        task_state = self.selector.select_task(prompt)

        if not task_state:
            return None

        for _ in range(MAX_SELF_ITERATIONS):
            task_state = await task_state.handler.transition(task_state)
            if task_state.is_done:
                return task_state.reply

        return None
