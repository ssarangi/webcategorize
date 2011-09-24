from PyQt4 import QtGui

class TabManager(QtGui.QTabWidget):
    def __init__(self, *args):
        QtGui.QTabWidget.__init__(self, *args)
        self.views = []
        
    def addView(self, view):
        if view not in self.views:
            self.views.append(view)
            self.addTab(view, view.caption())
            self.showPage(view)
            
    def _createView(self, document, viewClass):
        view = viewClass(self._viewManager,
                         document,
                         None,
                         QtGui.QWidget.WDestructiveClose)
        
        if (self._docToViewMap.has_key(document)):
            index = len(self._docToViewMap[document]) + 1
        else:
            index = 1
        view.setCaption(document.title() + " %s" % index)

        self._viewManager.addView(view)

        view.installEventFilter(self._parent)

        if self._viewToDocMap == {}:
            view.showMaximized()
        else:
            view.show()

        return view
    
    def removeView(self, view):
        if view in self.views:
            self.views.remove(view)
            self.removePage(view)

    def activeWindow(self):
        return self.currentPage()

    def windowList(self):
        return self.views
    
    def _removeView(self, view, document):
        try:
            self._docToViewMap[document].remove(view)
            self._viewManager.removeView(view)
            del self._viewToDocMap[view]
        except ValueError, e:
            pass # apparently already deleted    
            
    def cascade(self):
        pass

    def tile(self):
        pass

    def canCascade(self):
        return False

    def canTile(self):
        return False
    
        