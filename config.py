import os

dirname = os.path.dirname(__file__)

# Mode
isProdMode = True

# Files paths
sqliteDBPath = os.path.join(dirname, 'db/deadlines.sqlite') if isProdMode else os.path.join(dirname, 'db/testdb.sqlite')
qssPath = os.path.join(dirname, 'styles.qss')
mainFontPath = os.path.join(dirname, 'fonts/EmojiOneFont.ttf')
addIconPath = os.path.join(dirname, 'icons/add.svg')
deleteIconPath = os.path.join(dirname, 'icons/delete.svg')
downArrowIconPath = os.path.join(dirname, 'icons/down_arrow.svg')
editIconPath = os.path.join(dirname, 'icons/edit.svg')
sortIconPath = os.path.join(dirname, 'icons/sort.svg')
synchronizationIconPath = os.path.join(dirname, 'icons/synchronization.svg')

# Subject table
subjectTable = 'subjects'
subjectNameColumn = 'name'
subjectEmojiColumn = 'emoji'

# Deadline table
deadlineTable = 'deadlines'
deadlineNameColumn = 'name'
deadlineLinkColumn = 'link'
deadlineDateColumn = 'date'
deadlineSubjectColumn = 'subject_id'

# Emojis
defaultSubjectEmoji = '🎓'
deadlineOKEmoji = '✅'
deadlineBadEmoji = '❌'

# Date Format
dateFormat = '%d.%m.%Y'
datetimeFormat = '%d.%m.%Y %H:%M:%S'

# Telegraph
telegraphToken = '6b1c87313f9ef6625fe894a787731a8cbf5fc30eace0bc290dcb523256f4'
telegraphPage = 'Dedlajny-02-07' if isProdMode else ''
telegraphPageTitle = 'Дедлайны'
telegraphDeadlinePictureTag = {'tag': 'figure', 'children': [{'tag': 'img', 'attrs': {'src': '/file/34dd8a8e8485f072ffdf2.png'}}, {'tag': 'figcaption'}]}
telegraphNoDeadlinesTag = {'tag': 'p', 'children': [{'tag': 'em', 'children': ['Пока дедлайнов нет']}]}
telegraphLineBreakerTag = {'tag': 'p', 'children': [{'tag': 'br'}]}
telegraphCannotSynchronizeMessage = 'Cannot synchronize with Telegraph.\nCheck your Internet connection!'
