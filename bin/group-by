#!/usr/bin/env node
var fs = require('fs');
var r = {};
JSON.parse(fs.readFileSync('/dev/stdin').toString()).forEach(function(itm){
  r[itm[process.argv[2]]] = itm;
  delete itm[process.argv[2]];
});
process.stdout.write(JSON.stringify(r));
