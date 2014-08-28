import os, os.path
import random
import sqlite3
import string
import json
import cherrypy

DB_STRING = "my.db"

#class StringGenerator(object):
#    @cherrypy.expose
#    def index(self):
#        return file('')

#class StringGeneratorWebService(object):
#    exposed = True


class StringGenerator(object):
    @cherrypy.tools.accept(media='text/plain')
    def getcpus(request, name):
        with sqlite3.connect(DB_STRING) as data:
    	    cpus = get_cpus()
    	    cputype = cpus['type']
    	    cpucount = cpus['cpus']
    	    data = {}

        if name == 'type':
            try:
                data = cputype
            except Exception:
                data = None

        if name == 'count':
            try:
                data = cpucount
            except Exception:
                data = None

        data = json.dumps(data)
        response = HttpResponse()
        #response['Content-Type'] = "text/javascript"
        response.write(data)
        return response


def get_cpus():
    """
    Get the number of CPUs and model/type
    """
    try:
        pipe = os.popen("cat /proc/cpuinfo |" + "grep 'model name'")
        data = pipe.read().strip().split(':')[-1]
        pipe.close()

        if not data:
            pipe = os.popen("cat /proc/cpuinfo |" + "grep 'Processor'")
            data = pipe.read().strip().split(':')[-1]
            pipe.close()

        cpus = multiprocessing.cpu_count()

        data = {'cpus': cpus, 'type': data}

    except Exception, err:
        data = str(err)

    return data



def get_cpu_usage():
    """
    Get the CPU usage and running processes
    """
    try:
        pipe = os.popen("ps aux --sort -%cpu,-rss")
        data = pipe.read().strip().split('\n')
        pipe.close()

        usage = [i.split(None, 10) for i in data]
        del usage[0]

        total_usage = []

        for element in usage:
            usage_cpu = element[2]
            total_usage.append(usage_cpu)

        total_usage = sum(float(i) for i in total_usage)

        total_free = ((100 * int(get_cpus()['cpus'])) - float(total_usage))

        cpu_used = {'free': total_free, 'used': float(total_usage), 'all': usage}

        data = cpu_used

    except Exception, err:
        data = str(err)

    return data

def setup_database():
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE user_string (data)")

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

    webapp = StringGenerator()
    #webapp.generator = StringGeneratorWebService()
    cherrypy.config.update({'server.socket_host': '192.168.241.128',})
    cherrypy.quickstart(webapp, '/', conf)
