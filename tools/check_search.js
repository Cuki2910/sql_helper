'use strict';
const assert = require('assert/strict');
const { norm, terms, constraints, createEngine } = require('../js/search.js');

const phrases = ['price greater than all costs', 'price higher than any costs', 'cost no less than three',
  'orders in the first quarter', 'employees handled four orders', 'products ordered together'];
for (const phrase of phrases) assert.equal(norm(norm(phrase)), norm(phrase), phrase);
for (const [phrase, op] of [['at least 5', '>='], ['5 or more', '>='], ['five or more', '>='], ['no fewer than 5', '>='], ['5 or greater', '>='], ['a minimum of 5', '>='], ['5+', '>='],
  ['at most 5', '<='], ['no more than 5', '<='], ['not exceeding 5', '<='], ['5 or lower', '<='], ['a maximum of 5', '<='], ['more than 5', '>'], ['exceeds 5', '>'], ['fewer than 5', '<'], ['a max of 5', '<='], ['max 5', '<='], ['under or equal to 5', '<='], ['5 maximum', '<='], ['at the most 5', '<='], ['lte 5', '<='], ['min 5', '>='], ['over or equal to 5', '>='], ['gte 5', '>=']])
  assert.deepEqual([...constraints('categories with ' + phrase + ' products').cmp], [op], phrase);
assert.equal(constraints('the minimum price').cmp.size, 0);
for (const adjective of ['greater', 'higher', 'larger', 'more']) {
  assert.equal(constraints('price ' + adjective + ' than all costs').gtAll, true);
  assert.equal(constraints('price ' + adjective + ' than some costs').gtAny, true);
  assert.equal(constraints('price ' + adjective + ' than at least one cost').gtAny, true);
}
assert.equal(constraints('For every supplier count purchase records').every, false);
assert.equal(constraints('Find suppliers providing every required product').every, true);
assert.equal(constraints('For every supplier check every required product').every, true);
assert.equal(constraints('Return all the Product Code and Product Name values.').every, false);
assert.equal(constraints('Include every employee tied for the highest order count.').every, false);
assert.equal(constraints('Return every supplier providing every required product.').every, true);
assert.equal(constraints('Customers whose orders include all the Beverages products').every, true);
assert.equal(constraints('Exclude products whose Standard Cost is zero or NULL.').neg, false);
assert.equal(constraints('Employees who never processed an order. Exclude NULL cities.').neg, true);
assert.equal(constraints('Exclude customers whose orders contain products with NULL costs.').neg, true);
assert.deepEqual(terms('TotalOrderValue ShippingRatio'), terms('Total Order Value Shipping Ratio'));
assert(constraints('purchase records in the first quarter').months.has('q1'));
assert(constraints('purchase records in the second quarter').months.has('q2'));
assert(!constraints('purchase records without a date limit').months.size);

const entries = [
  { id: 'SQL', kind: 'sql', question: 'List hardware serial numbers', answer: 'SELECT 1;', tags: ['hardware','serial'], tables: [] },
  { id: 'THEORY', kind: 'theory', question: 'Why should hardware serial numbers be unique?', answer: 'Hardware serial numbers identify items.', tags: ['hardware','serial'], tables: [] }
];
const engine = createEngine({ entries });
assert.equal(engine.search('List hardware serial numbers').results[0].id, 'SQL');
assert.equal(engine.search('Why should hardware serial numbers be unique?').results[0].id, 'THEORY');
const columns = createEngine({ entries: [
  { id: 'COLUMNS', kind: 'sql', question: 'List catalogue products.', answer: 'SELECT 1;', columns: ['products.Standard Cost'] }
] });
assert.equal(columns.search('Standard Cost').results[0].id, 'COLUMNS');
assert.equal(constraints('Report every employee with order counts').every, false);
assert.equal(constraints('Identify every supplier providing every required product').every, true);
assert.equal(constraints('Employees with zero orders').neg, constraints('Employees with no orders').neg);
assert(terms('Tally orders').includes('count'));
assert.equal(norm('bought products'), 'purchased products');
assert.equal(norm('bought together'), 'ordered together');
assert.deepEqual([...constraints('products bought during 2006').status], ['purchased']);
const aliasEntry = { id: 'ALIASED', kind: 'sql', question: 'List hardware serial numbers',
  answer: 'SELECT 1;', aliases: ['Find catalogue identifiers in storage'] };
const aliasEngine = createEngine({ entries: [aliasEntry] });
const repeatedEngine = createEngine({ entries: [{ ...aliasEntry, aliases: Array(20).fill(aliasEntry.aliases[0]) }] });
const aliasMatch = aliasEngine.search('Find catalogue identifiers in storage').results[0];
assert.equal(aliasMatch.id, aliasEntry.id);
assert.equal(aliasMatch.exact, false);
assert.equal(aliasMatch.score, repeatedEngine.search('Find catalogue identifiers in storage').results[0].score);
const contradictory = createEngine({ entries: [{ id: 'NEGATED', kind: 'sql',
  question: 'Products that were never ordered', answer: 'SELECT 1;', aliases: ['Products that were ordered'] }] });
assert(contradictory.search('Products that were ordered').results.every((match) => !match.exact && match.nCrit > 0));
console.log('Synthetic normalization, quantifier scope, quarter and query-kind checks: PASS');
