import json
import os, os.path
import random
import sqlite3
import string

import cherrypy

DB_STRING = "my.db"

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return file('')

class StringGeneratorWebService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')#@login_required(login_url='/login/')
    def memusage(request):
        with sqlite3.connect(DB_STRING) as c:
            tasets_free = []
            tasets_used = []

            try:
                mem_usage = get_mem()
            except Exception:
                mem_usage = 0

            try:
                cookies = request._cookies['memory_usage']
            except Exception:
                cookies = None

            if not cookies:
                datasets_free.append(0)
                datasets_used.append(0)
            else:
                datasets = json.loads(cookies)
                datasets_free = datasets[0]
                datasets_used = datasets[1]

            if len(datasets_free) > 10:
                while datasets_free:
                    del datasets_free[0]
                    if len(datasets_free) == 10:
                        break
            if len(datasets_used) > 10:
                while datasets_used:
                    del datasets_used[0]
                    if len(datasets_used) == 10:
                        break
            if len(datasets_free) <= 9:
                datasets_free.append(int(mem_usage['free']))
            if len(datasets_free) == 10:
                datasets_free.append(int(mem_usage['free']))
                del datasets_free[0]
            if len(datasets_used) <= 9:
                datasets_used.append(int(mem_usage['usage']))
            if len(datasets_used) == 10:
                datasets_used.append(int(mem_usage['usage']))
                del datasets_used[0]

            if len(datasets_free) == 10:
                if sum(datasets_free) == 0:
                    datasets_free[9] += 0.1
                if sum(datasets_free) / 10 == datasets_free[0]:
                    datasets_free[9] += 0.1

            memory = {
                'labels': [""] * 10,
                'datasets': [
                    {
                        "data": datasets_used
                    },
                    {
                        "data": datasets_free
                    }
                ]
            } 

            cookie_memory = [datasets_free, datasets_used]
            data = json.dumps(memory)
            response = HttpResponse()
            response['Content-Type'] = "text/javascript"
            response.cookies['memory_usage'] = cookie_memory
            response.write(data)
            return c.response

    def get_mem():
        with sqlite3.connect(DB_STRING) as c:
            try:
                pipe = os.popen("free -tmo | " + "grep 'Mem' | " + "awk '{print $2,$4}'")
                data = pipe.read().strip().split()
                pipe.close()

                allmem = int(data[0])
                freemem = int(data[1])

                percent = (100 - ((freemem * 100) / allmem))
                usage = (allmem - freemem)

                mem_usage = {'usage': usage, 'free': freemem, 'percent': percent}

                data = mem_usage

            except Exception, err:
                data = str(err)

            return c.data

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
    webapp = StringGenerator()
    webapp.generator = StringGeneratorWebService()
    cherrypy.config.update({'server.socket_host': '192.168.241.128',})
    cherrypy.quickstart(webapp, '/', conf)

