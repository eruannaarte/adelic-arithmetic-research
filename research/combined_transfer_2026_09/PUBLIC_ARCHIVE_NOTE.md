# Public reproducibility archive and third-party reference copies

The public reproducibility package contains all authored mathematical proofs,
numerical proof inputs, source code, certificates and research evidence in the
predecessor packages. It omits three third-party reference copies from the
historical archive:

- `five_paths_2026_09/path2_harmonic/borsuk_1933_source.pdf`
- `five_paths_2026_09/path2_harmonic/borsuk_page1.png`
- `five_paths_2026_09/path2_harmonic/borsuk_page2.png`

These are the full publisher scan and two page images of a cited Borsuk
article, not authored research proofs or numerical certificate inputs. The
bibliographic citation, DOI, publisher record and publisher-provided source
link remain in the unchanged
[historical source note](../five_paths_2026_09/path2_harmonic/SOURCES.md).
The accepted theorem and the hypotheses needed for its application remain
identified there and in the authored proof.

The original local archive's **660 files remain unchanged**. Its complete
660-entry SHA256 record is retained in `PREVIOUS_ARTIFACTS_SHA256.json`.
The public archive includes **657 predecessor files**, together with this new
research package. No numerical proof source, coefficient table, infinite-tail
bound, actual-model reconstruction or computed-data certificate is omitted.

`integrity.py` allows absence of only the three exact paths above, and only
with their original hash identities pinned in both the checker and historical
manifest. If any of these references is present, its hash is checked normally.
Every other historical file must be present and match its recorded hash. The
checker reports the number of present verified predecessor files and lists
any omitted archival references explicitly; it does not describe the public
archive as containing all 660 original files.
