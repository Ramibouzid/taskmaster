from unittest.mock import patch, MagicMock
from flask import current_app


def test_openai_client_uses_base_url_from_config(app):
    with app.app_context():
        with patch("openai.OpenAI") as mock_openai:
            mock_instance = MagicMock()
            mock_openai.return_value = mock_instance
            mock_instance.chat.completions.create.return_value.choices = [
                MagicMock(message=MagicMock(content='{"desc": "test"}'))
            ]

            from app.routes.ai import generate_task
            with app.test_request_context(json={"title": "test task"}, method="POST"):
                from flask_login import login_user
                from app.models import User
                u = User(id=999, name="t", email="t@t.com")
                login_user(u)
                generate_task()

            call_kwargs = mock_openai.call_args[1]
            assert "base_url" in call_kwargs, "base_url not passed to OpenAI client"
            assert call_kwargs["base_url"] == current_app.config["OPENAI_BASE_URL"]


def test_chat_uses_base_url_from_config(app):
    with app.app_context():
        with patch("openai.OpenAI") as mock_openai:
            mock_instance = MagicMock()
            mock_openai.return_value = mock_instance
            mock_instance.chat.completions.create.return_value.choices = [
                MagicMock(message=MagicMock(content="reply"))
            ]

            from app.routes.ai import chat
            with app.test_request_context(json={"message": "hello"}, method="POST"):
                from flask_login import login_user
                from app.models import User
                u = User(id=999, name="t", email="t@t.com")
                login_user(u)
                chat()

            call_kwargs = mock_openai.call_args[1]
            assert "base_url" in call_kwargs, "base_url not passed to OpenAI client"
            assert call_kwargs["base_url"] == current_app.config["OPENAI_BASE_URL"]
