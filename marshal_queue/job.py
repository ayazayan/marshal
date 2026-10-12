from dataclasses import dataclass


@dataclass
class Job:
    # A job is one piece of work that needs doing later

    id: str          # a unique id, so we can tell two jobs apart
    task_name: str   # what kind of work it is
    payload: dict    # the details the work needs
    state: str = "queued"  # every job starts out waiting in line
