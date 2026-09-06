# Sources and hypothesis checks

## Primary accepted theorem

K. Borsuk, *Drei Sätze über die n-dimensionale euklidische Sphäre*, Fundamenta Mathematicae 20 (1933), 177–190, DOI [10.4064/fm-20-1-177-190](https://doi.org/10.4064/fm-20-1-177-190). [Publisher record](https://www.impan.pl/en/publishing-house/journals-and-series/fundamenta-mathematicae/all/20/0/93008/drei-satze-uber-die-n-dimensionale-euklidische-sphare), [original PDF](https://www.impan.pl/shop/en/publication/transaction/download/product/93008).

The accepted statement is **Satz II, printed page 178**: every continuous map from the n-sphere into R^n takes equal values at an antipodal pair. I visually inspected that statement in the publisher's scan. P2.1 checks the domain dimension, continuity, padding of the codomain, and reversal-as-antipodality explicitly, then derives the zero of its odd map. The trivial n=0 case is handled directly. This source establishes the topological ingredient, not historical priority for the arithmetic application.

## Density lineage, independently derived here

L. Kronecker, *Näherungsweise ganzzahlige Auflösung linearer Gleichungen* (1884), collected *Werke* III.1, pp47–110: [ETH e-rara original-source scan](https://www.e-rara.ch/download/pdf/5763564.pdf). The scan identifies the original 1884 reports, pp1179–1193 and 1271–1299. We use the classical rational-independence/dense-torus-orbit conclusion as context, but P2.1 supplies an elementary complete proof of the precise continuous-time density statement needed here. No quantitative time bound is imported from Kronecker.

## Interval arithmetic and actual dependency

F. Johansson, *Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic*, IEEE Transactions on Computers 66(8) (2017), 1281–1292, [author's preprint](https://arxiv.org/abs/1611.02831), DOI `10.1109/TC.2017.2690633`. The author's [ball-semantics documentation](https://fredrikj.net/arb/using.html) states the inclusion contract used by our elementary arithmetic, logarithm, pi, and determinant evaluations. Exact rational conversion is through `fmpq`; printed decimal ball strings are never used as finite proof inputs. The replay uses Python 3.12.14, python-flint 0.9.0, and FLINT 3.6.0, with 384-bit Arb and a 512-bit refinement. Correctness of these libraries remains trusted.

## Local research baseline

[AO VI](/Volumes/KINGSTON/Vibecoding/Math/ARITHMETIC_OBSERVABILITY_VI.md), Sections 2–5, supplies the original model, half-DFT upper construction, reflection lower bound, rational six-reading schedule, and .7901 floor. Its original [finite checker](/Volumes/KINGSTON/Vibecoding/Math/arithmetic_observability_full_segre.py) was rerun successfully. AO IV concerns geometric factors and should not be substituted for the full product-simplex local count; P2.2 derives the latter directly.

## Novelty boundary

Targeted primary-source searches covered product probability distributions, nonuniform Fourier recovery, Kronecker sampling, and Borsuk–Ulam harmonic identification. The nearby generalized-sampling literature includes [Adcock, Gataric, and Romero, *Computing reconstructions from nonuniform Fourier samples: Universality of stability barriers and stable sampling rates*](https://arxiv.org/abs/1606.07698). Its abstract concerns stable reconstruction in polynomial or wavelet spaces from nonuniform Fourier data; our factor-product global chord bound is a different declared finite model. No comparative theorem or priority conclusion is inferred from that distinction.

The DFT half-frame, compact simplex calculus, derivative perturbation, maximum-row-sum norm estimate, and finite clock-drift estimate are elementary/classical. The supported addition is their sharpened centered, row-specific application, the concrete interval-certified schedules, and the explicit acquisition/clock/stability table. This was not an exhaustive literature review, and the package claims no discovery of a new general sampling theorem.
