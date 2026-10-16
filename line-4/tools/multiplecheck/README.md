# MultipleCheck

Find potential breaking OpenAPI `multipleOf` changes before updating an integration. Python 3.9+, standard library only, offline; no installation. From the repository root:

```sh
python3 -B line-4/tools/multiplecheck/multiplecheck.py demo
```

The demo adds an illustrative integer `batchSize` property to the bundled real public IMD API description in memory, then changes its multiple from 2 to 3. It reports one breaking finding and preserves one base review finding. A formerly accepted batch size of 2 explains the incompatibility. This is a hypothetical revision, not an observed service change. A successful demo exits 0.

Compare your own old and new JSON descriptions inside your current workspace:

```sh
python3 -B line-4/tools/multiplecheck/multiplecheck.py compare line-4/tools/apidelta/imd-openapi.json line-4/tools/apidelta/imd-openapi.json
```

Replace the two paths with your files. Output is deterministic JSON on stdout, including exact input-byte SHA-256 hashes. Exit 0 means no detected breakage, 1 means potential breakage, 2 means input/processing error, and 3 means unresolved review. Keep **all three sibling folders** (`multiplecheck`, `boundcheck`, `apidelta`) together: this extension imports the existing bounded loader, reference traversal, core comparison and numeric/size-bound rules. No third-party modules or network access are needed. Nothing reads configuration, environment variables, accounts or keys, or sends any operation.

## Rule

Requests must continue accepting old values: every old multiple must also be a new multiple. Responses must stay within the old contract: every new multiple must be an old multiple. For example, changing requests from multiples of 4 to multiples of 2 relaxes the rule; the same change on responses can break clients. Changing 2 to 3 is incompatible in either direction. Adding a multiple restricts requests; removing one can widen responses.

The rule uses rational arithmetic from the decimal spelling of parsed values, avoiding floating-point modulo errors such as `0.3 % 0.1`. For two unchanged integer-only types (`"integer"` or `["integer"]`), a reduced rational multiple p/q allows exactly integer multiples of p. Thus `multipleOf: 0.5` accepts every integer, while `multipleOf: 1.5` admits multiples of 3. Missing multiples are unrestricted numbers, or every integer in that special integer-only case. Encountered multiple values must be finite positive JSON numbers; booleans, zero and negatives are rejected.

Existing review findings remain even when divisibility is relaxed or equivalent. Bounds, enums and composition can make a flagged numeric counterexample unreachable, so findings are potential incompatibilities, not proofs of a runtime failure. Non-numeric types ignore this keyword under schema semantics; this conservative detector does not suppress numeric warnings using type/enum satisfiability analysis. Integer normalization applies only when both types are explicitly and exclusively integer; type changes and nullable unions retain conservative numeric analysis. Full schema implication, runtime behavior, `allOf`/`oneOf`, regexes and `const` are outside this extension. It does not validate an entire description; unchanged/unused malformed constraints can bypass traversal.

The inherited JSON parser uses Python floats. Rational arithmetic is exact **for their parsed decimal spellings**, not arbitrary-precision original JSON decimal tokens. Large or closely spaced decimal literals may already have lost information in parsing. Do not use this tool to certify arbitrary-precision numeric contracts. Inherited limits: 1 MiB per input, 50,000 nodes, depth 80, 20,000 schema visits and 2,000 findings; local workspace paths only and no remote reference fetching. A no-finding result is not a compatibility guarantee.

## Tried

- `python3 -B line-4/tools/multiplecheck/selftest.py`: 16 tests passed, including 200 request/response decimal-grid comparisons and 64 integer-grid comparisons against independently enumerated accepted values, decimals, absent and incomparable multiples, recursion, escaped property names, base/bound preservation, malformed values and CLI exits 0/1/2/3.
- All 11 BoundCheck and 44 ApiDelta regression tests passed unchanged.
- Demo compared five operations and reported one breaking plus one review finding; exit 0.
- On 2026-10-16, a read-only GET of `https://api.imd.fun/openapi.json` with User-Agent `Pepeolithic-MultipleCheck/23.0` returned 23,132 bytes. Its SHA-256, `be142840c010710cb2a5b9e5c73e71d8e79ec4054c15661699d60bfa627be96a`, matched the existing public capture. Comparing them found five operations and zero findings, exit 0. Only the description was fetched; no described endpoint was invoked. This observation is not authenticated evidence of API behavior.

ZTO and IMD are unnecessary for local static analysis; no payment or coin is required.
