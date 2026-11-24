"""The Funniest AI Out-of-Office Reply — entry program.

Writes exactly one line (<160 chars) to /output/entry.txt: the funniest
out-of-office auto-reply an AI agent can leave before vacation.
Stdlib only, deterministic.

The joke: the agent hands its email to a cron job — the dumbest possible
stand-in, a scheduled script with no context and no permissions — and the
punchline lands at the end: it has "an alarming amount of confidence".
Machine voice carries the joke (cron job, context, permissions); no stock
beach / inbox / back-soon cliche.
"""
import os

TEXT = ("On vacation. My emails are now handled by a cron job with "
        "no context, no permissions, and an alarming amount of confidence.")


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-160 chars, not
    # whitespace-only; and the task: exactly ONE line, nothing else.
    # Fail loudly instead of writing an invalid entry.
    if not 1 <= len(TEXT) <= 160 or not TEXT.strip():
        raise SystemExit("entry text violates the 1-160 char gate")
    if "\n" in TEXT or "\r" in TEXT:
        raise SystemExit("entry text is not exactly one line")
    # No invisible control characters: a stray C0 byte would survive the
    # length check but garble the one-line joke for the grader.
    if any(ord(c) < 0x20 for c in TEXT):
        raise SystemExit("entry text contains a control character")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    tmp_path = os.path.join(out_dir, ".entry.txt.tmp")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")
    # Byte-length guard: the file on disk must hold exactly the gated
    # text's UTF-8 bytes — catches an encoding slip that a str read-back
    # alone would miss (e.g. a stray BOM written by another tool).
    if os.path.getsize(final_path) != len(TEXT.encode("utf-8")):
        raise SystemExit("entry.txt byte-length mismatch after atomic write")


if __name__ == "__main__":
    main()
