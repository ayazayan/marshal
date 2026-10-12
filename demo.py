from marshal_queue.memory_queue import InMemoryQueue


def send_email(payload):
    # Pretend to send an email. A real version would talk to an email service.
    print("  sending email to", payload["to"])


def resize_image(payload):
    # Pretend to resize an image.
    print("  resizing", payload["file"])


# The worker uses this to look up which function handles each kind of job.
HANDLERS = {
    "send_email": send_email,
    "resize_image": resize_image,
}

queue = InMemoryQueue()

# First, the "website" adds some jobs to the line.
print("Adding jobs...")
queue.enqueue("send_email", {"to": "sara@example.com"})
queue.enqueue("resize_image", {"file": "photo.png"})
queue.enqueue("send_email", {"to": "omar@example.com"})
print(" ", queue.count("queued"), "jobs waiting")

# Then the "worker" keeps taking jobs until there are none left.
print("Worker starting...")
while True:
    job = queue.claim()
    if job is None:
        break  # nothing left to do
    print("Took job", job.id[:8], "-", job.task_name)
    HANDLERS[job.task_name](job.payload)  # do the actual work
    queue.complete(job.id)  # cross it off the list

print("Done.", queue.count("succeeded"), "jobs succeeded.")
