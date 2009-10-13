function (doc) {
  if (doc.pagename && doc.body_rendered) {
    emit(doc.pagename, doc._id);
  }
}