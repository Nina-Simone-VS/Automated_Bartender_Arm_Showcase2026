import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot , QThread

#import hardware code
import Bartender_arm_movement_code

#DELETE THIS ↓
import time
# ↑
class BartWorker(QThread):
    sequenceDone = Signal()

    def __init__(self, drinkName, withMixer):
        super().__init__()
        self.drinkName = drinkName
        self.withMixer = withMixer
    #end constructor

    def run(self):
        print(f"HARDWARE THREAD: activate Bart for {self.drinkName}")

        try:
            roboArm = Bartender_arm_movement_code.Arm()
            roboArm.connect()

            #connect arm to bartender logic class
            bart = Bartender_arm_movement_code.Bartender(roboArm)

            #perform drink seq
            bart.make_drink(self.drinkName)

            #drink done
            roboArm.close()
            print("HARDWARE THREAD: Drink completed")
        except Exception as e:
            print(f"HARDWARE THREAD error: {e}")

            #fake an order for me DELETE THIS
            print(f"\nSimulate 5sec delay for testing UI")
            time.sleep(5)
        finally:
            #unlock QML screen
            self.sequenceDone.emit() 
        #end try drink seq
    #end run pour sequence fn  
#worker thread for arm movement

class Backend(QObject):
    updatedDrinks = Signal(list, list, arguments = ['drinkList', 'orderList'])
    armReady = Signal()

    def __init__(self):
        super().__init__()
        self.worker = None

        #recipe names
        self.recipeNames = [
            "Blueberry_Bliss",
            "Cranberry_Crush",
            "Pomegranate_Punch",
            "Passion_fruit_Paradise",
            "Watermelon_Wonder"
        ]
    #end constructor fn

    def loadDrinks(self):
        drinkMenu = ["DrinkB.jpeg","DrinkC.jpeg","DrinkG.jpeg","DrinkP.jpeg","DrinkW.jpeg"]
        orderMenu= ["OrderB.jpeg","OrderC.jpeg","OrderG.jpeg","OrderP.jpeg","OrderW.jpeg"]
        self.updatedDrinks.emit(drinkMenu, orderMenu)
    #end load python list of drink menu fn

    @Slot(int, bool) #QML can call & give int and bool
    def startPour(self,drinkIndex , isStill):
        drinkName = self.recipeNames[drinkIndex]
        withMixer = isStill

        print("BACKEND: Asynchronous execution of bg thread for motors...")

        #thread setup for GUI and motors
        self.worker = BartWorker(drinkName, withMixer)
        self.worker.sequenceDone.connect(self.finishPour)

        #MOTORS STARTING
        self.worker.start()
    #end start pour fn

    def finishPour(self):
        #unlock gui
        print("BACKEND: Motors stationary, give GUI unlock signal")
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
