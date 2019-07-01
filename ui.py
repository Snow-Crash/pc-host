# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1134, 828)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(30)
        self.layout.setObjectName("layout")
        self.control_panel = QtWidgets.QVBoxLayout()
        self.control_panel.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.control_panel.setObjectName("control_panel")
        self.btn = QtWidgets.QPushButton(self.centralwidget)
        self.btn.setMaximumSize(QtCore.QSize(200, 16777215))
        self.btn.setMouseTracking(False)
        self.btn.setObjectName("btn")
        self.control_panel.addWidget(self.btn)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setMaximumSize(QtCore.QSize(200, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.control_panel.addWidget(self.lineEdit)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.comboBox.setObjectName("comboBox")
        self.control_panel.addWidget(self.comboBox)
        self.listView = QtWidgets.QListView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView.sizePolicy().hasHeightForWidth())
        self.listView.setSizePolicy(sizePolicy)
        self.listView.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listView.setObjectName("listView")
        self.control_panel.addWidget(self.listView)
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setMaximumSize(QtCore.QSize(200, 16777215))
        self.checkBox.setObjectName("checkBox")
        self.control_panel.addWidget(self.checkBox)
        self.layout.addLayout(self.control_panel, 0, 0, 3, 1)
        self.raw_data_plot = PlotWidget(self.centralwidget)
        self.raw_data_plot.setObjectName("raw_data_plot")
        self.layout.addWidget(self.raw_data_plot, 0, 1, 1, 1)
        self.voltage_plot = PlotWidget(self.centralwidget)
        self.voltage_plot.setObjectName("voltage_plot")
        self.layout.addWidget(self.voltage_plot, 1, 2, 1, 1)
        self.outspike_plot = QtWidgets.QGraphicsView(self.centralwidget)
        self.outspike_plot.setObjectName("outspike_plot")
        self.layout.addWidget(self.outspike_plot, 2, 1, 1, 1)
        self.psp_plot = PlotWidget(self.centralwidget)
        self.psp_plot.setObjectName("psp_plot")
        self.layout.addWidget(self.psp_plot, 1, 1, 1, 1)
        self.inspike_plot = PlotWidget(self.centralwidget)
        self.inspike_plot.setObjectName("inspike_plot")
        self.layout.addWidget(self.inspike_plot, 0, 2, 1, 1)
        self.gridLayout.addLayout(self.layout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1134, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn.setText(_translate("MainWindow", "run"))
        self.checkBox.setText(_translate("MainWindow", "CheckBox"))

from pyqtgraph import PlotWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

