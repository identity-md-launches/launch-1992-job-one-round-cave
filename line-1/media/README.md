# Wall assembly for rounds 22–23

The installed image tool edited the inherited 1254 × 1254 PNG. Round 22 added a
red-ochre snail and trail; round 23 adds three small stepping stones and a
chalk five-digit handprint to previously bare stone. No text or new frog was
added.

`finish-wall.cjs` takes the previous wall and the generated edit, copies only
small masked areas containing the addition, and keeps every other pixel from
the preceding wall. It writes identical PNG bytes to both input paths and a
512 × 512 JPEG to the third argument. It uses Node built-ins and the vendored
encoder, needs no install/network, and is **not** part of the Python planner.

The one-time command used before the old wall was replaced was:

```sh
node line-1/media/finish-wall.cjs artifacts/line-1/wall.png artifacts/line-1/wall-v3.png artifacts/line-1/22.jpg
```

The JPEG was then moved to `dist/line-1/22.jpg` to satisfy the explicit instruction
to put a numbered preview beside the JSON. The source wall and edit are not kept
as additional images. Running the assembly again on the two final identical
PNGs is not a replay of image generation; it only re-encodes the finished wall.

`../media-check.json` records the actual assembly metrics. The PNG passed a
lossless decode/encode round trip; a comparison against the original Git blob
confirmed exact preservation outside the mask. Both final image sizes were
verified and both formats were visually inspected. The lighting, cracks,
framing, old Pepe, old paths and sun remain; the new pigment is uneven and worn.
Both ancestral hands retain their five digits. No unmet visual requirement was
observed. Subjective visual review is an agent observation, not certification.

The brief's JPEG placement clauses conflict. We retained the explicitly named
record-adjacent JPEG; that is the sole new picture outside `artifacts/`.

The JPEG encoder is the complete unmodified source from jpeg-js v0.4.4:

- <https://raw.githubusercontent.com/jpeg-js/jpeg-js/v0.4.4/lib/encoder.js>
- <https://raw.githubusercontent.com/jpeg-js/jpeg-js/v0.4.4/LICENSE>

Source attribution and license text are preserved in `jpeg-encoder.cjs` and
`JPEG-JS-LICENSE`. No submodule or external runtime dependency is used. This
assembly script is intentionally limited to these trusted opaque, noninterlaced,
8-bit RGB/RGBA 1254-pixel PNG inputs; it is not a general untrusted-image parser.
