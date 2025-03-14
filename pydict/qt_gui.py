import sys
import pyperclip
import traceback
from typing import List

from pydict import da_jp, yahoo_dict
import os
from PyQt6 import QtCore, QtWidgets, uic
from pydict.dict_result import DictResult
from pydict.logger import Logger

UiFileDir: str = os.path.dirname(os.path.dirname(__file__))
UriFilePath: str = os.path.join(UiFileDir, "pydict", "ui", "dict.ui")
dict_result_hist: dict[str, DictResult] = {}


class QtGui(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(QtGui, self).__init__()
        uic.loadUi(UriFilePath, self)

        Logger.set_log_widget(self.lstLog)

        self.is_raw_result = True
        self.dict_result: DictResult = None

        self.cbbTranType: QtWidgets.QComboBox
        self.btnCheckNext: QtWidgets.QPushButton
        self.btnCheck: QtWidgets.QPushButton
        self.btnCopyWord: QtWidgets.QPushButton
        self.btnCopyResult: QtWidgets.QPushButton
        self.txtWord2Check: QtWidgets.QTextEdit
        self.txtSuggestion: QtWidgets.QTextEdit
        self.txtResult: QtWidgets.QTextEdit
        self.txtWord: QtWidgets.QTextEdit
        self.lstHistory: QtWidgets.QListWidget
        self.lblStatus: QtWidgets.QLabel
        self.cbxIsMultiline: QtWidgets.QCheckBox
        self.lstLog: QtWidgets.QListWidget
        self.btnToggleRaw: QtWidgets.QPushButton

        self.btnCheck.clicked.connect(self.btn_check_clicked)
        self.btnCheckNext.clicked.connect(self.btn_check_next_clicked)
        self.btnToggleRaw.clicked.connect(self.btn_toggle_raw_clicked)
        self.lstHistory.currentItemChanged.connect(self.lst_history_current_item_changed)

        self.cbbTranType.addItem("EN")
        self.cbbTranType.addItem("JP")
        
        self.btnCopyResult.clicked.connect(lambda : pyperclip.copy(self.txtResult.toPlainText()))
        self.btnCopyWord.clicked.connect(lambda : pyperclip.copy(self.txtWord.text()))
        #self.txtResult.installEventFilter(self) # No longer needed since copy function exists, keep for ref
        self.txtWord2Check.installEventFilter(self)
        self.cbbTranType.currentTextChanged.connect(self.cbb_tran_type_current_text_changed)
        self.txtWord2Check.setFocus()
        
        Logger.log("Program initialised")

    # Do not modify function name, meant to override
    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if source is self.txtWord2Check:
            if event.type() == QtCore.QEvent.Type.KeyPress:
                if (event.modifiers() == QtCore.Qt.Modifier.SHIFT) or not self.cbxIsMultiline.isChecked():
                    if (event.key() == QtCore.Qt.Key.Key_Enter) or (event.key() == QtCore.Qt.Key.Key_Return):
                        self.btn_check_clicked()
                        return True
            if event.type() == QtCore.QEvent.Type.FocusIn:
                if not self.cbxIsMultiline.isChecked():
                    if len(self.txtWord2Check.toPlainText()) > 0: #If selectAll at empty box => cursor not appearing
                        # https://www.qtcentre.org/threads/31705-selectAll-in-QLineEdit-does-not-work?p=277477#post277477
                        # Workaround mouse click cancels selectAll()
                        QtCore.QTimer.singleShot(0, lambda: self.txtWord2Check.selectAll())
                        return True
                    
        return False

    def cbb_tran_type_current_text_changed(self) -> None:
        dict_result_hist.clear()
        self.lstHistory.currentItemChanged.disconnect(self.lst_history_current_item_changed)
        self.lstHistory.clear()
        self.lstHistory.currentItemChanged.connect(self.lst_history_current_item_changed)

    
    def lst_history_current_item_changed(self, current: QtWidgets.QListWidgetItem, prev: QtWidgets.QListWidgetItem) -> None:
        word_to_change: str = current.text()
        word_to_check: str = self.txtWord2Check.toPlainText()
        words_2_check: List[str] = word_to_check.split("\n")

        if self.cbxIsMultiline.isChecked():
            if word_to_change in words_2_check:
                words_2_check.remove(word_to_change)
            self.txtWord2Check.setText(word_to_change + "\n" + "\n".join(words_2_check))
        else:
            self.txtWord2Check.setText(word_to_change)
        
        if word_to_change in dict_result_hist:
            self.txtResult.setText(dict_result_hist[word_to_change].definition)
            self.txtSuggestion.setText("")
            self.txtWord.setText("")

    # Do not modify function name, meant to override
    def closeEvent(self, event) -> None:
        pass

    def btn_check_clicked(self) -> None:
        new_item = QtWidgets.QListWidgetItem()
        new_item_text = self.txtWord2Check.toPlainText()
        new_item.setText(new_item_text)

        if new_item_text not in dict_result_hist:
            self.lstHistory.insertItem(0, new_item)
            self.get_dictionary_result(self.txtWord2Check.toPlainText())
        else:
            self.is_raw_result = True
            self.apply_ui_dict_result(dict_result_hist[new_item_text])

    def btn_check_next_clicked(self) -> None:
        words = self.txtWord2Check.toPlainText().split("\n")
        if self.txtWord.text() == words[0]:
            if len(words) > 1:
                self.txtWord2Check.setText("\n".join(words[1:]))
                self.get_dictionary_result(words[1])
        else:
            self.get_dictionary_result(words[0])

    def btn_toggle_raw_clicked(self) -> None:
        self.is_raw_result = not self.is_raw_result
        self.apply_ui_dict_result(self.dict_result)


    def get_dictionary_result(self, word2search: str) -> None:
        self.btnCheck.setDisabled(True)

        try:

            if self.cbbTranType.currentText() == "JP":
                result = da_jp.get_dictionary_result(word2search)
            elif self.cbbTranType.currentText() == "EN":
                result = yahoo_dict.check_en_zh(word2search)
            else:
                raise Exception("Unrecognised Dictionary Type")

            if result.is_success:
                self.is_raw_result = True

            self.apply_ui_dict_result(result)
            dict_result_hist[result.word] = result
            self.dict_result = result

        except Exception:
            self.txtResult.setText("An error has occured: \n" + traceback.format_exc())
        finally:
            self.btnCheck.setDisabled(False)

    def apply_ui_dict_result(self, result: DictResult):
        if result.is_success:
            self.txtWord.setText(result.word)
            if self.is_raw_result:
                self.txtResult.setText(result.definition)
            else:
                self.txtResult.setText(result.definition_tc)

            self.lblStatus.setText("")
        else:
            self.lblStatus.setText("Word definition not found")

        self.txtSuggestion.setText(result.suggestion)

def run() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = QtGui()
    window.show()
    sys.exit(app.exec())