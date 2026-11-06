const fs=require('fs'),R=__dirname+'/../';
const {createEngine}=require(R+'js/search.js');
const bank=JSON.parse(fs.readFileSync(R+'data/bank.json')),schema=JSON.parse(fs.readFileSync(R+'data/schema.json'));
const eng=createEngine({entries:bank.entries,schema});
JSON.parse(fs.readFileSync(R+'tests/heldout_blind2_questions.json')).forEach((c,i)=>{const o=eng.search(c.q,{limit:3});
 console.log((i+1)+'. ['+c.slug+'] '+c.q);if(!o.results.length)console.log('   NONE');
 o.results.forEach(r=>console.log('   '+r.id+' '+r.score.toFixed(2)+(r.nCrit?' CRIT':'')+' | '+r.entry.question.slice(0,95)))});
