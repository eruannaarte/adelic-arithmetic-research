"""Assemble the concise reader-facing report from reviewed path chapters."""
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent

INTRO='''# Five mathematical research paths: supported developments

Research synthesis · 4 September 2026

The most useful development is a sharper account of **which question an experiment can answer, under which uncertainty, and at what cost**. All five paths now contribute a proved extension or a computational certificate beyond the earlier review. The new results are local to their declared models; they do not establish the project's broader philosophical interpretations.

Two findings deserve particular attention. Actual quadratic-field identities improve a discrete-query guarantee beyond an impossibility threshold for a larger coefficient envelope. Harmonic acquisition admits much shorter six-reading schedules with explicit global stability and clock bounds, while a separate five-reading example exposes the difference between local and global recovery. These make focused mathematical presentations with clear hypotheses and comparisons.

The applications also become more concrete. The pendulum guarantee now includes finite preparation error and a shared clock perturbation. Multiscale arithmetic sensing retains a positive noise allowance, although its coefficient-50 noise variance increases. A sharper semigroup remainder extends the finite-resolution certificate to a time interval five times as long at unchanged grid size.

The work starts from the [public research ledger](https://thegodnet.work/number-geometry/) and the local manuscripts and certificates assessed in the earlier review. Classical theorems are cited and their hypotheses checked in the proofs; the work claims new developments of this research package, without asserting historical priority. Exact arithmetic and outward interval computations decide numerical inequalities. Simulations supply additional controls. Noise tolerances in different chapters answer different questions and should not be compared without their source classes and norms.

The five chapters below give the results and limitations. The [proof appendix](PROOF_APPENDIX.md) and [claim-to-evidence index](CLAIM_EVIDENCE_INDEX.md) provide the full verification route.
'''

ENDING='''## What the results justify next

The quadratic query is the clearest bridge from an abstract uncertainty envelope to actual arithmetic. Its next question is whether more multiplicative relations produce a materially larger margin, or a sharp threshold, under the same measurement norm. The harmonic work is the strongest compact acquisition study: finding rigorous lower time bounds would complement its improved schedules.

For experimental design, the next useful step is increasing the certified preparation region and checking which tolerances an apparatus can achieve. For multiscale sensing, optimize bias and noise variance jointly; the present certificate establishes a tradeoff rather than universal statistical superiority. For resolution transfer, vary target position or add source modes while continuing to compare error with the weakest information direction.

All central numerical claims have a route back to their defining model, not only a saved matrix. The package records complete arithmetic-tail replays, nonlinear integration, phase reconstruction, continuum quadrature, precision controls, and independent consequence checkers. The [reproduction guide](README.md) distinguishes fast checks from expensive reconstructions. These verifications establish the stated mathematical guarantees; they do not supply empirical validation of a pendulum model or a physical noise distribution.
'''

paths=[('path1_preparation','PROOF.md'),('path2_harmonic','PROOFS.md'),('path3_noise','PROOF.md'),('path4_realizability','PROOF.md'),('path5_resolution','APPENDIX.md')]
out=[INTRO]
for i,(directory,proof) in enumerate(paths,1):
    chapter=(HERE/directory/'CHAPTER.md').read_text()
    chapter=re.sub(r'^#+ .*\n',f'## {i}. '+chapter.splitlines()[0].lstrip('# ').removeprefix(str(i)+'. ')+'\n',chapter,count=1)
    chapter=chapter.replace('same8900','same 8,900').replace('discriminants453,3165,381','discriminants 453, 3165, and 381')
    chapter=chapter.replace('to{0,1,2}','to {0,1,2}').replace('with a(4),a(9) each1 or3','with a(4),a(9) each 1 or 3')
    chapter=chapter.replace('at5,20,45','at 5,20,45').replace('least20','least 20').replace('are0,1,2','are 0,1,2')
    chapter=chapter.replace('above0.02003156','above 0.02003156').replace('radius**0.02**','radius **0.02**').replace('For any N,','For any integer N≥2,')
    if i==2:
        chapter=chapter.replace('The floor `c` means',"Here the factor norm is the Euclidean norm of the concatenated changes in all factor probabilities. The floor `c` means")
    out.append(chapter+f'\nProof and evidence: [complete derivation]({directory}/{proof}); [independent audit]({directory}/AUDIT.md).\n')
out.append(ENDING)
report='\n'.join(out)
# Absolute file links render in the shared desktop workspace.
report=re.sub(r'\]\((?!https?://)([^)]+)\)',lambda m:']('+str(HERE/m.group(1))+')',report)
(HERE/'REPORT.md').write_text(report)
words=len(re.findall(r'\S+',report))
intro_words=len(re.findall(r'\S+',INTRO))
print(f'Main report: {words} whitespace-separated words; opening: {intro_words}.')
if not(2000<=words<=3000 and intro_words<=400):raise SystemExit('word target failed')
