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

    def claim(self):
        # A worker calls this to get the next job. We hand out the oldest
        # waiting job and mark it "running" right away, so the next worker
        # who asks can't get the same one. If nothing is waiting, we return
        # None, which just means "no work right now".
        for job in self.jobs.values():
            if job.state == "queued":
                job.state = "running"
                return job
        return None

    def complete(self, job_id):
        # A worker calls this when it has finished a job. Only a job that is
        # currently "running" can be completed. Completing a job nobody
        # picked up would mean something went wrong, so we raise an error.
        job = self.jobs[job_id]
        if job.state != "running":
            raise ValueError("Only a running job can be completed.")
        job.state = "succeeded"
