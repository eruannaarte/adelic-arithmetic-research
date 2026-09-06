# Arithmetic acquisition contract

Declared before the new approximation search: retain 8,900 nominal times and
both physical windows. Compare polynomial degrees 6, 8, 10 and 12 for the
continuous families

`beta(t'/890) + A sin(omega*t'/890 + phi) + h`,

where beta is any complex polynomial of degree at most p, `|A| <= B`, real
`|omega| <= Omega`, and phi is any real phase. The physical clock is shared and
affine, `t' = a*t+b`, with `|a-1| <= 1e-14` and `|b| <= 1e-11`.
These clock bounds are mathematical assumptions, not measured calibration.
The independent declared weighted mismatch allowance is `||h||_W <= 1e-6`;
the sensor and digitization allowance is `eta=4e-5`.

Test frequency upper bounds Omega = 1/2, 1, 2, 3. Optimize the sufficient
amplitude capacity over the four degrees, including the inherited complete
arithmetic tail, Gram floor, digital correction, mismatch, clock distortion,
and the actual reconstructed normal residual. A failed sufficient bound is
not an impossibility result. Synthetic data will use degree-six beta so that
the same readings legitimately compare every tested degree.

For future-data capacity and minimum-error tables, use one declared normal
residual ceiling `1e-30` across all families. Every future solve must verify
this ceiling from its own readings and proposal. The actual fixture table
retains its own reconstructed residuals and verifies they meet that ceiling.

The affine clock preserves the unrestricted polynomial nuisance space. It
changes the sinusoidal frequency upper bound to `(1+1e-14)*Omega`; its phase
shift is already covered by arbitrary phi. The arithmetic signal distortion
will be bounded using the complete, absolutely convergent divisor-envelope
derivative series. No finite source fixture replaces that uniform envelope.
