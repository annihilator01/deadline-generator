import webbrowser
from functools import partial

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QCursor
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QToolButton, QMenu, QAction, QSizePolicy, QLayout, QWidget, \
    QMainWindow, QPushButton, QDialog, QMessageBox, QFrame, QDateEdit, QCheckBox, QScrollArea, QAbstractScrollArea, \
    QApplication
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout

import config
import utils


EMPTY_STRING = 'empty'


class DeadlineItem(QFrame):
    def __init__(self, itemType, value=''):
        super(DeadlineItem, self).__init__()

        self.mainLayout = QVBoxLayout()
        self.itemTypeLabel = QLabel(itemType)
        self.itemTypeLabel.setObjectName('description')
        self.infoLabel = QLabel()
        self.infoLabel.setObjectName('info-label')
        self.setDeadlineItemText(value)
        self.mainLayout.addWidget(self.itemTypeLabel)
        self.mainLayout.addWidget(self.infoLabel)
        self.setLayout(self.mainLayout)

    def setDeadlineItemText(self, text):
        if not text:
            text = EMPTY_STRING
            self.infoLabel.setStyleSheet('color: #636363; font-style: italic;')
        else:
            self.infoLabel.setStyleSheet('')
        self.infoLabel.setText(text)


class Deadline(QFrame):
    def __init__(self, id_, date, name, link, isActive):
        super(Deadline, self).__init__()
        self.deadlineLayout = QHBoxLayout()
        self.setLayout(self.deadlineLayout)

        self.id_ = id_
        self.date = date
        self.name = name
        self.link = link
        self.isActiveFrame = DeadlineItem('IS ACTIVE')
        self.isActiveFrame.setObjectName('is-active')
        self.isActiveFrame.infoLabel.setAlignment(Qt.AlignCenter)
        self.dateFrame = DeadlineItem('DATE')
        self.dateFrame.setObjectName('date')
        self.dateFrame.infoLabel.setAlignment(Qt.AlignCenter)
        self.nameFrame = DeadlineItem('NAME')
        self.nameFrame.setObjectName('name')
        self.linkFrame = DeadlineItem('LINK')
        self.linkFrame.setObjectName('link')
        self.deadlineLayout.addWidget(self.isActiveFrame)
        self.deadlineLayout.addWidget(self.dateFrame)
        self.deadlineLayout.addWidget(self.nameFrame)
        self.deadlineLayout.addWidget(self.linkFrame)
        self.deadlineLayout.setContentsMargins(0, 0, 0, 0)

        self.updateLabels()
        self._initToolButton()

    def updateLabels(self):
        self.isActiveFrame.setDeadlineItemText(config.deadlineOKEmoji if utils.isDateActive(self.date) else config.deadlineBadEmoji)
        self.dateFrame.setDeadlineItemText(self.date)
        self.nameFrame.setDeadlineItemText(self.name)
        self.linkFrame.setDeadlineItemText(self._getShorterLink(self.link))

        if self.link:
            self.linkFrame.infoLabel.mouseReleaseEvent = partial(self._onOpenLink, self.link)
            self.linkFrame.infoLabel.enterEvent = lambda e: self.linkFrame.infoLabel.setStyleSheet(
                'text-decoration: underline')
            self.linkFrame.infoLabel.leaveEvent = lambda e: self.linkFrame.infoLabel.setStyleSheet('')
            self.linkFrame.infoLabel.setCursor(Qt.PointingHandCursor)
        else:
            self.linkFrame.infoLabel.mouseReleaseEvent = lambda e: None
            self.linkFrame.infoLabel.enterEvent = lambda e: None
            self.linkFrame.infoLabel.leaveEvent = lambda e: None
            self.linkFrame.infoLabel.setCursor(Qt.ArrowCursor)

    def _getShorterLink(self, stringLink):
        shorterLink = stringLink.replace('https://', '', 1)
        shorterLink = shorterLink.replace('http://', '', 1)
        return shorterLink

    def _onOpenLink(self, link, event):
        webbrowser.open(link)

    def _initToolButton(self):
        toolButton = QToolButton()
        toolButton.setObjectName('deadline')
        menu = QMenu()
        self.editDeadlineAction = QAction('Edit deadline', self)
        self.deleteDeadlineAction = QAction('Delete deadline', self)
        self.editDeadlineAction.setIcon(QIcon(config.editIconPath))
        self.deleteDeadlineAction.setIcon(QIcon(config.deleteIconPath))
        menu.addActions([self.editDeadlineAction, self.deleteDeadlineAction])
        toolButton.setMenu(menu)
        toolButton.setPopupMode(QToolButton.InstantPopup)
        self.deadlineLayout.addWidget(toolButton)


