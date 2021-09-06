import argparse
import datetime
import sys
from string import Template

import requests
from PyQt5.QtGui import QFontDatabase, QFont

import config
from model import DeadlineGeneratorModel, intervalRun
from controller import DeadlineGeneratorController
from database import DatabaseManager, ConnectionException
from view import DeadlineGeneratorUI
from PyQt5.QtWidgets import QApplication, QMessageBox
from termcolor import colored


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', choices=['synctg'],
                        help='execute command in application using cli')
    return parser.parse_args()


def main():
    try:
        potentialConnectionException = None
        dbManager = DatabaseManager()
    except ConnectionException as ce:
        potentialConnectionException = ce

    args = getArgs()
    if args.command is None:
        gui(potentialConnectionException)
    else:
        cli(potentialConnectionException, args.command)


def gui(potentialConnectionException):
    app = QApplication(sys.argv)
    with open(config.qssPath) as styles:
        stringStyles = Template(styles.read()).substitute(downArrowIcon=config.downArrowIconPath)
        app.setStyleSheet(stringStyles)
    QFontDatabase.addApplicationFont(config.mainFontPath)
    app.setFont(QFont("Apple 彩色表情符號"))

    if potentialConnectionException is not None:
        QMessageBox.critical(
            None,
            "Deadline Generator",
            f'Database Error: {potentialConnectionException}',
        )
        sys.exit(1)

    view = DeadlineGeneratorUI()
    model = DeadlineGeneratorModel()
    DeadlineGeneratorController(model=model, view=view)

    view.show()
    sys.exit(app.exec_())


def cli(potentialConnectionException, command):
    if potentialConnectionException is not None:
        print(f'Database Error: {potentialConnectionException}')
        sys.exit(1)

    model = DeadlineGeneratorModel()
    commandToFunction = {'synctg': synctgCommand}

    try:
        commandToFunction[command](model)
    except requests.exceptions.ConnectionError as ce:
        print(colored(ce, 'red'))
        print(colored(f'Timestamp: {datetime.datetime.now().strftime(config.datetimeFormat)}', 'red'), end='\n\n')


@intervalRun()
def synctgCommand(model):
    model.synchronizeWithTelegraph()


if __name__ == '__main__':
    main()
