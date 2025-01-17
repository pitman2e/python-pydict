from PyQt6 import QtWidgets

class Logger:
    __lstLog: QtWidgets.QListWidget = None

    @staticmethod
    def set_log_widget(log_widget: QtWidgets.QListView) -> None:
        Logger.__lstLog = log_widget

    @staticmethod
    def log(msg: str) -> None:
        if Logger.__lstLog is not None:
            Logger.__lstLog.addItem(msg)