class Subject(QFrame):
    def __init__(self,
                 id_,
                 subjectName,
                 subjectEmoji=''):
        super(Subject, self).__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.subjectLayout = QVBoxLayout()
        self.setLayout(self.subjectLayout)

        self.id_ = id_
        self.subjectName = subjectName
        self.subjectEmoji = subjectEmoji

        self._initHeader()
        self.deadlinesFrame = QFrame()
        self.deadlinesLayout = QVBoxLayout()
        self.deadlinesLayout.setContentsMargins(0, 0, 0, 0)
        self.deadlinesFrame.setLayout(self.deadlinesLayout)
        self.subjectLayout.addWidget(self.deadlinesFrame)

        self.noDeadlinesLabel = QLabel('No deadlines for this subject yet.')
        self.subjectLayout.addWidget(self.noDeadlinesLabel)
        self.subjectLayout.setSpacing(10)
        self.subjectLayout.setContentsMargins(0, 0, 0, 0)

    def _initHeader(self):
        self.label = QLabel()
        self.label.setObjectName('subject-name')
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.updateLabel()
        self.toolButton = QToolButton()
        self.toolButton.setObjectName('subject')
        menu = QMenu()
        self.addDeadlineAction = QAction('Add new deadline', self)
        self.editSubjectNameAction = QAction('Edit subject name', self)
        self.deleteSubjectAction = QAction('Delete subject', self)
        self.addDeadlineAction.setIcon(QIcon(config.addIconPath))
        self.editSubjectNameAction.setIcon(QIcon(config.editIconPath))
        self.deleteSubjectAction.setIcon(QIcon(config.deleteIconPath))
        menu.addActions([self.addDeadlineAction, self.editSubjectNameAction, self.deleteSubjectAction])
        self.toolButton.setMenu(menu)
        self.toolButton.setPopupMode(QToolButton.InstantPopup)

        self.headerLayout = QHBoxLayout()
        self.headerLayout.addWidget(self.label)
        self.headerLayout.addWidget(self.toolButton)
        self.headerLayout.setAlignment(self.toolButton, Qt.AlignLeft)
        self.headerLayout.setSpacing(15)
        self.subjectLayout.addLayout(self.headerLayout)

    def updateLabel(self):
        if self.subjectEmoji:
            labelText = f'{self.subjectEmoji} {self.subjectName}'
        else:
            labelText = f'{self.subjectName}'
        self.label.setText(labelText)

    def updateDeadlinesShow(self):
        if self.deadlinesLayout.count():
            self.noDeadlinesLabel.hide()
            self.deadlinesFrame.show()
        else:
            self.deadlinesFrame.hide()
            self.noDeadlinesLabel.show()

    def addDeadline(self, deadline):
        self.deadlinesLayout.addWidget(deadline)
        self.updateDeadlinesShow()

    def remove(self, deadline):
        self.removeDeadline(deadline)

    def removeDeadline(self, deadline):
        self.deadlinesLayout.removeWidget(deadline)
        deadline.deleteLater()
        self.updateDeadlinesShow()


