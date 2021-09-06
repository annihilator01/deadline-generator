import webbrowser
from functools import partial

import requests
from PyQt5.QtCore import Qt, QCoreApplication, QEventLoop, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QMessageBox, QApplication

import config
import utils
from view import SubjectForm, Subject, DeadlineForm, DeadlineItem, Deadline


class DeadlineGeneratorController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self._fillViewWithDBData()
        self._connectActionsButtons()
        self._connectSubjectsButtons()

    def _fillViewWithDBData(self):
        subjects = self.model.fetchSubjectsData()
        self.view.loadSubjectsUI(subjects)

    def _showForm(self, FormType, formModeLabel, saveActionFunction, **kwargs):
        formObject = kwargs.get('formObject', None)

        form = FormType()
        form.formModeLabel.setText(formModeLabel)
        form.fillData(formObject)
        form.saveButton.clicked.connect(partial(saveActionFunction, form, **kwargs))
        form.exec()

    def _connectActionsButtons(self):
        self.view.addSubjectButton.clicked.connect(
            partial(
                self._showForm,
                FormType=SubjectForm,
                formModeLabel='Add Subject Form',
                saveActionFunction=self._onAddSubjectSaveAction
            ))
        self.view.sortDeadlinesButton.clicked.connect(self._onSortDeadlines)
        self.view.telegraphSynchronizationButton.clicked.connect(self._onTelegraphSynchronization)

    def _onAddSubjectSaveAction(self, subjectForm, **kwargs):
        subjectName = subjectForm.nameLine.text().strip()
        subjectEmoji = subjectForm.emojiLine.text().strip()

        if not subjectName:
            QMessageBox.warning(
                subjectForm,
                'Subject Form',
                'Name of subject is not given!'
            )
            return

        if not subjectEmoji:
            subjectEmoji = config.defaultSubjectEmoji

        newSubjectId = self.model.insertSubject(subjectName, subjectEmoji)
        newSubject = Subject(newSubjectId, subjectName, subjectEmoji)
        self._connectSubjectButtons(newSubject)

        self.view.subjectsScrollArea.verticalScrollBar().rangeChanged.connect(
            partial(
                self._onAddSubjectScrollBarMove,
                self.view.subjectsScrollArea.verticalScrollBar()
            ))

        self.view.subjectsLayout.addWidget(newSubject)
        self.view.updateSubjectsShow()
        subjectForm.close()

    def _onAddSubjectScrollBarMove(self, scrollBar):
        scrollBar.setValue(scrollBar.maximum())
        scrollBar.rangeChanged.disconnect()

    def _onSortDeadlines(self):
        self.view.clearSubjectsLayout()
        self._fillViewWithDBData()
        self._connectSubjectsButtons()

    def _onTelegraphSynchronization(self):
        try:
            self.model.synchronizeWithTelegraph()
        except requests.exceptions.ConnectionError:
            QMessageBox.warning(
                None,
                'Telegraph Synchronization',
                config.telegraphCannotSynchronizeMessage
            )

    def _connectSubjectsButtons(self):
        for subject in self.view.subjectsFrame.findChildren(Subject):
            self._connectSubjectButtons(subject)
            for deadline in subject.deadlinesFrame.findChildren(Deadline):
                self._connectDeadlineButtons(deadline, subject)

    def _connectSubjectButtons(self, subject):
        subject.addDeadlineAction.triggered.connect(
            partial(
                self._showForm,
                FormType=DeadlineForm,
                formModeLabel='Add Deadline Form',
                saveActionFunction=self._onAddDeadlineSaveAction,
                subject=subject
            ))
        subject.editSubjectNameAction.triggered.connect(
            partial(
                self._showForm,
                FormType=SubjectForm,
                formModeLabel='Edit Subject Form',
                saveActionFunction=self._onEditSubjectSaveAction,
                formObject=subject
            ))
        subject.mouseDoubleClickEvent = lambda e: subject.editSubjectNameAction.triggered.emit()
        subject.deleteSubjectAction.triggered.connect(
            partial(
                self._onDelete,
                dataObject=subject,
                deleteFrom=self.view,
                question=f'Are you sure to delete "<span style="font-weight: bold; font-style: italic;">{subject.subjectName}</span>" subject?',
                table=config.subjectTable
            ))

    def _connectDeadlineButtons(self, deadline, subject):
        deadline.editDeadlineAction.triggered.connect(
            partial(
                self._showForm,
                FormType=DeadlineForm,
                formModeLabel='Edit Deadline Form',
                saveActionFunction=self._onEditDeadlineSaveAction,
                formObject=deadline
            )
        )
        deadline.mouseDoubleClickEvent = lambda e: deadline.editDeadlineAction.triggered.emit()
        deadline.deleteDeadlineAction.triggered.connect(
            partial(
                self._onDelete,
                dataObject=deadline,
                deleteFrom=subject,
                question=f'Are you sure to delete "<span style="font-weight: bold; font-style: italic;">{deadline.name}</span>" deadline?',
                table=config.deadlineTable
            )
        )

    def _onEditSubjectSaveAction(self, subjectForm, **kwargs):
        subject = kwargs['formObject']

        subjectName = subjectForm.nameLine.text().strip()
        subjectEmoji = subjectForm.emojiLine.text().strip()

        if not subjectName:
            QMessageBox.warning(
                subjectForm,
                'Subject Form',
                'Name of subject is not given!'
            )
            return

        if not subjectEmoji:
            subjectEmoji = config.defaultSubjectEmoji

        self.model.updateSubject(subject.id_, subjectName, subjectEmoji)
        subject.subjectName = subjectName
        subject.subjectEmoji = subjectEmoji
        subject.updateLabel()
        subjectForm.close()

    def _onDelete(self, dataObject, deleteFrom, question, table):
        answer = QMessageBox.question(
            None,
            'Delete Question',
            question,
            QMessageBox.Yes | QMessageBox.No
        )

        if answer == QMessageBox.Yes:
            self.model.deleteObject(dataObject.id_, table)
            deleteFrom.remove(dataObject)
            self.view.adjustScrollArea()

    def _onAddDeadlineSaveAction(self, deadlineForm, **kwargs):
        subject = kwargs['subject']

        isDeadlineDateUseless = deadlineForm.isDateUselessCheckBox.isChecked()
        deadlineDate = '' if isDeadlineDateUseless else deadlineForm.dateWidget.text().strip()
        deadlineName = deadlineForm.nameLine.text().strip()
        deadlineLink = deadlineForm.linkLine.text().strip()

        if not deadlineName:
            QMessageBox.warning(
                deadlineForm,
                'Deadline Form',
                'Name of deadline is not given!'
            )
            return

        newDeadlineId = self.model.insertDeadline(subject.id_, deadlineDate, deadlineName, deadlineLink)
        newDeadline = Deadline(
            newDeadlineId,
            deadlineDate,
            deadlineName,
            deadlineLink,
            utils.isDateActive(deadlineDate)
        )
        self._connectDeadlineButtons(newDeadline, subject)
        subject.deadlinesLayout.addWidget(newDeadline)
        subject.updateDeadlinesShow()
        self.view.adjustScrollArea()
        deadlineForm.close()

    def _onEditDeadlineSaveAction(self, deadlineForm, **kwargs):
        deadline = kwargs['formObject']

        date = '' if deadlineForm.isDateUselessCheckBox.isChecked() else deadlineForm.dateWidget.text()
        name = deadlineForm.nameLine.text()
        link = deadlineForm.linkLine.text()

        if not name:
            QMessageBox.warning(
                deadlineForm,
                'Deadline Form',
                'Name of deadline is not given!'
            )
            return

        self.model.updateDeadline(deadline.id_, date, name, link)
        deadline.date = date
        deadline.name = name
        deadline.link = link
        deadline.updateLabels()
        deadlineForm.close()
