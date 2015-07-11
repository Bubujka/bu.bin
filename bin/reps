#!/usr/bin/env node
var exec = require('child_process').exec;
var request = require('request');
var async = require('async');
var printf = require('printf');
var fs = require('fs');



function gh_page(id, cb){
  request.get(
    'https://api.github.com/users/bubujka/repos?page='+id,
    {
      headers: {
        'User-Agent': '@bubujka reps list fetcher',
        'Authorization': 'token '+process.env.GITHUB_TOKEN
      }
    },
    function(err,res,body){
      if(err){
        return cb(err);
      }
      cb(null, JSON.parse(body));
    });
}

function gh_page_starred(id, cb){
  request.get(
    'https://api.github.com/users/bubujka/starred?page='+id,
    {
      headers: {
        'User-Agent': '@bubujka reps list fetcher',
        'Authorization': 'token '+process.env.GITHUB_TOKEN
      }
    },
    function(err,res,body){
      if(err){
        return cb(err);
      }
      cb(null, JSON.parse(body));
    });
}

async.parallel({
  bb: function(cb) {
    exec('bb list | grep git', function(err,reps) {
      if(err){
        return cb(err);
      }

      var bbreps = reps.split('\n').filter(function(i){
        return i.length;
      })
      .map(function(i) {
        var name = i.replace(/.*] /,'');
        return printf("bb:%-50s%s", name, 'http://bitbucket.org/'+name+'/src');
      });
      cb(null, bbreps);
    });
  },
  gh: function(cb) {
    var page = 1;
    var reps = [];
    var process_page = function(err, rawreps) {
      if(err){
        return cb(err);
      }
      if(rawreps.length){
        rawreps.forEach(function(i){
          reps.push(printf("gh:%-50s%s", i.full_name, i.html_url));
        });
        page++;
        gh_page(page, process_page);
      }else{
        cb(null, reps);
      }
    };
    gh_page(page, process_page);
  },

  gh_starred: function(cb) {
    var page = 1;
    var reps = [];
    var process_page = function(err, rawreps) {
      if(err){
        return cb(err);
      }
      if(rawreps.length){
        rawreps.forEach(function(i){
          reps.push(printf("★ %-50s%s", i.full_name, i.html_url));
        });
        page++;
        gh_page_starred(page, process_page);
      }else{
        cb(null, reps);
      }
    };
    gh_page_starred(page, process_page);
  }
}, function(err, data){
  if(err){
    console.log(err);
    process.exit(0);
  }
  var t = "";
  t = t + data.gh_starred.join('\n');
  t = t + '\n';
  t = t + data.gh.join('\n');
  t = t + '\n';
  t = t + data.bb.join('\n');
  fs.writeFileSync('/home/bubujka/.reps', t);
});
