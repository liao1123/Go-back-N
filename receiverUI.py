# Form implementation generated from reading ui file 'receiverUI.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(591, 240)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=Form)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 10, 331, 171))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(parent=Form)
        self.pushButton.setGeometry(QtCore.QRect(350, 20, 75, 24))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_2.setGeometry(QtCore.QRect(430, 20, 75, 24))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setGeometry(QtCore.QRect(510, 20, 75, 24))
        self.pushButton_3.setObjectName("pushButton_3")
        self.buttonBox = QtWidgets.QDialogButtonBox(parent=Form)
        self.buttonBox.setGeometry(QtCore.QRect(390, 120, 156, 24))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(430, 80, 131, 31))
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "接收"))
        self.pushButton_2.setText(_translate("Form", "丢弃"))
        self.pushButton_3.setText(_translate("Form", "损坏"))
        self.label.setText(_translate("Form", "是否发送ACK"))
