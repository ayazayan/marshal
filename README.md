# Marshal

A job queue built from scratch in Python.

I'm building Marshal to understand how background job systems actually work, from the basics of adding and processing jobs to the harder problems of concurrency, persistence, and failure recovery.

A lot of applications need to do work in the background: sending emails, processing files, generating reports, or running tasks that take too long to finish during a normal web request. Instead of making users wait, the application puts these tasks into a queue, and workers process them separately.

That sounds straightforward, but there are some interesting problems underneath. What if a worker crashes halfway through a job? What if two workers try to claim the same job? What if the application restarts while jobs are still waiting?

Marshal is my way of working through those questions by implementing the system myself, one piece at a time.

## How it works

The basic idea is simple:

```text
Application
    |
    | enqueue(job)
    v
+----------------------+
|      Job Queue       |
|                      |
|  Job A: send_email   |
|  Job B: resize_image |
|  Job C: send_email   |
+----------------------+
    |
    | claim()
    v
   Worker
    |
    | execute handler
    v
 complete(job.id)
    |
    v
 Job Succeeded
```

An application submits a job with a task name and some data (the payload). A worker claims the job, finds the function responsible for handling it, runs that function, and marks the job as completed.

Right now, the queue runs entirely in memory, and the demo processes jobs sequentially in one Python process. There's no database or separate worker service yet.

I'm starting small so I can understand each part before adding more complexity.

## What's implemented

- [x] In-memory queue with job submission, claiming, and completion
- [x] Job status tracking
- [x] Basic worker loop that executes jobs using registered handlers
- [x] Automated tests for the core queue functionality

The current version demonstrates the basic job lifecycle. Persistence, concurrent workers, and crash recovery are still planned.

## Try it yourself

### 1. Clone the repository

```bash
git clone https://github.com/ayazayan/marshal.git
cd marshal
```

### 2. Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
```

### 3. Run the demo

```bash
python demo.py
```

The demo adds three jobs to the queue:

1. Send an email to Sara.
2. Resize an image.
3. Send an email to Omar.

The worker picks up each job, calls the appropriate function, and marks it as completed.

The email and image functions are simulated for now. They print messages rather than sending actual emails or modifying files.

### 4. Run the tests

```bash
python -m pytest
```

## A small example

Here's what using the queue looks like:

```python
from marshal_queue.memory_queue import InMemoryQueue

queue = InMemoryQueue()

# Add a job
queue.enqueue("send_email", {"to": "sara@example.com"})

# Claim the next available job
job = queue.claim()

if job is not None:
    print(job.task_name, job.payload)

    # Mark the job as completed
    queue.complete(job.id)
```

This example shows the queue operations themselves. In the full demo, a handler function performs the simulated task before the worker marks it as completed.

## Project structure

```text
marshal/
├── marshal_queue/
│   └── memory_queue.py
├── tests/
├── demo.py
├── requirements-dev.txt
└── README.md
```

- `marshal_queue/` contains the queue implementation.
- `tests/` contains automated tests.
- `demo.py` demonstrates how jobs are submitted and processed.
- `requirements-dev.txt` lists development dependencies.

The package is called `marshal_queue` rather than `marshal` because Python already has a built-in module named `marshal`.

## What's next

I'm building Marshal in stages. The next steps focus on making it more reliable and eventually supporting multiple workers.

- [ ] **PostgreSQL storage:** Move jobs out of memory so they survive application restarts.
- [ ] **Concurrent workers:** Allow multiple workers to process jobs safely without claiming the same queued job at the same time.
- [ ] **Retries:** Retry failed jobs with backoff and move jobs that repeatedly fail into a dead-letter queue.
- [ ] **Crash recovery:** Detect jobs abandoned by crashed workers and make them available again.
- [ ] **HTTP API:** Add endpoints for submitting jobs and checking their status.
- [ ] **Dashboard:** Build a simple interface for viewing queued, running, completed, and failed jobs.
- [ ] **Benchmarks and failure testing:** Measure performance and test how the system behaves under concurrency and crashes.

## Problems I want to solve

These are some of the questions guiding the project as I build out the next stages.

### What if two workers claim the same job?

With multiple workers running, claiming a job needs to be atomic. Otherwise, two workers could pick up the same job before either one updates its status.

I plan to explore PostgreSQL transactions and row-level locking to handle this.

### What if a worker crashes?

Suppose a worker claims a job and crashes before finishing it. Without a recovery mechanism, that job could remain stuck.

One approach I want to implement is a lease system, where a worker claims a job for a limited period. If the lease expires without completion, the job can become available again.

### What if a job fails?

Some failures are temporary, like a network request timing out. Others won't be fixed by trying again.

I want to add retry limits, exponential backoff, and a dead-letter queue so failed jobs can be handled without retrying forever.

### What if a job runs twice?

A worker could finish sending an email but crash before recording that the job succeeded. When the system recovers, it might run that job again.

This is one reason I'm interested in at-least-once delivery and idempotency. I want to understand how real systems handle duplicate execution rather than assuming every job will run exactly once.

### How do I know the queue is reliable?

Unit tests are a starting point, but they don't tell the whole story.

As the project grows, I want to test concurrent workers, simulate crashes at different points in the job lifecycle, and measure throughput and latency.

These are design goals for future versions, not features the current implementation already supports.

## Why I started this project

I've used Python to build applications, but I wanted to understand more of what happens behind the scenes.

Job queues seemed like a good place to start because they connect several areas of software engineering that interest me: databases, concurrency, system design, and fault tolerance.

Rather than jumping straight into an existing queue framework, I decided to build a small one myself and gradually add the features that make these systems reliable.

I don't expect the first version to handle everything. The point is to understand why each new feature is needed, what trade-offs it introduces, and how to test whether it actually works.

I'll keep updating the project as I build and learn more.
