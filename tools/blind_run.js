const fs=require('fs');const root='/Users/cuki2910/Desktop/sql_helper/';
const {createEngine}=require(root+'js/search.js');
const bank=JSON.parse(fs.readFileSync(root+'data/bank.json'));const schema=JSON.parse(fs.readFileSync(root+'data/schema.json'));
const eng=createEngine({entries:bank.entries,schema});
const qs=JSON.parse(fs.readFileSync(root+'tests/heldout_blind_questions.json'));
qs.forEach((q,i)=>{const o=eng.search(q,{limit:3});console.log((i+1)+'. '+q);if(!o.results.length)console.log('   NONE');o.results.forEach(r=>console.log('   '+r.id+' | '+r.entry.question.slice(0,110)))});