class Form(QDialog):
    def __init__(self, parent):
        super(Form, self).__init__(parent)
        self.mainLayout = QVBoxLayout()
        self.formModeLabel = QLabel()
        self.formModeLabel.setObjectName('form-mode-label')
        self.dataLayout = QVBoxLayout()
        self.saveButton = QPushButton('SAVE')
        self.mainLayout.addWidget(self.formModeLabel)
        self.mainLayout.setAlignment(self.formModeLabel, Qt.AlignHCenter)
        self.mainLayout.addLayout(self.dataLayout)
        self.mainLayout.addWidget(self.saveButton)
        self.setLayout(self.mainLayout)

    def fillData(self, *args, **kwargs):
        pass


class SubjectForm(Form):
    def __init__(self, parent=None):
        super(SubjectForm, self).__init__(parent)
        self.setWindowTitle('Subject Form')
        emojiLayout = QVBoxLayout()
        emojiLabel = QLabel('EMOJI')
        emojiLabel.setObjectName('description')
        self.emojiLine = QLineEdit()
        emojiLayout.addWidget(emojiLabel)
        emojiLayout.addWidget(self.emojiLine)
        nameLayout = QVBoxLayout()
        nameLabel = QLabel('NAME')
        nameLabel.setObjectName('description')
        self.nameLine = QLineEdit()
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameLine)
        self.dataLayout.addLayout(emojiLayout)
        self.dataLayout.addLayout(nameLayout)

    def fillData(self, subject):
        if subject is None:
            return
        self.nameLine.setText(subject.subjectName)
        self.emojiLine.setText(subject.subjectEmoji)


class DeadlineForm(Form):
    def __init__(self, parent=None):
        super(DeadlineForm, self).__init__(parent)
        self.setWindowTitle('Deadline Form')
        dateLayout = QVBoxLayout()
        dateLabel = QLabel('DATE')
        dateLabel.setObjectName('description')
        dateCheckboxLayout = QHBoxLayout()
        self.dateWidget = QDateEdit()
        self.dateWidget.setCalendarPopup(True)
        self.dateWidget.setDate(QtCore.QDate.currentDate())
        self.isDateUselessCheckBox = QCheckBox('Date Useless')
        dateCheckboxLayout.addWidget(self.dateWidget)
        dateCheckboxLayout.addWidget(self.isDateUselessCheckBox)
        dateLayout.addWidget(dateLabel)
        dateLayout.addLayout(dateCheckboxLayout)
        nameLayout = QVBoxLayout()
        nameLabel = QLabel('NAME')
        nameLabel.setObjectName('description')
        self.nameLine = QLineEdit()
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameLine)
        linkLayout = QVBoxLayout()
        linkLabel = QLabel('LINK')
        linkLabel.setObjectName('description')
        self.linkLine = QLineEdit()
        linkLayout.addWidget(linkLabel)
        linkLayout.addWidget(self.linkLine)
        self.dataLayout.addLayout(dateLayout)
        self.dataLayout.addLayout(nameLayout)
        self.dataLayout.addLayout(linkLayout)

        self._connectCheckBox()

    def fillData(self, deadline):
        if deadline is None:
            return

        if deadline.date:
            self.dateWidget.setDate(QtCore.QDate.fromString(deadline.date, 'dd.MM.yyyy'))
        else:
            self.dateWidget.setEnabled(False)
            self.isDateUselessCheckBox.setCheckState(Qt.Checked)
        self.nameLine.setText(deadline.name)
        self.linkLine.setText(deadline.link)

    def _connectCheckBox(self):
        self.isDateUselessCheckBox.stateChanged.connect(self._onCheckBoxStateChanged)

    def _onCheckBoxStateChanged(self):
        self.dateWidget.setEnabled(not self.isDateUselessCheckBox.isChecked())


