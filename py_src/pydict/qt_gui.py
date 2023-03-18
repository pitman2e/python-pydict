import sys
import os
import pyperclip
import traceback
from typing import List

from . import yahoo_dict
import os
from PyQt6 import QtCore, QtWidgets, uic
from .hjenglish_jp_core import HJEnglishWebDriverCore
from .dict_result import DictResult
from .logger import logger

UiFileDir: str = os.path.dirname(os.path.dirname(__file__))
UriFilePath: str = os.path.join(UiFileDir, "pydict", "ui", "dict.ui")

class qt_gui(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(qt_gui, self).__init__()
        uic.loadUi(UriFilePath, self)

        logger.set_log_widget(self.lstLog)

        self.cbbTranType: QtWidgets.QComboBox
        self.btnCheckNext: QtWidgets.QPushButton
        self.btnCheck: QtWidgets.QPushButton
        self.btnCopyWord: QtWidgets.QPushButton
        self.btnCopyResult: QtWidgets.QPushButton
        self.txtWord2Check: QtWidgets.QTextEdit
        self.txtSuggestion: QtWidgets.QTextEdit
        self.lstHistory: QtWidgets.QListWidget
        self.lblStatus: QtWidgets.QLabel
        self.cbxIsMultiline: QtWidgets.QCheckBox
        self.lstLog: QtWidgets.QListWidget
        self.btnRefreshCore: QtWidgets.QPushButton

        self.btnCheck.clicked.connect(self.btnCheck_Clicked)
        self.btnCheckNext.clicked.connect(self.btnCheckNext_Clicked)
        self.btnRefreshCore.clicked.connect(self.btnRefreshCore_Clicked)
        self.lstHistory.currentItemChanged.connect(self.lstHistory_currentItemChanged)

        self.cbbTranType.addItem("EN")
        self.cbbTranType.addItem("JP")
        
        self.btnCopyResult.clicked.connect(lambda : pyperclip.copy(self.txtResult.toPlainText()))
        self.btnCopyWord.clicked.connect(lambda : pyperclip.copy(self.txtWord.text()))
        #self.txtResult.installEventFilter(self) # No longer needed since copy function exists, keep for ref
        self.txtWord2Check.installEventFilter(self)
        self.cbbTranType.currentTextChanged.connect(self.cbbTranType_currentTextChanged)
        self.txtWord2Check.setFocus()
        
        self.core = None

        logger.log("Program initialised")

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> None:
        if source is self.txtWord2Check:
            if event.type() == QtCore.QEvent.Type.KeyPress:
                if (event.modifiers() == QtCore.Qt.Modifier.SHIFT) or not self.cbxIsMultiline.isChecked():
                    if ((event.key() == QtCore.Qt.Key.Key_Enter) or (event.key() == QtCore.Qt.Key.Key_Return)):
                        self.btnCheck_Clicked()
                        return True
            if event.type() == QtCore.QEvent.Type.FocusIn:
                if not self.cbxIsMultiline.isChecked():
                    if len(self.txtWord2Check.toPlainText()) > 0: #If selectAll at empty box => cursor not appearing
                        # https://www.qtcentre.org/threads/31705-selectAll-in-QLineEdit-does-not-work?p=277477#post277477
                        # Workaround mouse click cancels selectAll()
                        QtCore.QTimer.singleShot(0, lambda: self.txtWord2Check.selectAll())
                        return True
                    
        return False

    def cbbTranType_currentTextChanged(self) -> None:
        if self.cbbTranType.currentText() == "JP":
            if self.core == None:
                self.core = HJEnglishWebDriverCore()
                logger.log("Init HJ English Core")
        else:
            self.core.close()
            self.core = None
            logger.log("Close HJ English Core")

    
    def lstHistory_currentItemChanged(self, current: QtWidgets.QListWidgetItem, prev: QtWidgets.QListWidgetItem) -> None:
        word2Change: str = current.text()
        word2Check: str = self.txtWord2Check.toPlainText()
        txtWordsCheck: List[str] = word2Check.split("\n")

        if self.cbxIsMultiline.isChecked():
            if word2Change in txtWordsCheck:
                txtWordsCheck.remove(word2Change)
            self.txtWord2Check.setText(word2Change + "\n" + "\n".join(txtWordsCheck))
        else:
            self.txtWord2Check.setText(word2Change)

    def closeEvent(self, event) -> None:
        if self.core is not None: 
            self.core.close()

    def btnCheck_Clicked(self) -> None:
        newItem = QtWidgets.QListWidgetItem()
        newItem.setText(self.txtWord2Check.toPlainText())
        self.lstHistory.insertItem(0, newItem)
        self.getDictionaryResult(self.txtWord2Check.toPlainText())
    
    def btnCheckNext_Clicked(self) -> None:
        words = self.txtWord2Check.toPlainText().split("\n")
        if self.txtWord.text() == words[0]:
            if len(words) > 1:
                self.txtWord2Check.setText("\n".join(words[1:]))
                self.getDictionaryResult(words[1])
        else:
            self.getDictionaryResult(words[0])

    def btnRefreshCore_Clicked(self) -> None:
        if self.cbbTranType.currentText() == "JP":
            self.core.close()
            self.core = HJEnglishWebDriverCore()
            logger.log("Refreshed HJ English Core")

    def getDictionaryResult(self, word2Search: str) -> None:
        self.btnCheck.setDisabled(True)

        try:
            result: DictResult
            
            if self.cbbTranType.currentText() == "JP":
                result = self.core.GetDictionaryResult(word2Search)
            elif self.cbbTranType.currentText() == "EN":
                result = yahoo_dict.Check_EN_ZH(word2Search)
            else:
                raise Exception("Unrecognised Dictionary Type")
                
            if (result.is_success):
                self.txtWord.setText(result.word)
                self.txtResult.setText(result.definition)
                self.lblStatus.setText("")
            else:
                self.lblStatus.setText("Word definition not found")
                
            self.txtSuggestion.setText(result.suggestion)

        except Exception:
            self.txtResult.setText("An error has occured: \n" + traceback.format_exc())
        finally:
            self.btnCheck.setDisabled(False)

def run() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = qt_gui()
    window.show()
    sys.exit(app.exec())