/* Apache-2.0. Exact toy model and bounded, reproducible presentation state. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.TransferCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const DEFAULT = Object.freeze({v:1, noise:18, incidence:'shared', query:'integer', bank:'sixJoint', sensor:100, clock:100, potential:100, design:'outer', degree:12, amplitude:4000, multiplier:120});
  const choices = {incidence:['single','shared','independent'], query:['integer','continuous'], bank:['sixKnown','sixJoint','sevenJoint'], design:['multi','outer']};
  const ranges = {noise:[0,100], sensor:[0,160], clock:[0,160], potential:[0,160], multiplier:[0,200]};
  function state(input) {
    if (!input || typeof input !== 'object' || Array.isArray(input)) throw Error('A scenario must be an object.');
    for (const k of Object.keys(input)) if (!Object.hasOwn(DEFAULT,k)) throw Error('Unknown scenario field: '+k);
    if (input.v !== undefined && input.v !== 1) throw Error('Unsupported scenario version.');
    const result = {...DEFAULT, ...input};
    for (const [key, values] of Object.entries(choices)) if (!values.includes(result[key])) throw Error('Invalid '+key+'.');
    for (const [key,[lo,hi]] of Object.entries(ranges)) if (!Number.isInteger(result[key]) || result[key]<lo || result[key]>hi) throw Error('Invalid '+key+'.');
    if (![6,8,10,11,12].includes(result.degree)) throw Error('Invalid degree.');
    if (![500,4000].includes(result.amplitude)) throw Error('Invalid amplitude.');
    return result;
  }
  function encode(input) { return '#scenario='+encodeURIComponent(JSON.stringify(state(input))); }
  function decode(hash) {
    if (!hash) return state({});
    if (!hash.startsWith('#scenario=') || hash.length>1600) throw Error('Invalid scenario link.');
    return state(JSON.parse(decodeURIComponent(hash.slice(10))));
  }
  function answers(input) {
    const s=state(input), radius=s.incidence==='shared' ? 2*s.noise : 200;
    const low=s.incidence==='shared' ? Math.max(0,200-radius) : 0;
    const high=s.incidence==='shared' ? Math.min(400,200+radius) : 400;
    const integers=[0,1,2,3,4].filter(x=>100*x>=low && 100*x<=high);
    return {low:low/100,high:high/100,integers,diameter:(high-low)/100,
      determined:s.query==='integer' ? integers.length===1 : high===low};
  }
  // Certificate inheritance: reducing any radius preserves the published contract.
  // No new interval matrix computation is performed by this browser.
  function spatial(input, evidence) {
    const s=state(input), e=evidence.spatial[s.bank];
    const within=s.sensor<=100 && (e.clock===0 || s.clock<=100) && (e.potential===0 || s.potential<=100);
    return {within, evidence:e, sensor:e.sensor*s.sensor/100, clock:e.clock*s.clock/100, potential:e.potential*s.potential/100};
  }
  function arithmetic(input,evidence) {
    const s=state(input), e=evidence.arithmetic[s.design][String(s.degree)];
    // Components are rounded display estimates. Their floating sum cannot
    // establish a new certificate; the status uses only saved contracts.
    const c=e.components;
    const clock=e.clockLinear*s.multiplier + e.clockQuadratic*s.multiplier*s.multiplier;
    const omega=3*(1+s.multiplier*1e-14);
    const polynomial=terms=>terms.reduce((sum,term)=>sum+term[1]*omega**term[0],0);
    const drift=s.amplitude*e.inverseGain*Math.max(polynomial(e.odd),polynomial(e.even));
    const components={tail:c.tail, sensor:c.sensor, mismatch:c.mismatch, drift, clock, computation:c.computation};
    const total=Object.values(components).reduce((a,b)=>a+b,0);
    const verified=(s.degree===12 && s.multiplier<=120) || (s.degree===11 && s.amplitude===500 && s.multiplier<=1);
    return {components,total,verified,record:e, failure:total>=.5 ? 'The displayed estimate is at or above ½; no certificate is shown for this scenario.' : 'The displayed estimate is below ½; this scenario is outside the saved contracts shown here.'};
  }
  return Object.freeze({DEFAULT,state,encode,decode,answers,spatial,arithmetic});
});