class DeadlineGeneratorUI(QMainWindow):
    def __init__(self):
        super(DeadlineGeneratorUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Deadline Generator')

        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        actionsSectionLabel = QLabel('Actions')
        actionsSectionLabel.setObjectName('action-section')
        self.mainLayout.addWidget(actionsSectionLabel)
        self.mainLayout.setAlignment(actionsSectionLabel, Qt.AlignHCenter)

        self.headerLayout = QHBoxLayout()
        self.addSubjectButton = QPushButton('Add new subject')
        self.addSubjectButton.setObjectName('action')
        self.addSubjectButton.setIcon(QIcon(config.addIconPath))
        self.sortDeadlinesButton = QPushButton('Sort deadlines')
        self.sortDeadlinesButton.setObjectName('action')
        self.sortDeadlinesButton.setIcon(QIcon(config.sortIconPath))
        self.telegraphSynchronizationButton = QPushButton('Synchronize with Telegraph')
        self.telegraphSynchronizationButton.setObjectName('action')
        self.telegraphSynchronizationButton.setIcon(QIcon(config.synchronizationIconPath))
        self.headerLayout.addWidget(self.addSubjectButton)
        self.headerLayout.addWidget(self.sortDeadlinesButton)
        self.headerLayout.addWidget(self.telegraphSynchronizationButton)
        self.mainLayout.addLayout(self.headerLayout)

        subjectSectionLabel = QLabel('Subjects')
        subjectSectionLabel.setObjectName('subject-section')
        self.mainLayout.addWidget(subjectSectionLabel)
        self.mainLayout.setAlignment(subjectSectionLabel, Qt.AlignHCenter)

        self.subjectsFrame = QFrame()
        self.subjectsLayout = QVBoxLayout()
        self.subjectsLayout.setSpacing(30)
        self.subjectsFrame.setObjectName('subjects-frame')
        self.subjectsLayout.setContentsMargins(0, 0, 0, 0)
        self.subjectsFrame.setLayout(self.subjectsLayout)

        self.subjectsScrollArea = QScrollArea()
        self.subjectsScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.subjectsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.subjectsScrollArea.setWidgetResizable(True)
        self.subjectsScrollArea.setWidget(self.subjectsFrame)
        self.mainLayout.addWidget(self.subjectsScrollArea)

        self.noSubjectsLabel = QLabel('No subjects in generator yet.')
        self.mainLayout.addWidget(self.noSubjectsLabel)

    def loadSubjectsUI(self, subjects):
        for subject in subjects:
            subjectUI = Subject(
                subject['id'],
                subject[f'{config.subjectNameColumn}'],
                subject[f'{config.subjectEmojiColumn}']
            )
            for deadline in subject['deadlines']:
                deadlineUI = Deadline(
                    deadline['id'],
                    deadline[f'{config.deadlineDateColumn}'],
                    deadline[f'{config.deadlineNameColumn}'],
                    deadline[f'{config.deadlineLinkColumn}'],
                    deadline['isActive']
                )
                subjectUI.addDeadline(deadlineUI)
            self.subjectsLayout.addWidget(subjectUI)
        self.updateSubjectsShow()

    def adjustScrollArea(self):
        QTimer.singleShot(1, self._adjustScrollArea)

    def _adjustScrollArea(self):
        QtWidgets.qApp.processEvents()
        step = 5
        if self.subjectsScrollArea.verticalScrollBar().isVisible():
            while self.subjectsScrollArea.verticalScrollBar().isVisible() and self.height() < self.maximumHeight():
                self.resize(self.width(), self.height() + step)
        else:
            while not self.subjectsScrollArea.verticalScrollBar().isVisible() and self.height() > self.minimumHeight():
                self.resize(self.width(), self.height() - step)
            if self.subjectsScrollArea.verticalScrollBar().isVisible():
                self.resize(self.width(), self.height() + step)

    def remove(self, subject):
        self.subjectsLayout.removeWidget(subject)
        subject.deleteLater()
        self.updateSubjectsShow()

    def clearSubjectsLayout(self):
        for subject in self.subjectsFrame.findChildren(Subject):
            self.remove(subject)

    def updateSubjectsShow(self):
        if self.subjectsLayout.count():
            self.noSubjectsLabel.hide()
            self.subjectsScrollArea.show()
        else:
            self.subjectsScrollArea.hide()
            self.noSubjectsLabel.show()

        self.adjustScrollArea()
