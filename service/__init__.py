from celery import Celery

broker_url = "amqp://freddthink:pandroid016@localhost:5672/myvhost"

worker = Celery(
    "service",
    broker=broker_url,
    backend="db+sqlite:///db.sqlite3",
    include=["service.tasks"],
)


worker.conf.update(
    result_expires=3600,
)



if __name__ == '__main__':
    worker.start()
