# Joint preparation calibration bridge

Read [REPORT.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/REPORT.md), [PROOFS.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/PROOFS.md), and [CALIBRATION_PROTOCOL.md](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/CALIBRATION_PROTOCOL.md). The new theorem conditions on measured centers and retains one common four-component systematic correction across A and B. Existing browser and preparation research files are preserved.

From the Math repository root:

```sh
/private/tmp/math-five-paths-venv/bin/python -S research/unified_query_2026_09/preparation/calibration_bridge.py
/private/tmp/math-five-paths-venv/bin/python -m unittest discover -s research/unified_query_2026_09/preparation -p test_calibration_bridge.py -v
/private/tmp/math-five-paths-venv/bin/python research/next15_2026_09/preparation/verify.py --deep
```

Expected: the exact calibration replay passes, ten focused tests pass, and all three inherited complete ODE reconstructions pass. The new checker needs only Python's standard library. The optional deep reconstruction uses the prior package's pinned numerical runtime and takes roughly a dozen seconds on the prepared host. It does not modify prior artifacts.

The source link is explicit: each ordinary run reconstructs the fixed rational decoder, source contraction, local and shared preparation gains, and noise gains from the preserved Cycle 2 interval artifacts, validates their previous exact consequences, and records hashes. It does not freshly integrate the ODE unless the deep command is run. Validation is cached by immutable file contents, so altered files do not reuse an earlier acceptance.

[record.schema.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/record.schema.json) defines the input shape. The executable adds exact rational/domain/certificate checks beyond JSON Schema. [synthetic_calibration.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/synthetic_calibration.json) is a complete, explicitly synthetic example; [certificate.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/certificate.json) records its exact rational consequences. The `--write` switch deliberately regenerates that certificate; ordinary verification is read-only. Use `--record /absolute/path/to/record.json` to assess another record.

The physical status is **NOT_RUN** for the fixture. A physical-record label yields `REQUIRES_EXTERNAL_PROVENANCE_AND_MODEL_VALIDATION`, even if its conditional mathematics passes. This is intentional: neither evidence-reference strings nor a passed algebraic gate independently authenticates measurements or model adequacy. [VALIDATION.json](/Volumes/KINGSTON/Vibecoding/Math/research/unified_query_2026_09/preparation/VALIDATION.json) records the checks completed in this extension.
