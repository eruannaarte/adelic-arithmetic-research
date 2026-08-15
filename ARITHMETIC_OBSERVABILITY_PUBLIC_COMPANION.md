# Can a Few Echoes Reveal a Hidden Arithmetic Shape?

> **Public companion to the Arithmetic Observability Atlas**
> This is a science-communication essay and interactive-model guide, not a
> substitute for the formal manuscripts.  The mathematics is not peer
> reviewed, and the physical interpretation below is deliberately identified
> as an analogy rather than an empirical claim.

Imagine that an object is hidden behind a wall.  You cannot inspect it
directly.  You can only send in a small number of precisely chosen tones and
listen to the echoes.

How many echoes would you need before two different hidden objects could no
longer sound the same?  If the echoes are noisy, how different would the
objects have to be before you could reliably tell them apart?  And if some
part of the object is allowed to shift while you listen, which differences
remain observable at all?

The **Arithmetic Observability Atlas** asks versions of those questions for
arithmetic data.  Its hidden objects are structured coefficient patterns;
its tones are harmonic probes built from prime logarithms; and its echoes are
complex-valued readings.  Across ten manuscripts, the project pairs recovery
theorems with impossibility results and asks what geometry is created by the
act of measurement itself.

## The arithmetic chord

The interactive laboratory uses the primes 2, 3, and 5.  A synthetic object
has 64 possible components,

```text
n = 2^a 3^b 5^c,       a,b,c in {0,1,2,3}.
```

Each prime carries a four-level local profile.  For a prime `p`, a compact
shape coordinate `y_p` between zero and one is converted to

```text
u_p = y_p / (1-y_p),
q_p(a) = u_p^a / (1 + u_p + u_p^2 + u_p^3).
```

The 64 coefficients are the products

```text
q_2(a) q_3(b) q_5(c).
```

This is what **shape** means in the lab.  It is not the physical shape of a
prime number, and the primes themselves do not move.  Shape is a compact way
to describe how probability or weight is distributed across the four allowed
exponents of each prime:

- `y_p < 1/2` favors low exponents;
- `y_p = 1/2` makes the four exponent levels equally weighted;
- `y_p > 1/2` favors high exponents.

For the lab's default source, the prime-2 profile is concentrated toward
exponent zero, the prime-3 profile is nearly even, and the prime-5 profile is
concentrated toward exponent three.  Moving a shape slider changes that hidden
coefficient landscape.

The instrument does not read the 64 components one by one.  At time `t` it
hears their combined harmonic response,

```text
H_y(t) = product over p in {2,3,5} of
         sum from a=0 to 3 q_p(a) exp(-i a t log p).
```

Because distinct primes have rationally independent logarithms, carefully
chosen times can make one prime direction speak clearly while the others are
nearly quiet.  The three-reading schedule in the lab is the explicit
phase-separated schedule certified in Arithmetic Observability V.

## When two shapes become confusable

Two shapes are exactly observationally equivalent for a chosen schedule when
all of their displayed readings agree.  With uncertainty, the more useful
question is whether their possible response sets overlap.

That overlap is called **confusability**.  It is intentionally not called a
general equivalence relation: with set-valued uncertainty, shape A may be
confusable with B and B with C without A being confusable with C.

In the lab, the cutoff is a pairwise reading-space distance.  If each of two
objects may carry independent adversarial error of radius `epsilon`, then
their response fibres can meet when their noiseless readings are within
`2 epsilon`.  That is why the control is labelled **Pair cutoff (2epsilon)**.

The heatmap varies the visible prime-2 and prime-3 shapes while allowing the
hidden prime-5 shape to compensate as well as it can.  Orange hatching marks
candidate cells that remain within the declared cutoff.  With only one
reading, broad valleys can survive: changes in one prime direction can partly
cancel changes in another.  Adding independent readings cuts across those
valleys.  In the declared positive geometric model, the three certified
readings are globally injective: exact equality of all three forces equality
of the compact shape.

