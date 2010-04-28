var couchapp = require('couchapp'),
    path = require('path');

var ddoc = {_id:"_design/app", shows:{}, lists:{}, views:{index:{},byUser:{}},
            modules:{}, templates:{}}

ddoc.rewrites = [
  { from: "/:page", to:"_list/page/index", method: "GET", 
    query: {startkey:[":page"], endkey:[":page", null]} },
]

ddoc.views.index.map = function (doc) {
  if (doc.pageid) { emit(doc.pageid, 1) }
}

ddoc.lists.page = function (head, req) {
  start({"code": 200, "headers": {"content-type":"text/html"}})
  var row;
  var mustache = require('modules/mustache').Mustache;
  var v = {pagedoc:getRow(), pageid:req.query.startkey, pagetitle:req.query.startkey.join('/')};
  if (!v.pagedoc) { v.newPage = true } else { v.newPage = false}
  v.index = [v.pagedoc];
  while(row = getRow()) {
    v.index.push(row.value);
  }
  var p = mustache.to_html(this.templates['page.mustache'], v);
  send(p);
}

couchapp.loadModules(ddoc.modules, path.join(__dirname, 'modules'));
couchapp.loadFiles(ddoc.templates, path.join(__dirname, 'templates'));
couchapp.loadAttachments(ddoc, path.join(__dirname, 'static'));
exports.app = ddoc;