# Independent Path 3 audit

Reviewed the decoder, covariance derivation, arithmetic-tail parsing, Gram consequences and actual nested grid. Initial producer SHA-256: `defec6f08530e8bef97b65f72031e945f8e9eb8ae3f708a28deed358ee78778c`. After the authorized source-binding repair: `e68d907c5adda3c626c07bae0a008e3e9a10b90c4b0aa8e350bb1f600c2b662d`.

## Material finding, repaired

The initial single-window parser checked its end-to-end source hash but read the remote tail vector without checking the remote formal hash or binding it to the parent's remote dependency. In a temporary directory, replacing the degree-14 remote vector by zeros while leaving its hash stale was accepted. The reported maximum bias fell from 0.5959293953 to 0.1093569109, which could falsely promote the single-window rounding claim.

The repaired producer checks the remote formal projection through the original remote verifier, binds its digest to the matching parent dependency, checks the frozen degree/time/sample/window/bin/scale contract, validates vector lengths/nonnegativity, and independently reconstructs the mixed remote vector from both bound components. It also checks the multiscale degree, component weights, centered offsets and distinct acquisition count, plus single-window time/sample/degree fields. Existing source artifacts and certificate values did not change. Stale, separately readdressed, and readdressed wrong-time dependency tests now reject.

## Independent checks

- `check_consequences.py` uses only exact Python rational/integer arithmetic. It reconstructs all 100 variance intervals, the deterministic noise-radius margin, and the variance50 ratio. It also verifies the Gaussian union bound with rational lower Taylor sums for the positive exponential, without importing Arb or using floating exponentials.
- A separate direct NumPy calculation forms both actual 8,900-by-50 design matrices, Gram matrices and decoders. All 100 numerical variance diagnostics lie inside the certified bounds. Its target-50 variance ratio is approximately 1.0012730013, consistent with the certified lower ratio 1.000265975. This is an independent numerical control, not an outward proof.
- Exact shared-grid indices were checked. Omitting the reuse cross term loses about 1.0330665e-6 from the squared-weight sum, understating it by about 0.5068%. The current producer sums sample weights before covariance and retains the term correctly.
- The Neumann row bound is sound: row-n correction norm is at most q_n/(1-q), so triangle and reverse-triangle bounds enclose the squared iid noise gain. The weighted adversarial bound follows from G >= (1-q)I and the exact weighted dual norm of the decoder row.
- Half-integer ties, malformed dyadic vectors and wrong acquisition contracts have explicit negative/boundary controls.

Final focused run: **5/5 audit tests passed**; see audit_checks.log. Root's fresh complete dependency records were inspected: multiscale finite/Gram reconstruction PASS (417s), both MPFR remote reconstructions and single-window finite/Gram reconstruction PASS (combined 394s). These reconstruct existing mathematical inputs; a source digest alone would not suffice.

## Scientific boundaries that must remain explicit

1. Circular Gaussian sigma means E|epsilon_j|^2=sigma^2; each real component has variance sigma^2/2. Other conventions change the tail exponent.
2. Decoded coefficient noises are correlated. The union bound does not require independence between coefficients; iid is imposed at the physical observation level only.
3. The designs' W-norm balls differ. Do not infer cross-design superiority from equal weighted radius alone. A common coordinatewise sensor bound implies both weighted bounds, and the iid same-vector variance comparison is directly comparable.
4. The single-window bound above one half is an insufficient certificate, not proof that recovery fails. The multiscale variance increase is a proved comparison for target 50, not every coefficient.
5. Finite precision used to execute the actual decoder, arbitrary sensor correlation, non-Gaussian tails, and physical model error need their own allowances. This package certifies the mathematical decoder under its stated noise models.
