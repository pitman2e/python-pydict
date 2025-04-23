import sys
import pyperclip
import traceback
from typing import List

from PyQt6.QtGui import QKeyEvent

from pydict import da_jp, yahoo_dict
import os
from PyQt6 import QtCore, QtWidgets
from pydict.dict_result import DictResult
from pydict.logger import Logger
from enum import Enum

from pydict.ui.main_ui import Ui_mainWindow

UiFileDir: str = os.path.dirname(os.path.dirname(__file__))
UriFilePath: str = os.path.join(UiFileDir, "pydict", "ui", "dict.ui")

class DefinitionViewMode(Enum):
    DEFAULT = 0
    TC = 1
    RAW = 2

class QtGui(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        
        Logger.set_log_widget(self.ui.lstLog)

        self.definition_view_mode = DefinitionViewMode.DEFAULT

        self.ui.btnCheck.clicked.connect(self.btn_check_clicked)
        self.ui.btnCheckNext.clicked.connect(self.btn_check_next_clicked)
        self.ui.btnToggleRaw.clicked.connect(self.btn_toggle_raw_clicked)
        self.ui.lstHistory.currentItemChanged.connect(self.lst_history_current_item_changed)

        self.ui.cbbTranType.addItem("EN")
        self.ui.cbbTranType.addItem("JP")
        self.current_lang = self.ui.cbbTranType.currentText()

        self.dict_result_hist = {
            "EN": {},
            "JP": {},
        }
        self.dict_result_hist_cur_lang = self.dict_result_hist[self.current_lang]

        self.ui.btnCopyResult.clicked.connect(lambda: pyperclip.copy(self.ui.txtResult.toPlainText()))
        self.ui.btnCopyWord.clicked.connect(lambda: pyperclip.copy(self.ui.txtWord.text()))
        # self.txtResult.installEventFilter(self) # No longer needed since copy function exists, keep for ref
        self.ui.txtWord2Check.installEventFilter(self)
        self.ui.cbbTranType.currentTextChanged.connect(self.cbb_tran_type_current_text_changed)
        self.ui.txtWord2Check.setFocus()

        Logger.log("Program initialised")

    # Do not modify function name, meant to override
    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if source is self.ui.txtWord2Check:
            if event.type() == QtCore.QEvent.Type.KeyPress:
                event: QKeyEvent
                if (event.modifiers() == QtCore.Qt.Modifier.SHIFT) or not self.ui.cbxIsMultiline.isChecked():
                    if (event.key() == QtCore.Qt.Key.Key_Enter) or (event.key() == QtCore.Qt.Key.Key_Return):
                        self.btn_check_clicked()
                        return True
            if event.type() == QtCore.QEvent.Type.FocusIn:
                if not self.ui.cbxIsMultiline.isChecked():
                    if len(self.ui.txtWord2Check.toPlainText()) > 0: #If selectAll at empty box => cursor not appearing
                        # https://www.qtcentre.org/threads/31705-selectAll-in-QLineEdit-does-not-work?p=277477#post277477
                        # Workaround mouse click cancels selectAll()
                        QtCore.QTimer.singleShot(0, lambda: self.ui.txtWord2Check.selectAll())
                        return True
                    
        return False


    def cbb_tran_type_current_text_changed(self) -> None:
        self.current_lang = self.ui.cbbTranType.currentText()
        self.dict_result_hist_cur_lang = self.dict_result_hist[self.current_lang]
        self.ui.lstHistory.currentItemChanged.disconnect(self.lst_history_current_item_changed)
        self.ui.lstHistory.clear()
        for k in self.dict_result_hist[self.current_lang].keys():
            self.ui.lstHistory.insertItem(0, k)
        self.ui.lstHistory.currentItemChanged.connect(self.lst_history_current_item_changed)

    
    def lst_history_current_item_changed(self, current: QtWidgets.QListWidgetItem, prev: QtWidgets.QListWidgetItem) -> None:
        word_to_change: str = current.text()
        word_to_check: str = self.ui.txtWord2Check.toPlainText()
        words_2_check: List[str] = word_to_check.split("\n")

        if self.ui.cbxIsMultiline.isChecked():
            if word_to_change in words_2_check:
                words_2_check.remove(word_to_change)
            self.ui.txtWord2Check.setText(word_to_change + "\n" + "\n".join(words_2_check))
        else:
            self.ui.txtWord2Check.setText(word_to_change)
        
        if word_to_change in self.dict_result_hist_cur_lang:
            self.ui.txtResult.setText(self.dict_result_hist_cur_lang[word_to_change].definition)
            self.ui.txtSuggestion.setText("")
            self.ui.txtWord.setText("")

    # Do not modify function name, meant to override
    def closeEvent(self, event) -> None:
        pass

    def btn_check_clicked(self) -> None:
        new_item = QtWidgets.QListWidgetItem()
        new_item_text = self.ui.txtWord2Check.toPlainText()
        new_item.setText(new_item_text)

        if new_item_text not in self.dict_result_hist_cur_lang:
            self.ui.lstHistory.insertItem(0, new_item)
            self.get_dictionary_result(self.ui.txtWord2Check.toPlainText())
        else:
            self.definition_view_mode = DefinitionViewMode.DEFAULT
            self.apply_ui_dict_result(self.dict_result_hist_cur_lang[new_item_text])

    def btn_check_next_clicked(self) -> None:
        words = self.ui.txtWord2Check.toPlainText().split("\n")
        if self.ui.txtWord.text() == words[0]:
            if len(words) > 1:
                self.ui.txtWord2Check.setText("\n".join(words[1:]))
                self.get_dictionary_result(words[1])
        else:
            self.get_dictionary_result(words[0])

    def btn_toggle_raw_clicked(self) -> None:
        self.definition_view_mode = DefinitionViewMode((self.definition_view_mode.value + 1) % len(DefinitionViewMode))
        self.apply_ui_dict_result(self.dict_result)


    def get_dictionary_result(self, word2search: str) -> None:
        self.ui.btnCheck.setDisabled(True)

        try:

            if self.ui.cbbTranType.currentText() == "JP":
                result = da_jp.get_dictionary_result(word2search)
            elif self.ui.cbbTranType.currentText() == "EN":
                result = yahoo_dict.check_en_zh(word2search)
            else:
                raise Exception("Unrecognised Dictionary Type")

            if result.is_success:
                self.definition_view_mode = DefinitionViewMode.DEFAULT

            self.apply_ui_dict_result(result)
            self.dict_result_hist_cur_lang[result.word] = result
            self.dict_result = result

        except Exception:
            self.ui.txtResult.setText("An error has occurred: \n" + traceback.format_exc())
        finally:
            self.ui.btnCheck.setDisabled(False)

    def apply_ui_dict_result(self, result: DictResult):
        if result.is_success:
            self.ui.txtWord.setText(result.word)
            if self.definition_view_mode == DefinitionViewMode.DEFAULT:
                self.ui.txtResult.setText(result.definition)
                self.ui.btnToggleRaw.setText("Toggle Raw(DF)")
            elif self.definition_view_mode == DefinitionViewMode.TC:
                self.ui.txtResult.setText(result.definition_tc)
                self.ui.btnToggleRaw.setText("Toggle Raw(TC)")
            elif self.definition_view_mode == DefinitionViewMode.RAW:
                self.ui.txtResult.setText(result.definition_raw)
                self.ui.btnToggleRaw.setText("Toggle Raw(RW)")

            self.ui.lblStatus.setText("")
        else:
            self.ui.lblStatus.setText("Word definition not found")

        self.ui.txtSuggestion.setText(result.suggestion)

def run() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = QtGui()
    window.show()
    sys.exit(app.exec())