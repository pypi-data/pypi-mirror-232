# Form implementation generated from reading ui file 'qt/aqt/forms/about.ui'
#
# Created by: PyQt6 UI code generator 6.5.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from aqt.utils import tr



class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(410, 664)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(About.sizePolicy().hasHeightForWidth())
        About.setSizePolicy(sizePolicy)
        self.vboxlayout = QtWidgets.QVBoxLayout(About)
        self.vboxlayout.setContentsMargins(0, 0, 0, 0)
        self.vboxlayout.setObjectName("vboxlayout")
        self.label = AnkiWebView(parent=About)
        self.label.setProperty("url", QtCore.QUrl("about:blank"))
        self.label.setObjectName("label")
        self.vboxlayout.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=About)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(About)
        self.buttonBox.accepted.connect(About.accept) # type: ignore  # type: ignore
        self.buttonBox.rejected.connect(About.reject) # type: ignore  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(tr.about_about_anki())
from aqt.webview import AnkiWebView