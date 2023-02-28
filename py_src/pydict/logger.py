from PyQt6 import QtWidgets

class logger:
    __lstLog: QtWidgets.QListWidget = None

    @staticmethod
    def set_log_widget(log_widget: QtWidgets.QListView) -> None:
        logger.__lstLog = log_widget

    @staticmethod
    def log(msg: str) -> None:
        if logger.__lstLog is not None:
            logger.__lstLog.addItem(msg)