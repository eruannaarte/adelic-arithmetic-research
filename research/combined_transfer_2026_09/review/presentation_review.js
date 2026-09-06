/* Mathematical semantic review; no DOM simulation or claim of browser QA. */
'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const C=require(path.join(root,'website/transfer-theorem-lab/core.js'));
const E=require(path.join(root,'website/transfer-theorem-lab/evidence.json'));
let toy=0,profiles=0,certified=0,boxes=0;
for(const incidence of ['single','shared','independent'])for(const query of ['integer','continuous'])for(let noise=0;noise<=100;noise++){
  const a=C.answers({incidence,query,noise});
  const expected=[];
  for(let x=0;x<=4;x++)if(incidence!=='shared'||Math.abs(200-100*x)<=2*noise)expected.push(x);
  assert.deepEqual(a.integers,expected);
  const lo=incidence==='shared'?Math.max(0,200-2*noise):0;
  const hi=incidence==='shared'?Math.min(400,200+2*noise):400;
  assert.equal(a.low,lo/100);assert.equal(a.high,hi/100);
  assert.equal(a.determined,query==='integer'?expected.length===1:lo===hi);
  toy++;
}
for(const design of ['multi','outer'])for(const degree of [6,8,10,11,12])for(const amplitude of [500,4000])for(let multiplier=0;multiplier<=200;multiplier++){
  const s=C.state({design,degree,amplitude,multiplier}),r=C.arithmetic(s,E);
  // Check conservative inheritance only. These booleans are not derived from
  // the floating plot. The endpoint research contracts carry the proof.
  const covers=(degree===12&&multiplier<=120)||(degree===11&&amplitude===500&&multiplier<=1);
  assert.equal(r.verified,covers);
  assert.ok(Number.isFinite(r.total)&&r.total>=0);
  if(covers){assert.ok(r.total<0.5);certified++;}
  assert.deepEqual(C.decode(C.encode(s)),s);profiles++;
}
for(const bank of ['sixKnown','sixJoint','sevenJoint'])for(const sensor of [0,100,101,160])for(const clock of [0,100,101,160])for(const potential of [0,100,101,160]){
  const r=C.spatial({bank,sensor,clock,potential},E),e=E.spatial[bank];
  assert.equal(r.within,sensor<=100&&(e.clock===0||clock<=100)&&(e.potential===0||potential<=100));
  if(e.clock===0)assert.equal(r.clock,0);
  if(e.potential===0)assert.equal(r.potential,0);
  boxes++;
}
assert.equal(E.paths.length,5);assert.equal(E.history.length,9);
assert.throws(()=>C.state({amplitude:501}));assert.throws(()=>C.state({degree:7}));
assert.throws(()=>C.state({noise:0.5}));assert.throws(()=>C.state({other:1}));
console.log(JSON.stringify({verified:true,exactElementaryCases:toy,arithmeticScenarioCases:profiles,
  conservativelyCertifiedArithmeticCases:certified,spatialBoundaryCases:boxes,
  originalResearchPaths:E.paths.length,researchPackages:E.history.length,
  scope:'Core semantics and conservative published-contract containment, not browser layout or a new interval certificate.'},null,2));
