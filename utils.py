import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QPainter

import config


def existsWidgetInLayout(widget, layout):
    for i in range(layout.count()):
        if widget is layout.itemAt(i).widget():
            return True
    return False


def existsLayoutInLayout(layout, parentLayout):
    for i in range(parentLayout.count()):
        if layout is parentLayout.itemAt(i).layout():
            return True
    return False


def widgetItemIndexInLayout(widget, layout):
    for i in range(layout.count()):
        if widget is layout.itemAt(i).widget():
            return i
    return -1


def widgetItemIndexInLayout(layout, parentLayout):
    for i in range(parentLayout.count()):
        if layout is parentLayout.itemAt(i).layout():
            return i
    return -1


def setTextToLabel(label, text):
    metrix = QFontMetrics(label.font())
    width = label.width()
    clippedText = metrix.elidedText(text, Qt.ElideRight, width)
    label.setText(clippedText)


def isDateActive(dateString):
    return (
            dateString == '' or
            getDateFromString(dateString) >=
            datetime.datetime.now().date()
    )


def getDateFromString(dateString):
    return datetime.datetime.strptime(dateString, config.dateFormat).date()


def getDatetimeFromString(dateString):
    return datetime.datetime.strptime(dateString, config.dateFormat)
