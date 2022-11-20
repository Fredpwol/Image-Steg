from settings import CELERY_MESSAGING_QUEUE
from celery import Celery


worker = Celery(
    "service",
    broker=CELERY_MESSAGING_QUEUE,
    backend="db+sqlite:///db.sqlite3",
    include=["service.tasks"],
)


worker.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    worker.start()
