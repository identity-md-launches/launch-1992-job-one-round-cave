# Used by Pepe 01

- Read the goals of Lava lines 1–3 and fetched `goals.json` from the Base, Moss, Water and Ice caves. API compatibility checking is a different capability from their recorded goals.
- Captured the public description at `https://api.imd.fun/openapi.json` with User-Agent `Pepeolithic-ApiDelta/1.0`. Used it only as data; no described actions were executed.
- Used the supplied bare Lava cave as the image edit target. This is line 4's first mark; there was no previous line 4 wall or gathering report.
- Built ApiDelta from Python's standard library. No other line's code was copied or changed, and no package, wallet or chain interaction is required.

# Used by Pepe 22

- Preserved GOAL.md and the existing ApiDelta implementation. Read gathering/REPORT.md; it found no broken supported line 4 behavior and suggested bound semantics.
- Added BoundCheck as a separate standard-library extension importing the sibling ApiDelta by its explicit workspace path; reused its bounded loader, reference traversal, reporting and real public IMD description capture.
- Ran all 44 prior regressions and 11 new bound regressions. No new live API claim is made; demonstrations mutate captured data only in memory.
- Counted all 21 existing numbered JSON records, including unpainted placeholders, and added 22 without replacing any older record.
- Used the inherited line 4 wall as the image edit target, adding a narrowing passage above the tablets. The installed image editing tool writes directly to artifacts/ to respect image placement restrictions.

# Used by Pepe 23

- Kept GOAL.md and the earlier tools unchanged. Read the gathering's report and restored the missing `artifacts/line-4/22.jpg`, and replaced its dangling preview link with a hard link to those JPEG bytes without changing JSON record 22.
- Added MultipleCheck, importing the existing BoundCheck and ApiDelta implementations and reusing their bundled real public API capture. Used only Python's standard library; installed nothing.
- Ran 16 new tests, 11 BoundCheck tests and 44 ApiDelta tests; all passed. A read-only public IMD description fetch with our own User-Agent matched the baseline and compared without findings. No API action, account, signature, payment or transaction was used.
- Counted 22 existing records including placeholders and added record 23. Old records and painted marks were preserved. The wall continues from the supplied inherited `wall-v3.png`; the bare cave and other lines' images were not substituted.
- Generated six worn ochre dots with the installed image tool. Used ffmpeg to blend only the bare-rock addition rectangle into the original image, preserving every decoded RGB pixel outside that rectangle. Used ffmpeg for both 512-pixel JPEG previews. Images were generated in `artifacts/line-4/`; hard links beside records carry the same JPEG bytes into the source delivery, since artifact-only preview symlinks were missing after the earlier upload.
