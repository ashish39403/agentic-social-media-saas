from social_saas.worker.tasks import ping


def test_foundation_ping_task_contract() -> None:
    assert ping.run() == {"status": "ok"}
