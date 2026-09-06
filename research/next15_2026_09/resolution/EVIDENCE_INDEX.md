# Three-cycle evidence map

| Cycle | Substantive advance | Before / after | Proof and certificate | Controls / limit |
|---|---|---|---|---|
| R1 | Graph-locality bound on target-dependent Grams | Exact center →919 uniformly certified placements | PROOFS.md R1; placement.py; placement_certificate.json; check_placement.py | Exact first differing walk order; independent dense Arb exponential; full-field output, not fixed even modes |
| R2 | Explicit decoder for an unknown target and source | Fixed realized target floor →907 unknown target locations under finite noise | PROOFS.md R2; localization.py; localization_certificate.json; check_localization.py | Reflection and first-moment controls; full-state regression; zero-source obstruction |
| R3 | Restricted spatial sensing operator with source floor and localization | Full output →99 spatial-average rows under21-target prior | PROOFS.md R3; window.py; window_certificate.json; check_window.py | PSD discarded Gram; least-singular-direction noise example; exact symmetric-pair rank obstruction |

All numerical examples in localization_example.json and window_example.json are explicitly floating regressions, not certificate inputs. The new inequalities are exact-rational consequences of complete analytic proofs plus the inherited central interval certificate. That baseline's rational Taylor/metric/cover consequences are rechecked automatically; its model-to-Arb enclosures retain their documented independent prior replay. Acquiring spatial-average rows directly is an additional implementation capability, not something supplied by an orthogonal change of coordinates.
