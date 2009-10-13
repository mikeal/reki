import os, sys
from datetime import datetime

from couchquery import Database
from webenv import HtmlResponse
from webenv.rest import RestApplication
from webenv.applications.file_server import FileServerApplication
from mako.lookup import TemplateLookup
import markdown2

try:
    import json
except:
    import simplejson as json

this_directory = os.path.abspath(os.path.dirname(__file__))
static_dir = os.path.join(this_directory, 'static')
pages_design_doc = os.path.join(this_directory, 'pagesDesign')
template_dir = os.path.join(this_directory, 'templates')

lookup = TemplateLookup(directories=[template_dir], encoding_errors='ignore', input_encoding='utf-8', output_encoding='utf-8')

class MakoResponse(HtmlResponse):
    def __init__(self, name, **kwargs):
        template = lookup.get_template(name+'.mko')
        kwargs['json'] = json
        self.body = template.render_unicode(**kwargs).encode('utf-8', 'replace')
        self.headers = []

class FeedResponse(MakoResponse):
    content_type = 'application/rss+xml'

class RekiApplication(RestApplication):
    def __init__(self, db):
        super(RekiApplication, self).__init__()
        self.db = db
        self.add_resource('static', FileServerApplication(static_dir))
        
    def get_page(self, args):
        result = self.db.views.pages.byName(key=args)
        if len(result) is 0:
            page = {"pagename":args}
            info = self.db.create(page)
            page['_id'] = info['id']
            page['_rev'] = info['rev']
        else:
            page = result[0]
        return page
        
    def GET(self, request, *args):
        page = self.get_page(args)
        pages_index = self.db.views.pages.idsByName(startkey=args, endkey=list(args)+[{}])
        return MakoResponse('page', page=page, pages_index=pages_index)
    
def cli():
    from wsgiref.simple_server import make_server
    db = Database(sys.argv[-1])
    db.sync_design_doc('pages', pages_design_doc)
    application = RekiApplication(db)
    httpd = make_server('', 8888, application)
    print "Serving on http://localhost:8888/"
    httpd.serve_forever()
    
    