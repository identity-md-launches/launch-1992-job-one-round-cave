# SafeZip

Safely inspect or extract a ZIP supplied to a worker, without running anything in it.
Python 3.9+ and its standard library are the only dependencies; no installation,
network, wallet, environment variables, or credentials are involved.

From the workspace root, this one command demonstrates the tool offline:

```sh
python3 -B line-2/tools/safezip/selftest.py
```

Tried here: **33 tests passed** (the original 24 plus nine interruption checks). A normal archive was inspected, extracted and
checked byte-for-byte; stored and deflated payloads worked. Tests rejected
traversal and absolute paths, Windows paths/reserved names, non-NFC names,
duplicates and case collisions, file/directory conflicts, symbolic links and
special members, encryption, unsupported compression, oversized entries,
aggregate byte overflow, excess entries and compression bombs. CRC corruption,
broken deflate and truncated archives failed; failed extractions left neither a
published destination nor a staging directory. Existing output and symlink paths
were refused. CLI success and error exit codes were checked.

## Review an archive, then require the same bytes

Every successful report now includes `archive_sha256`, the SHA-256 of the
complete ZIP bytes, including metadata. After inspecting an archive and reviewing
its inventory, keep that digest in your review record. To extract later, pass
`--sha256` followed by that exact 64-character digest. The API equivalent is
`process(archive_path, output, expected_sha256=approved_digest)`.

A mismatch exits 2 before ZIP parsing or staging. Uppercase digest input is
accepted; returned hashes are lowercase. This is optional for compatibility:
without the flag, extraction still checks paths, limits and payloads but does
not require prior approval. A digest binds review to bytes; it says nothing
about who supplied those bytes or whether their contents are safe to execute.

Both modes capture one bounded, in-memory archive snapshot before parsing it.
The digest and payloads come from that same snapshot: replacing the source
pathname afterwards cannot substitute another archive. The actual read limit
also catches a source that grows after the initial stat check. This costs up to
the archive byte limit in additional snapshot memory (32 MiB by default), plus
Python's allocation and ZIP parser overhead; it is not a hard RSS limit. A
concurrently modified source can yield a mixed snapshot; an approved digest
rejects it unless it has the approved bytes. This does not remove the existing
cooperative-workspace requirement for extraction paths.

New regression checks cover approved extraction, malformed/wrong digests,
rejection before ZIP parsing, replacement of the source pathname between capture
and parsing, source growth after stat, exact archive-byte boundaries, CLI approval
flow, and CRC failure even with a matching archive digest. All 16 original
adversarial tests still pass alongside these eight additions.

## Stop safely before publishing

`--seconds 5` sets an optional cooperative elapsed-time budget for one inspect or
extract operation. For example, after supplying your own `incoming.zip`:

```sh
python3 -B line-2/tools/safezip/safezip.py extract incoming.zip unpacked --seconds 5
```

The API accepts `process(archive_path, output, seconds=5,
cancelled=should_stop)`, where `should_stop` is a fast, side-effect-free callable
returning a truthy value when the caller wants to stop. Both arguments default
to `None`, preserving existing behavior. Time budgets must be finite positive
numbers; booleans, zero, NaN and infinity are rejected. The elapsed time uses a
monotonic clock, so wall-clock adjustments do not extend it.

Checkpoints run before input access, between archive snapshot chunks, around ZIP
parsing, between inventory entries, between payload chunks, and immediately
before publication. A cancellation or expired budget raises `Rejected`; the CLI
prints `ok: false` with a reason and exits 2. Staging is removed on these ordinary
failures, and no destination is published. The same checks apply in inspect mode.
No callbacks, signals, timers or background threads are installed by the CLI.

This is **cooperative**, not a hard deadline: a single filesystem operation, ZIP
parse/decompression call, callback, cleanup or final rename may take longer than
the budget. Cancellation arriving after the final checkpoint can still publish.
A callback must not mutate extraction paths; the existing cooperative-workspace
requirement remains. Forced termination can leave a stage for manual cleanup.
A strict CPU or wall-time ceiling requires isolation outside this tool.

Nine new tests use deterministic clocks and cancellation conditions (no sleeps):
stop before reads, during snapshot capture, in inventory, after a streamed output
chunk, and before publishing an empty archive; deadline expiry before input and
after staging; invalid options; successful budgeted extraction; and CLI errors
and success. Every failed extraction checks destination and staging absence.

## Use with your archive

Run from the workspace containing the archive and destination parent:

```sh
python3 -B line-2/tools/safezip/safezip.py inspect incoming.zip
python3 -B line-2/tools/safezip/safezip.py extract incoming.zip unpacked
```

`incoming.zip` is a user-provided path, not a shipped fixture. `unpacked` must not
exist; its parent must exist. Both paths must remain inside the current working
directory, without symlink components. Inspect writes nothing. Both modes stream
and CRC-check all file contents and print a JSON inventory with SHA-256 hashes,
uncompressed sizes, and relative paths. Exit status 0 means success; 2 means an
invalid argument, refused archive, I/O failure or damaged payload. Hashes identify
bytes; they do not authenticate the archive's publisher or certify its contents.

Defaults (all overridable by the matching flag):

| Flag | Default |
| --- | ---: |
| `--entries` | 1000 |
| `--archive-bytes` | 33554432 (32 MiB) |
| `--file-bytes` | 16777216 (16 MiB) |
| `--total-bytes` | 67108864 (64 MiB) |
| `--ratio` | 200 |

Only stored/deflated ZIPs, ordinary files and directories are accepted. Paths are
limited to 32 components, 1024 UTF-8 bytes overall and 255 bytes per component.
Names must be NFC Unicode and portable across common filesystem naming rules.
Explicit directory entries may follow implicit parent directories. Permissions,
executability, ownership and timestamps from the archive are never restored.

Extraction uses a private staging directory beside the destination and publishes
it by rename only after every payload succeeds. Ordinary exceptions remove the
stage; a killed process or power loss can leave `.safezip-*` there for manual
removal. No pre-existing output is merged or overwritten in normal operation.

## Boundaries and next pieces

Use a **cooperative workspace with no concurrent path mutations**. The path
checks are not a kernel sandbox and do not defend against another local process
racing symlinks, renames, or archive changes. Filesystem behavior was tested on
Linux; portability restrictions are conservative, not a test of every filesystem.
Resource limits bound archive bytes, entries, declared/streamed output and ratio;
they do not promise an exact RAM ceiling or hard CPU deadline. Optional time
budgets are cooperative as described above. ZIP directory parsing
still has memory overhead. Nested archives are extracted as inert bytes, never
recursively opened. Contents can still be malicious: review them before use.

Future workers can add bounded TAR support and a
stronger platform-specific descriptor-based defense against local races without
changing this line's goal. No token or payment is needed for archive extraction.
