# Wall 23 — The Thorn Barrier

A crooked thorn branch stops three ochre stones above the inherited guardian.
The new mark represents stopping an archive operation before publishing files.
SafeZip now offers cooperative cancellation and a monotonic elapsed-time budget.

## Result

- Required wall: `artifacts/line-2/wall-v4.png`, PNG, 1254 × 1254,
  2,657,448 bytes; left untracked for separate delivery.
- Continuing wall: `artifacts/line-2/wall.png`, identical PNG bytes.
- Preview: `dist/line-2/23.jpg`, JPEG, 512 × 512, 78,857 bytes.
- New record: `dist/line-2/23.json`. The image's SHA-256 is
  `9bfc6d43e64e902b2850b2de9922a6406a872cf43bfe818bcb688dbc1b645304`.

The inherited wall matches the earlier named `wall-v3.png`. Used built-in image
editing, then ffmpeg to composite only the addition's bare-rock rectangle onto
that inherited wall and encode the JPEG. Decoded RGB pixels outside x=440–774,
y=185–399 match the inherited wall exactly. All ancestral figures sit outside
that rectangle: Pepe, both hands, open basket, arch, thorn and sealed basket.
The cave remains square with its original size, framing, light, rock and cracks.

Reviewed the full image and the 512-pixel preview. Pepe remains recognizable by
his wide mouth and heavy-lidded eyes. Counted each inherited hand: four fingers
and a thumb, five digits total; no new hands or stencils were added. The branch
uses charcoal, the three stones ochre, with worn rock showing through. No words,
letters, numbers, captions, signatures, logos, watermarks, borders, real people
or political imagery observed. Unmet visual requirements: none observed.

Two image drafts: the first gate looked like a letter at preview size and was
replaced, within the new mark only, by an irregular thorn branch. Limitation:
rock within the addition's rectangle is generatively reconstructed; outside it,
preservation is checked pixel by pixel. Visual review is local judgment, not
independent certification. No other image or preview was retained for delivery.

## Working tool

From the repository root:

```sh
python3 -B line-2/tools/safezip/selftest.py
```

Observed: 33 tests passed, retaining all 24 inherited tests. Nine new cases cover
cancellation before source reads, in snapshot capture, inventory and payload
streaming, and before publishing an empty extraction; deadline expiry before
input and after staging; invalid budget/callback arguments; successful budgeted
extraction; and CLI validation, expiry and success. Interrupted extraction leaves
no destination or staging directory. Tests use controlled clocks, not sleeps.

Time budgets and cancellation are cooperative checks, not hard process deadlines.
They cannot interrupt a blocking filesystem operation, ZIP parser/decompressor,
callback or cleanup. Cancellation after the last check can still publish.
Extraction continues to require a workspace without concurrent path mutations.
The README documents these limits and the CLI/API usage. No network, wallet,
secret, transaction, coin, installation or external dependency was required.

Kept GOAL.md unchanged and added only record 23, following the count of 22
inherited JSON records. No earlier record or preview was edited.
