'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const C=require('./core.js'),E=JSON.parse(fs.readFileSync(path.join(__dirname,'evidence.json'),'utf8'));
test('zero-error shared nuisance identifies exact source',()=>{
  assert.deepEqual(C.answers({noise:0}).integers,[2]);
  assert.equal(C.answers({noise:0,query:'continuous'}).diameter,0);
});
test('closed interval retains boundary integer alternatives',()=>{
  assert.deepEqual(C.answers({noise:49}).integers,[2]);
  assert.deepEqual(C.answers({noise:50}).integers,[1,2,3]);
  assert.deepEqual(C.answers({noise:100}).integers,[0,1,2,3,4]);
});
test('independent unbounded nuisance cannot be canceled',()=>{
  for(const incidence of ['single','independent'])for(const noise of [0,18,100]){
    const a=C.answers({incidence,noise});assert.equal(a.integers.length,5);assert.equal(a.diameter,4);
  }
});
test('every toy integer has an exact admissible shared-nuisance witness iff retained',()=>{
  for(let noise=0;noise<=100;noise++)for(let x=0;x<=4;x++){
    // hundredths: e2=(2-x)/2, e1=-e2, u=5-x-e1.
    const twiceE2=(2-x)*100;
    assert.equal(Math.abs(twiceE2)<=2*noise,C.answers({noise}).integers.includes(x));
  }
});
test('continuous diameter is reported without rounding to a discrete answer',()=>{
  const a=C.answers({noise:18,query:'continuous'});assert.equal(a.low,1.64);assert.equal(a.high,2.36);assert.equal(a.diameter,.72);assert.equal(a.determined,false);
});
test('all controls survive share-link round trip',()=>{
  const s=C.state({incidence:'independent',query:'continuous',noise:75,bank:'sevenJoint',sensor:62,clock:133,potential:23,design:'multi',degree:11,amplitude:500,multiplier:1});assert.deepEqual(C.decode(C.encode(s)),s);
});
test('scenario parser rejects malformed and unknown state',()=>{
  for(const x of [null,[],{v:2},{degree:9},{degree:'11'},{noise:NaN},{noise:1.2},{noise:101},{multiplier:201},{bank:'four'},{amplitude:4001},{url:'javascript:alert(1)'},JSON.parse('{"__proto__":{}}')])assert.throws(()=>C.state(x));
  for(const x of ['#scenario={','#scenario='+encodeURIComponent('{"v":99}'),'#other=1','#scenario='+'a'.repeat(1700)])assert.throws(()=>C.decode(x));
});
test('spatial inherited box includes boundaries and excludes exceeded coordinates',()=>{
  for(const bank of ['sixJoint','sevenJoint']){
    assert.equal(C.spatial({bank},E).within,true);
    for(const k of ['sensor','clock','potential'])assert.equal(C.spatial({bank,[k]:101},E).within,false);
  }
});
test('known-time bank keeps physical uncertainty exactly zero',()=>{
  const r=C.spatial({bank:'sixKnown',clock:160,potential:160},E);assert.equal(r.clock,0);assert.equal(r.potential,0);assert.equal(r.within,true);
});
test('degree12 saved contract is inherited only within h120',()=>{
  for(const design of ['multi','outer'])for(const amplitude of [500,4000]){
    for(const multiplier of [0,1,60,120])assert.equal(C.arithmetic({design,amplitude,multiplier},E).verified,true);
    assert.equal(C.arithmetic({design,amplitude,multiplier:121},E).verified,false);
  }
});
test('degree11 lower amplitude/baseclock consequence stays distinct',()=>{
  for(const design of ['multi','outer']){
    assert.equal(C.arithmetic({design,degree:11,amplitude:500,multiplier:1},E).verified,true);
    assert.equal(C.arithmetic({design,degree:11,amplitude:500,multiplier:2},E).verified,false);
    assert.equal(C.arithmetic({design,degree:11,amplitude:4000,multiplier:1},E).verified,false);
  }
});
test('UI budget agrees with independent exact h120 component receipt',()=>{
  const expected={multi:.4471533665,outer:.4961987078};
  for(const design of ['multi','outer'])assert.ok(Math.abs(C.arithmetic({design},E).total-expected[design])<1e-9);
});
test('verified degree11 positive and failed fixed-amplitude budgets agree',()=>{
  for(const design of ['multi','outer']){
    assert.ok(C.arithmetic({design,degree:11,amplitude:4000,multiplier:1},E).total>1);
    assert.ok(C.arithmetic({design,degree:11,amplitude:500,multiplier:1},E).total<.5);
  }
});
test('all displayed budgets are finite positive and monotone in clock',()=>{
  for(const design of ['multi','outer'])for(const degree of [6,8,10,11,12])for(const amplitude of [500,4000]){
    let prev=0;
    for(let multiplier=0;multiplier<=200;multiplier++){
      const r=C.arithmetic({design,degree,amplitude,multiplier},E);assert.ok(Number.isFinite(r.total)&&r.total>=prev);prev=r.total;
      if(r.verified)assert.ok(r.total<.5);
    }
  }
});
test('no older tested degree is advertised as verified',()=>{
  for(const degree of [6,8,10])for(const amplitude of [500,4000])assert.equal(C.arithmetic({degree,amplitude,multiplier:0},E).verified,false);
});
test('evidence input hashes bind actual research artifacts',()=>{
  const crypto=require('node:crypto'),root=path.resolve(__dirname,'../..');
  for(const [name,expected] of Object.entries(E.inputSha256))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,name))).digest('hex'),expected,name);
});
test('proof and path links are pinned to this publication tag',()=>{
  for(const url of [...Object.values(E.proofLinks),...E.paths.map(p=>p.url),...E.history.map(p=>p.url)])assert.ok(url.includes('/blob/'+E.tag+'/'));
});
test('JS evidence and JSON evidence have the same content',()=>{
  const vm=require('node:vm'),context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'evidence.js'),'utf8'),context);assert.equal(JSON.stringify(context.window.TransferEvidence),JSON.stringify(E));
});
test('standalone assets require no remote runtime scripts or styles',()=>{
  const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  assert.equal(/<(?:script|link)[^>]+(?:src|href)=["']https?:/i.test(html),false);
  for(const file of ['core.js','app.js','transfer.css'])assert.equal(/\bfetch\s*\(|XMLHttpRequest|@import|eval\s*\(/.test(fs.readFileSync(path.join(__dirname,file),'utf8')),false);
});
