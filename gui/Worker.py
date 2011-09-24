from globals.global_imports import *

class WorkerThread(QtCore.QThread):
    def __init__(self, name, *args):
        QtCore.QThread.__init__(self)
        self.counter=0
        self.name=name
        print "Initializing: %s" % name

    def run(self):
        print "Starting %s" % self.name
        pass