import uuid

from marshal_queue.job import Job


class InMemoryQueue:
    # A waiting line for jobs. For now it only lives in memory, so if the
    # program stops, the jobs are gone. Later we'll move them into a real
    # database so they survive.

    def __init__(self):
        # Every job we've been given, stored by its id so we can find it fast.
        self.jobs = {}

    def enqueue(self, task_name, payload):
        # Add a new job to the line and hand it back.
        job = Job(id=str(uuid.uuid4()), task_name=task_name, payload=payload)
        self.jobs[job.id] = job
        return job

    def count(self, state):
        # How many jobs are in a given state, like "queued"?
        return sum(1 for job in self.jobs.values() if job.state == state)
