from django.http import HttpResponse
import platform
import os, os.path
import random
import sqlite3
#import string
import json
import cherrypy

DB_STRING = "my.db"

#class StringGenerator(object):
#    @cherrypy.expose
#    def index(self):
#        return file('')

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
       <head></head>
       <body>
        <div class="span3">
         <div class="widget widget-table action-table">
            <div class="widget-header"> <i class="fa fa-dashboard"></i>
              <h3>General Info</h3><i class="fa fa-minus"></i>
              <div id="refresh-os">
              </div>
            </div>
            <!-- /widget-header -->
            <div class="widget-content">
                <br>
              <div style="text-align:center;">
                <b>OS:</b> <span class="" id="get-osname"></span><br>
                <b>Uptime:</b> <span class="" id="get-uptime"></span> Hours<br>
                <b>Hostname:</b> <span class="" id="get-hostname"></span><br>
                <b>Kernel:</b> <span class="" id="get-kernel"></span><br>
                <b>CPU(s):</b> <span class="" id="get-cpucount"></span> x <span class="" id="get-cputype"></span>
                <br><br>
              </div>
            </div>
            <!-- /widget-content -->
          </div>
          <!-- /widget -->
        </div>
        </body>
        </html>"""

class StringGeneratorWebService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')#@login_required(login_url='/login/')
    def platform(self, name):
        with sqlite3.connect(DB_STRING) as c:
            c.getplatform = get_platform()
            c.hostname = getplatform['hostname']
            c.osname = getplatform['osname']
            c.kernel = getplatform['kernel']
            c.data = {}

        if name == 'hostname':
            try:
                c.data = hostname
            except Exception:
                c.data = None

        if name == 'osname':
            try:
                c.data = osname
            except Exception:
                c.data = None

        if name == 'kernel':
            try:
                c.data = kernel
            except Exception:
                c.data = None

        c.data = json.dumps(data)
        c.response = HttpResponse()
        #response['Content-Type'] = "text/javascript"
        c.response.write(data)
        return c.response

    def get_platform():
        with sqlite3.connect(DB_STRING) as c:
        #Get the OS name, hostname and kernel
            try:
                c.osname = " ".join(platform.linux_distribution())
                c.uname = platform.uname()

                if osname == '  ':
                    c.osname = uname[0]

                c.data = {'osname': osname, 'hostname': uname[1], 'kernel': uname[2]}

            except Exception, err:
                c.data = str(err)

            return c.data


def setup_database():
    """
    Create the `user_string` table in the database
    on server startup
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE user_string")

def cleanup_database():
    """
    Destroy the `user_string` table from the database
    on server shutdown.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    cherrypy.engine.subscribe('start', setup_database)
    cherrypy.engine.subscribe('stop', cleanup_database)

    webapp = StringGenerator()
    webapp.generator = StringGeneratorWebService()
    cherrypy.config.update({'server.socket_host': '192.168.241.128',})
    cherrypy.quickstart(webapp, '/', conf)
