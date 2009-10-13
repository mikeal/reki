function (doc) {
  if (doc.pagename) {
    emit(doc.pagename, doc);
  }
}