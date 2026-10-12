# Marshal

**A Python job queue built from scratch to explore reliable background processing, concurrency, and fault tolerance.**

Applications often need to perform work that shouldn't block the main request-response cycle: sending emails, processing uploaded files, generating reports, or running computationally expensive tasks.

A job queue solves this by separating the application that submits work from the workers that execute it.

Marshal is my attempt to understand and build that infrastructure from the ground up. It starts with a small in-memory queue and will gradually evolve into a persistent, fault-tolerant background job system.

The interesting challenge isn't getting jobs to run when everything works. It's figuring out what happens when things go wrong: workers crash, jobs fail, processes restart, and multiple workers compete for the same task.

## How It Works

The basic job lifecycle looks like this:

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

An application submits a job containing a task name and its payload. A worker claims the job, looks up the appropriate handler, executes it, and marks the job as completed.

The current implementation runs entirely in memory. It provides a foundation for introducing persistence, concurrency, retries, and failure recovery.

## Current Implementation

Marshal currently includes:

- **Job submission:** Add jobs to an in-memory queue with a task name and payload.
- **Job claiming:** Retrieve queued jobs for processing.
- **Job completion:** Mark successfully processed jobs as completed.
- **Status tracking:** Count jobs by their status.
- **Worker demonstration:** Execute jobs through registered task handlers.
- **Automated tests:** Verify the queue's core behavior.

The current demo runs a worker loop sequentially in a single Python process. It demonstrates the basic job lifecycle rather than a fully independent or distributed worker system.

### Example

```python
from marshal_queue.memory_queue import InMemoryQueue

queue = InMemoryQueue()

queue.enqueue("send_email", {"to": "sara@example.com"})

job = queue.claim()

if job is not None:
    print(job.task_name, job.payload)
    queue.complete(job.id)
```

This example submits a job, claims it, inspects its contents, and marks it as completed.

Actual task execution is handled separately by the worker's registered functions.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ayazayan/marshal.git
cd marshal
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install development dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Run the demo

```bash
python demo.py
```

The demo submits three jobs:

1. Send an email to Sara.
2. Resize an image.
3. Send an email to Omar.

A worker claims each job, executes the corresponding handler, and marks it as completed.

The handlers currently simulate these operations by printing messages. No actual emails are sent or images modified.

### 5. Run the tests

```bash
python -m pytest
```

## Project Structure

```text
marshal/
├── marshal_queue/
│   └── memory_queue.py
├── tests/
├── demo.py
├── requirements-dev.txt
└── README.md
```

| Component | Purpose |
|---|---|
| `marshal_queue/` | Core queue implementation |
| `tests/` | Automated tests |
| `demo.py` | Example worker and job execution |
| `requirements-dev.txt` | Development dependencies |

The Python package is named `marshal_queue` rather than `marshal` to avoid conflicting with Python's built-in `marshal` module.

## Roadmap

Marshal is being developed incrementally. Each milestone introduces a new engineering problem to solve.

- [x] **In-memory queue:** Implement job submission, claiming, completion, and status tracking.
- [x] **Basic worker:** Demonstrate job execution through registered handlers.
- [x] **Initial tests:** Validate the core queue operations.
- [ ] **PostgreSQL persistence:** Store jobs durably so queued work survives application restarts.
- [ ] **Concurrent workers:** Coordinate multiple workers without allowing the same queued job to be claimed simultaneously.
- [ ] **Retries and failure handling:** Retry failed jobs with configurable policies and move repeatedly failing jobs to a dead-letter queue.
- [ ] **Worker crash recovery:** Detect abandoned jobs and make them eligible for processing again.
- [ ] **HTTP API:** Expose job submission, status inspection, and management through an API.
- [ ] **Monitoring dashboard:** Visualize queue activity, job states, failures, and worker health.
- [ ] **Performance and reliability testing:** Measure throughput and latency, simulate crashes, and test concurrent execution.

## Engineering Challenges

Building a reliable job queue raises questions that go beyond storing and retrieving tasks.

### What happens if a worker crashes?

A job shouldn't remain stuck forever because the worker responsible for it disappeared.

Future versions will explore leases, timeouts, and recovery mechanisms that allow abandoned jobs to be processed again.

### How do multiple workers avoid claiming the same job?

When several workers access the same queue, claiming a job must be atomic.

The PostgreSQL implementation will explore transactions and locking mechanisms to coordinate concurrent workers.

### What happens when a job fails?

Some failures are temporary. Others require investigation.

Retry policies, exponential backoff, and dead-letter queues will help manage failures without endlessly retrying jobs that cannot succeed.

### Can a job execute more than once?

A worker might complete an external operation but crash before recording that the job succeeded.

Recovering the job could cause the operation to run again.

Marshal will explore at-least-once delivery semantics and idempotent handlers to understand and manage this trade-off.

### How can reliability be measured?

Passing unit tests doesn't guarantee that a system behaves correctly under concurrency or failure.

Future testing will include concurrent execution, failure injection, throughput measurements, and recovery scenarios.

These capabilities are planned rather than implemented. The current version focuses on establishing a small, understandable foundation.

## Why I'm Building Marshal

I wanted to understand the systems behind background tasks rather than treating job queues as black boxes.

Building one from scratch gives me the opportunity to explore state management, concurrency, database transactions, fault tolerance, and distributed systems through practical implementation.

I'm intentionally developing Marshal in stages. Each feature introduces a specific engineering problem to solve, test, and document.

The long-term goal is to build a system whose reliability can be explained and demonstrated, not just assumed.

---

Marshal is an ongoing engineering project. Features are being added incrementally, with an emphasis on understanding the design decisions and trade-offs behind each implementation.
