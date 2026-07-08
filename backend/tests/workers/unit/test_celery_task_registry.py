from app.workers.app import REQUIRED_SIGNAL_TASKS, registered_signal_tasks


def test_signal_celery_tasks_are_registered_on_worker_app_import() -> None:
    assert REQUIRED_SIGNAL_TASKS <= registered_signal_tasks()
