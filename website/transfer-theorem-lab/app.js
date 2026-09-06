(function(){
  'use strict';
  const C=window.TransferCore,E=window.TransferEvidence,$=id=>document.getElementById(id);
  let s=C.state({});
  const NS='http://www.w3.org/2000/svg';
  function svg(tag,attrs,text){const el=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs||{}))el.setAttribute(k,String(v));if(text!==undefined)el.textContent=text;return el;}
  function element(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
  function scientific(x){return x===0?'0':x.toExponential(2).replace('e-',' × 10⁻').replace('e+',' × 10^');}
  function number(x){return x<.00001?x.toExponential(3):x.toFixed(x<1?6:3);}
  function percentUpper(x){return (Math.ceil(x*100*1e6)/1e6).toFixed(6);}
  function resetSVG(el,title){el.replaceChildren(svg('title',{id:el.getAttribute('aria-labelledby')||el.id+'-title'},title));}
  function message(text){$('message').textContent=text;}
  function syncControls(){
    for(const key of ['noise','bank','sensor','clock','potential','design','degree','amplitude','multiplier'])$(key).value=String(s[key]);
    for(const name of ['incidence','query'])for(const input of document.querySelectorAll('input[name="'+name+'"]'))input.checked=input.value===s[name];
  }
  function renderAnswers(){
    const a=C.answers(s),plot=$('answer-plot'),x=v=>50+125*v;
    $('noise-out').textContent=(s.noise/100).toFixed(2);
    resetSVG(plot,'Feasible answers: '+(s.query==='integer'?a.integers.join(', '):'from '+a.low+' to '+a.high));
    plot.append(svg('line',{x1:50,y1:85,x2:550,y2:85,stroke:'#a5b4a5','stroke-width':2}));
    plot.append(svg('rect',{x:x(a.low),y:70,width:Math.max(1,x(a.high)-x(a.low)),height:30,fill:'#dfeee4'}));
    for(let i=0;i<=4;i++){
      const fits=a.integers.includes(i);
      plot.append(svg('circle',{cx:x(i),cy:85,r:s.query==='integer'?12:4,fill:fits?'#1b7260':'#f7f5ed',stroke:fits?'#1b7260':'#a5b4a5','stroke-width':2}));
      plot.append(svg('text',{x:x(i),y:125,'text-anchor':'middle'},String(i)));
    }
    plot.append(svg('text',{x:50,y:35},s.query==='integer'?'Filled dots are admissible integer answers':'Shaded interval contains every admissible value'));
    $('answer-status').replaceChildren(element('span',s.query==='integer'?(a.determined?'One answer remains: x = '+a.integers[0]:a.integers.length+' integer answers remain: '+a.integers.join(', ')):'x lies in ['+a.low.toFixed(2)+', '+a.high.toFixed(2)+']'));
    $('answer-status').append(element('small',s.query==='continuous'?'Certified interval diameter: '+a.diameter.toFixed(2)+'. The interval describes the uncertainty in this observation.':a.determined?'This integer question is determined for the displayed data and assumptions.':'The data permit these different answers. A decoder should retain the set.'));
    $('answer-explanation').textContent=s.incidence==='shared'?'Subtracting the readings removes the common offset. The two sensor errors remain: |x − 2| ≤ 2ε.':s.incidence==='single'?'With one reading, the unrestricted unknown offset can explain every source value.':'Independent offsets can explain every source value. Removing a common offset would assume the wrong model.';
  }
  function renderSpatial(){
    const r=C.spatial(s,E),e=r.evidence,plot=$('spatial-plot'),x=v=>35+(v-482)*530/36;
    $('clock').disabled=e.clock===0;$('potential').disabled=e.potential===0;
    for(const k of ['sensor','clock','potential'])$(k+'-out').textContent=scientific(r[k]);
    $('spatial-badge').textContent=r.within?'WITHIN VERIFIED CONTRACT':'OUTSIDE THIS CERTIFICATE';$('spatial-badge').className='pill'+(r.within?'':' outside');
    resetSVG(plot,e.rows.length+' selected readout rows: '+e.rows.join(', ')+'. Targets range from 490 to 510.');
    plot.append(svg('rect',{x:x(490),y:28,width:x(510)-x(490),height:70,fill:'#edf0e5'}));
    for(let j=482;j<=518;j++)plot.append(svg('line',{x1:x(j),x2:x(j),y1:55,y2:88,stroke:j>=490&&j<=510?'#b1bda9':'#e1e4db','stroke-width':1}));
    for(const j of e.rows){plot.append(svg('line',{x1:x(j),x2:x(j),y1:35,y2:93,stroke:'#1b7260','stroke-width':3}));plot.append(svg('text',{x:x(j),y:113,'text-anchor':'middle','font-size':11},j));}
    plot.append(svg('text',{x:35,y:18},'Green lines: selected spatial averages'));
    plot.append(svg('text',{x:35,y:141},'Shaded region: 21 possible target rows'));
    $('spatial-status').textContent=r.within?'Every admitted target is identifiable; source error < '+percentUpper(e.error)+'%.':'At least one radius exceeds this saved contract. No conclusion of impossibility follows.';
    const values=[['Source error target','< 0.1%'],['Certified full-box bound','< '+percentUpper(e.error)+'%'],['Readout count',String(e.rows.length)],['Time interval','[1, 2], nominal and actual'],['Readout rows',e.rows.join(', ')]];
    $('spatial-numbers').replaceChildren(...values.map(([k,v])=>{const d=element('div');d.append(element('dt',k),element('dd',v));return d;}));
  }
  const colors={tail:'#293f35',sensor:'#55957a',mismatch:'#a5bea1',drift:'#b56c3d',clock:'#d9ab60',computation:'#83877e'};
  const names={tail:'Infinite tail',sensor:'Sensor',mismatch:'Mismatch',drift:'Drift family',clock:'Affine clock',computation:'Centering + residual'};
  function renderArithmetic(){
    const r=C.arithmetic(s,E),plot=$('budget-plot');
    $('multiplier-out').textContent=s.multiplier+' ×';
    $('arithmetic-badge').textContent=r.verified?'WITHIN VERIFIED CONTRACT':'SUFFICIENT-BOUND EXPLORER';$('arithmetic-badge').className='pill'+(r.verified?'':' outside');
    $('arithmetic-total').textContent='≈ '+number(r.total);
    const max=Math.max(.6,r.total*1.08),scale=540/max,x=v=>30+v*scale;
    resetSVG(plot,'Estimated error '+r.total+'. Integer rounding threshold one half.');
    plot.append(svg('rect',{x:30,y:30,width:540,height:30,fill:'#eeeee3'}));
    let offset=0;
    for(const [key,value] of Object.entries(r.components)){plot.append(svg('rect',{x:x(offset),y:30,width:value*scale,height:30,fill:colors[key]}));offset+=value;}
    plot.append(svg('line',{x1:x(.5),x2:x(.5),y1:16,y2:72,stroke:'#983f3b','stroke-width':2}));
    plot.append(svg('text',{x:x(.5),y:91,'text-anchor':x(.5)>490?'end':'middle'},'½ · strict rounding threshold'));
    $('budget-legend').replaceChildren(...Object.entries(r.components).map(([key,value])=>{const label=element('span',names[key]+' '+number(value));label.style.setProperty('--swatch',colors[key]);return label;}));
    $('arithmetic-status').replaceChildren(element('span',r.verified?'All 49 unknown integers have a strict rounding guarantee.':r.failure));
    const cap=s.degree===11?r.record.certifiedMaximumB500:r.record.certifiedMaximum;
    $('arithmetic-status').append(element('small',r.verified?'Saved full-contract error < '+(Math.ceil(cap*1e9)/1e9).toFixed(9)+'. Requires the declared model and a verified normal residual ≤ 10⁻³⁰.':'A failed sufficient gate does not prove that no decoder could succeed. Displayed values are rounded estimates, not fresh interval certificates.'));
  }
  function render(){syncControls();renderAnswers();renderSpatial();renderArithmetic();}
  function loadState(input){s=C.state(input);render();}
  for(const key of ['noise','sensor','clock','potential','multiplier'])$(key).addEventListener('input',()=>{s=C.state({...s,[key]:Number($(key).value)});render();});
  for(const key of ['bank','design','degree','amplitude'])$(key).addEventListener('change',()=>{s=C.state({...s,[key]:['degree','amplitude'].includes(key)?Number($(key).value):$(key).value});render();});
  for(const key of ['incidence','query'])for(const input of document.querySelectorAll('input[name="'+key+'"]'))input.addEventListener('change',()=>{s=C.state({...s,[key]:input.value});render();});
  $('spatial-reset').addEventListener('click',()=>loadState({...s,sensor:100,clock:100,potential:100}));
  $('arithmetic-reset').addEventListener('click',()=>loadState({...s,degree:12,amplitude:4000,multiplier:120}));
  $('reset').addEventListener('click',()=>{loadState({});message('All controls reset.');});
  $('share').addEventListener('click',async()=>{
    const url=location.href.split('#')[0]+C.encode(s);
    $('share-text').value=url;$('share-fallback').hidden=false;
    try{if(!navigator.clipboard)throw Error('Clipboard unavailable');await navigator.clipboard.writeText(url);message('Scenario link copied.');}
    catch{const d=$('share-fallback');d.hidden=false;d.open=true;$('share-text').value=url;$('share-text').focus();$('share-text').select();message('Copy the selected scenario link below.');d.scrollIntoView({block:'center'});}
  });
  $('download').addEventListener('click',()=>{const json=JSON.stringify(s,null,2)+'\n';$('export-text').value=json;$('export-fallback').hidden=false;$('export-fallback').open=true;const blob=new Blob([json],{type:'application/json'});const url=URL.createObjectURL(blob);const a=element('a');a.href=url;a.download='transfer-theorem-scenario.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);message('Download requested. You can also copy the scenario JSON below.');});
  $('import').addEventListener('change',async()=>{const f=$('import').files[0];if(!f)return;try{if(f.size>4096)throw Error('Scenario file is too large.');loadState(JSON.parse(await f.text()));message('Scenario loaded.');}catch(e){message('Scenario was not loaded: '+e.message);}finally{$('import').value='';}});
  $('print').addEventListener('click',()=>window.print());
  window.addEventListener('hashchange',()=>{try{if(location.hash.startsWith('#scenario=')){loadState(C.decode(location.hash));message('Shared scenario loaded.');}}catch(e){message(e.message);}});
  for(const link of document.querySelectorAll('[data-evidence]'))link.href=E.proofLinks[link.dataset.evidence];
  E.paths.forEach((p,i)=>{const row=element('article',undefined,'path'),head=element('div'),note=element('div',undefined,'connection');head.append(element('h3',p.title),element('p',p.subtitle),element('p',p.finding));const a=element('a','Explore the evidence ↗');a.href=p.url;note.append(element('span','CONTRIBUTION TO THE TRANSFER','eyebrow'),element('p',p.connection),a);row.append(element('span',String(i+1).padStart(2,'0'),'path-index'),head,note);$('path-list').append(row);});
  for(const p of E.history){const li=element('li'),a=element('a',p.title);a.href=p.url;li.append(a,document.createTextNode(' — '+p.description));$('history').append(li);}
  for(const p of E.links){const a=element('a',p.title);a.href=p.url;a.append(element('span',p.description));$('evidence-links').append(a);}
  try{if(location.hash.startsWith('#scenario='))s=C.decode(location.hash);}catch(e){message('Could not load shared scenario: '+e.message);}
  render();
})();
