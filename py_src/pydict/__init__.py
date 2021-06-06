import sys
import os
import inspect
import pyperclip
import traceback
import pydict.yahoo_dict
import os
from PySide2 import QtCore, QtWidgets, QtUiTools
from pydict.hjenglish_jp_core import HJEnglishWebDriverCore

UiFileDir: str = os.path.dirname(inspect.getfile(pydict))
UriFilePath: str = os.path.join(UiFileDir, "dict.ui")

Ui_MainWindow, QtBaseClass = QtUiTools.loadUiType(UriFilePath)

class DictQtGui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.cbbTranType: QtWidgets.QComboBox
        self.btnCheckNext: QtWidgets.QPushButton
        self.btnChecked: QtWidgets.QPushButton
        self.btnCopyWord: QtWidgets.QPushButton
        self.txtWord2Check: QtWidgets.QTextEdit

        self.btnCheck.clicked.connect(self.btnCheck_Clicked)
        self.btnCheckNext.clicked.connect(self.btnCheckNext_Clicked)

        self.cbbTranType.addItem("EN")
        self.cbbTranType.addItem("JP")
        
        self.btnCopyResult.clicked.connect(lambda : pyperclip.copy(self.txtResult.toPlainText()))
        self.btnCopyWord.clicked.connect(lambda : pyperclip.copy(self.txtWord.text()))
        #self.txtResult.installEventFilter(self) # No longer needed since copy function exists, keep for ref
        self.txtWord2Check.installEventFilter(self)
        self.cbbTranType.currentTextChanged.connect(self.cbbTranType_currentTextChanged)
        
        self.core = None

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> None:
        if source is self.txtWord2Check:
            if event.type() == QtCore.QEvent.KeyPress:
                if (event.modifiers() == QtCore.Qt.ShiftModifier) and (event.key() & QtCore.Qt.Key_Enter):
                    self.btnCheck_Clicked()
                    return True
                    
        return False

    def cbbTranType_currentTextChanged(self):
        if self.cbbTranType.currentText() == "JP":
            if self.core == None:
                self.core = HJEnglishWebDriverCore()
                print("Init Core")
        else:
            self.core.close()
            self.core = None
            print("Close Core")

    def closeEvent(self, event) -> None:
        self.core.close()

    def btnCheck_Clicked(self) -> None:
        self.getDictionaryResult(self.txtWord2Check.toPlainText())
    
    def btnCheckNext_Clicked(self) -> None:
        words = self.txtWord2Check.toPlainText().split("\n")
        if self.txtWord.text() == words[0]:
            if len(words) > 1:
                self.txtWord2Check.setText("\n".join(words[1:]))
                self.getDictionaryResult(words[1])
        else:
            self.getDictionaryResult(words[0])

    def getDictionaryResult(self, word2Search) -> None:
        self.btnCheck.setDisabled(True)

        try:
            result: str
            isOK: bool
            
            if self.cbbTranType.currentText() == "JP":
                result, isOK = self.core.GetDictionaryResult(word2Search)
            elif self.cbbTranType.currentText() == "EN":
                resultDict = pydict.yahoo_dict.Check_EN_ZH(word2Search)
                result, isOK = resultDict['definition'], resultDict['isSuccess']
            else:
                raise Exception("Unrecognised Dictionary Type")
                
            if (isOK):
                self.txtWord.setText(word2Search)
            self.txtResult.setText(result)

        except Exception:
            self.txtResult.setText("An error has occured: \n" + traceback.format_exc())
        finally:
            self.btnCheck.setDisabled(False)

def run() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = DictQtGui()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()