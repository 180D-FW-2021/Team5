import sys
from PyQt5.QtCore import QCoreApplication, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtGui

class window(QMainWindow):

    def __init__(self):

        super(window, self).__init__()
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('Andre\'s control center')
        self.setWindowIcon(QIcon('ik.jpg'))


        self.label = QLabel('Dit is het control center van Andre Jochemsen',self)
        self.label.setGeometry(10,10,400,50)



        extractAction = QAction('&Exit', self)
        extractAction.setShortcut('Ctrl+Q')
        extractAction.setStatusTip('Sluit de applicatie')
        extractAction.triggered.connect(self.close_application)

        # Intermaris

        intAlgemeen = QAction('&Algemeen', self)
        intAlgemeen.triggered.connect(self.intermaris_algemeen)

        intIncidenten = QAction('&Incidenten', self)
        intIncidenten.triggered.connect(self.intermaris_algemeen)

        intWijzigingen = QAction('&Wijzigingen', self)
        intWijzigingen.triggered.connect(self.intermaris_algemeen)

        # Balance

        balAlgemeen = QAction('&Algemeen', self)
        balAlgemeen.triggered.connect(self.intermaris_algemeen)

        balIncidenten = QAction('&Incidenten', self)
        balIncidenten.triggered.connect(self.intermaris_algemeen)

        balWijzigingen = QAction('&Wijzigingen', self)
        balWijzigingen.triggered.connect(self.intermaris_algemeen)

        # Brakel Atmos

        braAlgemeen = QAction('&Algemeen', self)
        braAlgemeen.triggered.connect(self.intermaris_algemeen)

        braIncidenten = QAction('&Incidenten', self)
        braIncidenten.triggered.connect(self.intermaris_algemeen)

        braWijzigingen = QAction('&Wijzigingen', self)
        braWijzigingen.triggered.connect(self.intermaris_algemeen)

        self.statusBar()

        mainMenu  = self.menuBar()
        fileMenu2 = self.menuBar()
        fileMenu3 = self.menuBar()
        fileMenu4 = self.menuBar()


        fileMenu = mainMenu.addMenu('&File')
        fileMenu2 = mainMenu.addMenu('&Balance')
        fileMenu3 = mainMenu.addMenu('&Brakel Atmos')
        fileMenu4 = mainMenu.addMenu('&Intermaris')


        fileMenu.addAction(extractAction)
        fileMenu2.addAction(balAlgemeen)
        fileMenu2.addAction(balIncidenten)
        fileMenu2.addAction(balWijzigingen)
        fileMenu3.addAction(braAlgemeen)
        fileMenu3.addAction(braIncidenten)
        fileMenu3.addAction(braWijzigingen)
        fileMenu4.addAction(intAlgemeen)
        fileMenu4.addAction(intIncidenten)
        fileMenu4.addAction(intWijzigingen)


        self.show()


    def close_application(self):
    # deze method wordt toegepast op de 1e instance, in dit geval self.
        choice = QMessageBox.question(self, 'message',
                                        "Nooo! R u sure?", QMessageBox.Yes |
                                        QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            print('quit application')
            sys.exit()
        else:
            pass

    def intermaris_algemeen(self):
        print('Button clicked.')



def run():
    app = QApplication(sys.argv)
    Gui = window()
    sys.exit(app.exec_())

run()
