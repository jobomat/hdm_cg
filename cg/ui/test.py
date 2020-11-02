from PySide2 import QtWidgets
import os


style_path = "D:/coding/python/pyside"


class SceneRow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(GuiTest, self).__init__(parent)
        with open(os.path.join(style_path, 'test.css')) as css_file:
            css = css_file.read()
            # print(css)
        self.setStyleSheet(css)

        nameLabel = QtWidgets.QLabel("Irgendwas:")
        self.nameLine = QtWidgets.QLineEdit()
        self.nameLine.setReadOnly(True)

        self.addButton = QtWidgets.QPushButton("&Lock/Unlock")
        self.addButton.show()

        self.dialog = MyDialog()

        self.addButton.clicked.connect(self.myDialog)

        buttonLayout1 = QtWidgets.QVBoxLayout()
        buttonLayout1.addWidget(self.addButton)
        buttonLayout1.addStretch()

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addLayout(buttonLayout1, 1, 2)

        self.setLayout(mainLayout)
        self.setWindowTitle("Simple GuiTest")

    def myDialog(self):
        self.dialog.show()

        if self.dialog.exec_() == QtWidgets.QDialog.Accepted:
            theInput = self.dialog.getFindText()

            if theInput in ['unlock', 'go']:
                self.nameLine.setReadOnly(False)
            elif theInput in ['lock', 'stop']:
                self.nameLine.setReadOnly(True)
            else:
                QtWidgets.QMessageBox.information(
                    self, "Not the magic word",
                    "Sorry, \"%s\" is not the expected magic word." % theInput
                )
                return
            self.nameLine.setStyle(self.nameLine.style())


class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        findLabel = QtWidgets.QLabel("Enter the magic word:")
        self.lineEdit = QtWidgets.QLineEdit()

        self.findButton = QtWidgets.QPushButton("&GO!")
        self.findText = ''

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(findLabel)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.findButton)

        self.setLayout(layout)
        self.setWindowTitle("Unlock with magic")

        self.findButton.clicked.connect(self.findClicked)
        self.findButton.clicked.connect(self.accept)

    def findClicked(self):
        text = self.lineEdit.text()

        if not text:
            QtWidgets.QMessageBox.information(
                self, "Empty Field",
                "Please enter a word."
            )
            return

        self.findText = text
        self.lineEdit.clear()
        self.hide()

    def getFindText(self):
        return self.findText
