import logging
import os
from logging.handlers import RotatingFileHandler, QueueHandler
from queue import Queue


def setup_logging(app):
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    log_dir = os.path.join(app.root_path, "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_queue = Queue()
    queue_handler = QueueHandler(log_queue)
    queue_handler.setLevel(log_level)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "taskmaster.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"
    ))

    listener = logging.handlers.QueueListener(log_queue, file_handler, stream_handler)
    listener.start()

    app.logger.addHandler(queue_handler)
    app.logger.setLevel(log_level)
    app.logger.propagate = False

    app.extensions["log_listener"] = listener

    app.logger.info("Logging initialized")


def get_logger(name):
    return logging.getLogger(name)


def register_error_handlers(app):
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error("Server error: %s", str(e))
        return render_template("errors/500.html"), 500
