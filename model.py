import time
import datetime

import requests
import telegraph
import telegraph.utils

from functools import cmp_to_key
from PyQt5.QtSql import QSqlQuery

import config
import utils


def intervalRun(interval=90, times=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            for i in range(times):
                try:
                    result = func(*args, **kwargs)
                    break
                except requests.exceptions.ConnectionError:
                    if i == times - 1:
                        raise
                    time.sleep(interval)
            return result
        return wrapper
    return decorator


class DeadlineGeneratorModel:
    def __init__(self):
        self.telegraphApi = telegraph.Telegraph(config.telegraphToken)

    def fetchSubjectsData(self):
        subjects = []

        selectSubjectsQuery = QSqlQuery()
        selectSubjectsQuery.exec(
            f"""
            SELECT id, {config.subjectNameColumn}, {config.subjectEmojiColumn}
            FROM {config.subjectTable}
            """
        )
        while selectSubjectsQuery.next():
            subjectID = selectSubjectsQuery.value(0)
            subjectName = selectSubjectsQuery.value(1)
            subjectEmoji = selectSubjectsQuery.value(2)
            subject = {
                'id': subjectID,
                config.subjectNameColumn: subjectName,
                config.subjectEmojiColumn: subjectEmoji,
                'deadlines': []
            }

            selectDeadlinesQuery = QSqlQuery()
            selectDeadlinesQuery.exec(
                f"""
                SELECT id, {config.deadlineNameColumn}, {config.deadlineLinkColumn}, {config.deadlineDateColumn}
                FROM {config.deadlineTable}
                WHERE {config.deadlineSubjectColumn} = {subjectID}
                """
            )
            while selectDeadlinesQuery.next():
                deadlineID = selectDeadlinesQuery.value(0)
                deadlineName = selectDeadlinesQuery.value(1)
                deadlineLink = selectDeadlinesQuery.value(2)
                deadlineDate = selectDeadlinesQuery.value(3)
                deadline = {
                    'id': deadlineID,
                    config.deadlineNameColumn: deadlineName,
                    config.deadlineLinkColumn: deadlineLink,
                    config.deadlineDateColumn: deadlineDate,
                    'isActive': utils.isDateActive(deadlineDate)
                }

                subject['deadlines'].append(deadline)
            # subject['deadlines'].sort(key=lambda d: self._sortByDateKeyFunc(d['date']))
            subject['deadlines'].sort(key=cmp_to_key(self._dateCmp))

            selectDeadlinesQuery.finish()
            subjects.append(subject)

        selectSubjectsQuery.finish()

        # subjects.sort(key=lambda s: self._sortSubjectsByDateKeyFunc(s['deadlines']))
        subjects.sort(key=cmp_to_key(self._subjectDateCmp))
        return subjects

    def _dateCmp(self, deadline1, deadline2):
        date1 = deadline1[config.deadlineDateColumn]
        date2 = deadline2[config.deadlineDateColumn]
        if date1 == '':
            if utils.isDateActive(date2):
                return 1
            else:
                return -1
        elif utils.isDateActive(date1):
            if date2 == '' or not utils.isDateActive(date2) or utils.getDateFromString(date1) < utils.getDateFromString(date2):
                return -1
            else:
                return 1
        else:
            if date2 == '' or utils.isDateActive(date2) or utils.getDateFromString(date1) < utils.getDateFromString(date2):
                return 1
            else:
                return -1

    def _subjectDateCmp(self, subject1, subject2):
        deadlines1 = subject1['deadlines']
        deadlines2 = subject2['deadlines']
        if len(deadlines1) == 0:
            return 1
        elif len(deadlines2) == 0:
            return -1
        else:
            return self._dateCmp(deadlines1[0], deadlines2[0])


    def _sortByDateKeyFunc(self, date):
        if date == '':
            date = datetime.datetime.max - datetime.timedelta(days=1)
        else:
            date = datetime.datetime.strptime(date, config.dateFormat)
            if date.date() < datetime.datetime.now().date():
                deadlineExpired = date.date() - datetime.datetime.min.date()
                date = datetime.datetime.max - deadlineExpired
        return date

    def _sortSubjectsByDateKeyFunc(self, deadlines):
        if len(deadlines) == 0:
            date = datetime.datetime.max
        else:
            date = self._sortByDateKeyFunc(deadlines[0][config.deadlineDateColumn])
        return date

    def insertSubject(self, name, emoji):
        insertSubjectQuery = QSqlQuery()
        insertSubjectQuery.prepare(
            f"""
            INSERT INTO {config.subjectTable} (
                {config.subjectNameColumn},
                {config.subjectEmojiColumn}
            )
            VALUES (?, ?)
            """
        )
        insertSubjectQuery.addBindValue(name)
        insertSubjectQuery.addBindValue(emoji)
        insertSubjectQuery.exec()
        newSubjectID = insertSubjectQuery.lastInsertId()
        insertSubjectQuery.finish()
        return newSubjectID

    def updateSubject(self, id_, name, emoji):
        updateSubjectQuery = QSqlQuery()
        updateSubjectQuery.prepare(
            f"""
            UPDATE {config.subjectTable}
            SET {config.subjectNameColumn} = ?,
                {config.subjectEmojiColumn} = ?
            WHERE id = ?
            """
        )
        updateSubjectQuery.addBindValue(name)
        updateSubjectQuery.addBindValue(emoji)
        updateSubjectQuery.addBindValue(id_)
        updateSubjectQuery.exec()
        updateSubjectQuery.finish()

    def insertDeadline(self, subjectId, date, name, link):
        insertDeadlineQuery = QSqlQuery()
        insertDeadlineQuery.prepare(
            f"""
            INSERT INTO {config.deadlineTable} (
                {config.deadlineSubjectColumn},
                {config.deadlineDateColumn},
                {config.deadlineNameColumn},
                {config.deadlineLinkColumn}
            )
            VALUES (?, ?, ?, ?)
            """
        )
        insertDeadlineQuery.addBindValue(subjectId)
        insertDeadlineQuery.addBindValue(date)
        insertDeadlineQuery.addBindValue(name)
        insertDeadlineQuery.addBindValue(link)
        insertDeadlineQuery.exec()
        newDeadlineID = insertDeadlineQuery.lastInsertId()
        insertDeadlineQuery.finish()
        return newDeadlineID

    def updateDeadline(self, id_, date, name, link):
        updateDeadlineQuery = QSqlQuery()
        updateDeadlineQuery.prepare(
            f"""
            UPDATE {config.deadlineTable}
            SET {config.deadlineDateColumn} = ?,
                {config.deadlineNameColumn} = ?,
                {config.deadlineLinkColumn} = ?
            WHERE id = ?
            """
        )
        updateDeadlineQuery.addBindValue(date)
        updateDeadlineQuery.addBindValue(name)
        updateDeadlineQuery.addBindValue(link)
        updateDeadlineQuery.addBindValue(id_)
        updateDeadlineQuery.exec()
        updateDeadlineQuery.finish()

    def deleteObject(self, id_, table):
        deleteSubjectQuery = QSqlQuery()
        deleteSubjectQuery.prepare(
            f"""
            DELETE FROM {table}
            WHERE id = ?
            """
        )
        deleteSubjectQuery.addBindValue(id_)
        deleteSubjectQuery.exec()
        deleteSubjectQuery.finish()

    # @intervalRun(interval=10, times=3)
    def synchronizeWithTelegraph(self):
        subjects = self.fetchSubjectsData()
        page = [config.telegraphDeadlinePictureTag]
        for subject in subjects:
            subjectTag = self.getSubjectTag(subject)
            page.append(subjectTag)

            if subject['deadlines']:
                for deadline in subject['deadlines']:
                    deadlineTag = self.getDeadlineTag(deadline)
                    page.append(deadlineTag)
            else:
                page.append(config.telegraphNoDeadlinesTag)
            page.append(config.telegraphLineBreakerTag)
        page.append(self.getTimeTag())

        try:
            self.telegraphApi.edit_page(config.telegraphPage, config.telegraphPageTitle, content=page)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError(config.telegraphCannotSynchronizeMessage)

    def getSubjectTag(self, subject):
        subjectTitle = f'{subject[config.subjectEmojiColumn]} {subject[config.subjectNameColumn]}'
        return {'tag': 'h4', 'children': [subjectTitle]}

    def getDeadlineTag(self, deadline):
        datePrefix = f"""{config.deadlineOKEmoji if deadline['isActive'] else config.deadlineBadEmoji} """
        if deadline[config.deadlineDateColumn]:
            datePrefix += f"""{deadline[config.deadlineDateColumn]} - """
        return {
            'tag': 'p',
            'children': [
                datePrefix,
                {
                    'tag': 'a',
                    'attrs': {'href': deadline[config.deadlineLinkColumn], 'target': '_blank'},
                    'children': [{'tag': 'em', 'children': [deadline[config.deadlineNameColumn]]}]
                }
            ]
        }

    def getTimeTag(self):
        nowTime = datetime.datetime.now().strftime(config.datetimeFormat)
        return {
            'tag': 'p',
            'children': [
                {
                    'tag': 'strong',
                    'children': [
                        {
                            'tag': 'em',
                            'children': [f'обновлено: {nowTime}']
                        }
                    ]
                }
            ]
        }