The second plot is a **separation envelope**.  For each size of hidden-shape
change, it shows the smallest response change found on the displayed grid.
It is best read as an instrument-resolution curve:

- a low envelope means that some substantially different shapes still sound
  nearly alike;
- a rising envelope means that larger shape changes force larger observable
  changes;
- where the envelope lies below the pair cutoff, adversarial response fibres
  may overlap at that displayed resolution.

The curve is a sampled diagnostic, not a new theorem and not an energy
spectrum.  Its job is to make the theorem's geometry visible.

## A controlled bridge to physics

There is a clean way to place this arithmetic experiment inside a familiar
physical language without claiming that nature actually uses it.

Consider an engineered quantum toy system with basis states
`|a,b,c>`, where `a,b,c` range from zero to three, and define a Hamiltonian by

```text
E_(a,b,c) = hbar Omega (a log 2 + b log 3 + c log 5).
```

Prepare a factorized occupation profile with probabilities
`q_2(a)q_3(b)q_5(c)`.  After rescaling time, the survival amplitude

```text
<psi_y | exp(-i H t / hbar) | psi_y>
```

is exactly the harmonic reading used in the lab.  Under this interpretation,
the prime logarithms are engineered spectral spacings, the shape coordinates
control occupation bias, and the selected reading times are experimental
design choices.

This makes several real-world projections plausible as research directions:

- **quantum sensing:** infer a structured preparation from a few coherent
  return amplitudes;
- **spectroscopy:** distinguish mixtures whose component frequencies obey a
  multiplicative or tensor-product organization;
- **network diagnostics:** locate several hidden local biases from aggregated
  oscillatory telemetry;
- **chemical or population mixtures:** design a small set of probes that
  separates structured concentration profiles;
- **distributed sensing:** choose measurements that remain informative after
  nuisance variables are allowed to move.

If a future application calibrated `y_p` to temperature, field strength,
chemical potential, or another physical control, the separation envelope
could become a genuine resolution curve for that instrument: the smallest
observable signal change forced by a declared change in the hidden control.

But it would still not automatically be a list of particle energy states.
The energy levels in the toy Hamiltonian are chosen to reproduce the
arithmetic phases.  The Atlas supplies an exact mathematical embedding and a
language for recovery and obstruction; it does not supply evidence that an
elementary particle has prime-logarithmic energies.

## What the Atlas contributes

The most durable idea is broader than the prime example.  Observability is not
just a property of an object.  It is a relationship among:

1. the hidden model;
2. the feature or question we want answered;
3. the measurements we are allowed to take;
4. the nuisance changes or uncertainty we permit; and
5. the metric in which we judge error.

Change any one of those, and the boundary between distinguishable and
confusable can move.  The Atlas turns that boundary into mathematics: kernel
criteria, sharp reading counts, minimax constants, quotient metrics, compact
phase geometries, response tubes, zonoids, and certified finite examples.

That is the physical intuition worth carrying forward.  Measurement does not
merely reveal a pre-existing geometry.  Once information is incomplete and
nuisance is admitted, the measurement protocol helps determine which
directions are near, which are far, and which collapse into the same observable
shadow.

## Status and further reading

The AO Lab is an interactive illustration of a declared synthetic model.  Its
heatmap and separation envelope are finite-grid computations.  The exact
three-reading injectivity statement comes from the formal positive geometric
model in Arithmetic Observability V.  Other Atlas branches use different
models, norms, and nuisance classes and should not be inferred from this one
demonstration.

- [Arithmetic Observability Atlas](ARITHMETIC_OBSERVABILITY_ATLAS.md)
- [Arithmetic Observability V](ARITHMETIC_OBSERVABILITY_V.md)
- [Arithmetic Observability VI](ARITHMETIC_OBSERVABILITY_VI.md)
- [Corpus manifest](arithmetic_observability_corpus_manifest.json)
- [Interactive companion package](website/arithmetic-observability-companion/README.md)
