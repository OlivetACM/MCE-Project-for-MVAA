import sqlite3


class Reviewer:

    def __init__(self, database, name):
        # Establish connection to the database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        self.name = name
        self.phone = ''.join(curs.execute('select ReviewerPhone from Reviewer where ReviewerName=?',
                                          (name,)).fetchone())
        self.email = ''.join(curs.execute('select ReviewerEmail from Reviewer where ReviewerName=?',
                                          (name,)).fetchone())
        self.department = ''.join(curs.execute('select ReviewerDepartment from Reviewer where ReviewerName=?',
                                               (name,)).fetchone())
