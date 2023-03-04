import sublime
import sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import _thread
import threading
import platform
import os
import re
import time

def decodeStringsOfFile(s):
    L = ["<", ">", "/", "\\", "|", ":", "\"", "*", "?", ".", "\'", "(", ")"]
    for i in L:
        s = s.replace(i, "")
    s = re.sub('[^\x00-\xFF\u4e00-\u9fa5]', '', s)
    return s
def MakeHandlerClassFromFilename():
    class HandleRequests(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                print(body)
                J = json.loads(body.decode('utf8'))
                settings = sublime.load_settings("FastOlympicCodingHook.sublime-settings")
                templateFile = settings.get("template-file")
                parsedProblemsFolder = settings.get("parse-folder")
                print("Received")
                g = open(templateFile, "r")
                templ = g.read()
                g.close()
                if(type(J).__name__ == "array"):
                    for i in range(len(J)):
                        tests = J[i]
                        dirc = parsedProblemsFolder + decodeStringsOfFile(tests["group"].replace(" ", "_")) + "/"
                        if not os.path.exists(dirc):
                            os.mkdir(dirc)
                        fn = dirc + decodeStringsOfFile(tests["name"].replace(" ", "_")) + '.' + settings.get("file-suffix", "cpp");
                        fl_size = -1
                        if not os.path.exists(fn):
                            cppF = open(fn, "w", encoding = "utf-8")
                            code = (templ
                                .replace("%$Problem$%" , tests["name"])
                                .replace("%$Contest$%" , tests["group"])
                                .replace("%$URL$%"     , tests["url"])
                                .replace("%$Time$%"    , time.strftime(settings.get("time-format", "%Y-%m-%d %H:%M:%S"), time.localtime()))
                                .replace("%$MemoryL$%" , str(tests["memoryLimit"]))
                                .replace("%$TimeL$%"   , str(tests["timeLimit"])))
                            cppF.write(code)
                            fl_size = len(code)
                            cppF.close()
                        else:
                            fl_size = os.path.getsize(fn)
                        vw = sublime.active_window().open_file(fn)
                        while vw.is_loading() == True:
                            pass
                        vw.show(fl_size, animate = False)
                        tests = tests["tests"]
                        ntests = []
                        for test in tests:
                            ntest = {
                                "test": test["input"],
                                "correct_answers": [test["output"].strip()]
                            }
                            ntests.append(ntest)
                        nfilename = fn + ":tests"
                        if platform.system() == "Windows":
                            nfilename = fn + "__tests"
                        with open(nfilename, "w") as f:
                            f.write(json.dumps(ntests))
                else:
                    tests = J
                    dirc = parsedProblemsFolder + decodeStringsOfFile(tests["group"].replace(" ", "_")) + "/"
                    if not os.path.exists(dirc):
                        os.mkdir(dirc)
                    fn = dirc + decodeStringsOfFile(tests["name"].replace(" ", "_")) + '.' + settings.get("file-suffix", "cpp");
                    fl_size = -1
                    if not os.path.exists(fn):
                        cppF = open(fn, "w", encoding = "utf-8")
                        code = (templ
                            .replace("%$Problem$%" , tests["name"])
                            .replace("%$Contest$%" , tests["group"])
                            .replace("%$URL$%"     , tests["url"])
                            .replace("%$Time$%"    , time.strftime(settings.get("time-format", "%Y-%m-%d %H:%M:%S"), time.localtime()))
                            .replace("%$MemoryL$%" , str(tests["memoryLimit"]))
                            .replace("%$TimeL$%"   , str(tests["timeLimit"])))
                        cppF.write(code)
                        fl_size = len(code)
                        cppF.close()
                    else:
                        fl_size = os.path.getsize(fn)
                    vw = sublime.active_window().open_file(fn)
                    while vw.is_loading() == True:
                        pass
                    vw.show(fl_size, animate = False)
                    tests = tests["tests"]
                    ntests = []
                    for test in tests:
                        ntest = {
                            "test": test["input"],
                            "correct_answers": [test["output"].strip()]
                        }
                        ntests.append(ntest)
                    nfilename = fn + ":tests"
                    if platform.system() == "Windows":
                        nfilename = fn + "__tests"
                    with open(nfilename, "w") as f:
                        f.write(json.dumps(ntests))
            except Exception as e:
                print("Error handling POST - ``" + str(e))
            self.send_response(202)
            self.end_headers()
    return HandleRequests


class CompetitiveCompanionServer:
    def startServer():
        host = 'localhost'
        settings = sublime.load_settings("FastOlympicCodingHook.sublime-settings")
        port = settings.get("server-port", 12345)
        HandlerClass = MakeHandlerClassFromFilename()
        global httpd
        httpd = HTTPServer((host, port), HandlerClass)
        httpd.allow_reuse_address = True
        print("Start server... - ::" + str(port))
        httpd.serve_forever()
        print("Server has been shutdown")

try:
    _thread.start_new_thread(CompetitiveCompanionServer.startServer,
                             ())
except Exception as e:
    print("Error: unable to start thread - " + str(e))
