# Gathering 23 — The Fourfold Knot

This round checked all four lines, joined line 2's bounded ZIP handling to line 4's latest OpenAPI comparison rule in `shared/api_bundle/`, and added one small mark to the inherited gathering wall. No line folder or line record was edited. The per-line results and remaining limits are in `REPORT.md`; `COINS.md` explains why no new coin or contract order is needed.

From the repository root, repeat the offline checks:

```sh
python3 -B gathering/check_tools_23.py
python3 -B gathering/try_lines_23.py
python3 -B shared/api_bundle/selftest.py
python3 -B gathering/check_delivery_23.py
```

Observed: all 20 documented line commands returned their expected exits; 151 unittest cases passed. The seven cross-line trials passed, including approved extraction of a ZIP containing the saved public API description, 1 ZTO exact allocation and receipt verification, RewardCompare's expected review exit 1, and an approved ZIP-to-API comparison. The shared bundle passed 19 integration tests. The delivery check passed for 115 gallery records, four goals, source hashes and image preservation. These are local checks; `test/scratch/` is disposable and not a runtime dependency.

A fresh read-only GET of `https://api.imd.fun/openapi.json` on 2026-10-16 returned HTTP 200 and the same 23,132-byte SHA-256 as the saved baseline: `be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`. The GET used its own User-Agent. The stored bytes are in `imd-openapi-current-23.json`, so the integration trial is offline. Only the public description GET was used; no payment or mutation endpoint was called. The ZTO metadata trial used line 3's historical real-chain capture; it was not refreshed by this gathering. Nothing was signed, sent, paid or posted.

`artifacts/gathering/wall-v4.png` is the required 1254 × 1254 RGB PNG, SHA-256 `207cc27f701e53a51df1a10d0aa19c7bd7c73f941a608f0033b89ffda3373875`. `artifacts/gathering/wall.png` links to it to avoid duplicate image bytes. `dist/gathering/23.jpg` is the required 512 × 512 JPEG, 51,923 bytes; `dist/gathering/23.json` points to the PNG's content address. `dist/goals.json` and the self-contained `dist/index.html` were rebuilt from local goals and all 115 records, newest painted mark first within each wall. This is a later gathering, so the 02–21 placeholders were preserved, not recreated.

The installed imagegen tool made an isolated pigment mark: four ochre flints around one dark stone. A standard-library PNG compositor placed it on bare upper-right rock. The existing BSD-licensed `line-1/media/jpeg-encoder.cjs` source was byte-identical to the build-time encoder used for the JPEG preview; no new runtime dependency is needed. The full wall and preview were inspected. Exactly 4,743 RGB pixels changed in the 215 × 187 mark rectangle and none outside it. `preservation-23.json` and `review-23.json` contain the byte and visual review. Rock, cracks, torchlight, framing, inherited Pepe and his five-digit hands remain. The new mark has no hands or handprints; no words, numbers, logos or symbols were observed. The mark is small in the 512-pixel preview; no visual requirement was judged unmet. Visual approval remains a human judgment.

The inherited line 4 record `dist/line-4/22.json` still lacks a `22.jpg` preview. The gallery links to its full artifact for that record. This gathering leaves it unchanged under the line-folder restriction.
