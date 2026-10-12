from marshal_queue.memory_queue import InMemoryQueue


def test_a_new_job_starts_out_waiting():
    queue = InMemoryQueue()
    job = queue.enqueue("send_email", {"to": "sara@example.com"})

    assert job.state == "queued"
    assert queue.count("queued") == 1


def test_a_claimed_job_is_not_handed_out_twice():
    queue = InMemoryQueue()
    queue.enqueue("a", {})

    assert queue.claim() is not None  # the first worker gets the job
    assert queue.claim() is None      # a second worker gets nothing
