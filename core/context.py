from contextvars import ContextVar

current_user_id = ContextVar("current_user_id", default=None)
current_chat_id = ContextVar("current_chat_id", default=None)
