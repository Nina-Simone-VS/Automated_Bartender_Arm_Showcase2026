import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot , QTimer

class Backend(QObject):
    updatedDrinks = Signal(list, list, arguments = ['drinkList', 'orderList'])
    armReady = Signal()

    def __init__(self):
        super().__init__()
    #end constructor fn

    def loadDrinks(self):
        drinkMenu = ["DrinkB.jpeg","DrinkC.jpeg","DrinkG.jpeg","DrinkP.jpeg","DrinkW.jpeg"]
        orderMenu= ["OrderB.jpeg","OrderC.jpeg","OrderG.jpeg","OrderP.jpeg","OrderW.jpeg"]
        self.updatedDrinks.emit(drinkMenu, orderMenu)
    #end load python list of drink menu fn

    @Slot() #QML can call
    def startPour(self):
        print("Hardware: Motors moving...")
        #wait 5sec for movement
        QTimer.singleShot(5000, self.armReady)
    #end start pour fn

    def finishPour(self):
        #unlock gui
        print("Hardware: Motors stationary")
        self.armReady.emit()
    #end finish pour fn
#end backend class

class BartenderMenuApp:
    def __init__(self):
       #use QML instead of Qt widgets
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine() 

        self.backend = Backend()

        #connect quits of UI to main app stopping
        self.engine.quit.connect(self.app.quit)
        #load QML file for UI
        self.engine.load('main.qml')

        self.engine.rootObjects()[0].setProperty('backend', self.backend)
        self.backend.loadDrinks()
    #end constructor
 
    def run(self):
        sys.exit(self.app.exec()) 
    #end run gui fn
#end menuapp class

if __name__=='__main__':
    ui_app = BartenderMenuApp()
    ui_app.run()
#end if run main fn
