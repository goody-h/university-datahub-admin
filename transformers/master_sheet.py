import re
from transformers.table_mapper import TableMapper

class MasterSheet(TableMapper):
    def __init__(self, filename, courseCode='', session=''):
        super().__init__(
            filename, table_anchor='matric',
            row_check = {'match': '^[u,U]\d{4}/\d{7}$', 'key': 'mat_no'},
            column_map = [
                {'search': 'matric', 'key': 'mat_no'},
                {'search': '(total|score)', 'key': 'score'},
                {'search': 'delete', 'key': 'delete'},
            ],
            header_map = [{'search': 'session', 'exec': self.session_handler}, {'search': 'course (code|no)', 'exec': self.code_handler}]),
            
        self._courseId = courseCode
        self._session = session
        self._courseCode = courseCode

    def __modify_row__(self, row):
        row.update({
            'session': self.session, 'courseId': self.courseId,
            'courseCode': self.courseCode, 'mat_no': row['mat_no'].upper(),
            'resultId': self.getResultId(row['mat_no'].upper())
        })
        # TODO tests and sanitize (mat number, score), yada yada yada!
        return row.get('score') != None and re.fullmatch('^\d+\.{0,1}\d*$',str(row.get('score'))) != None
    
    def __is_valid_header__(self):
        return self.session != '' and self.courseCode != ''

    def __post_header_call__(self):
        if self.session == None:
            self.session = self._session
        if self.courseCode == None:
            self.courseCode = self._courseCode
            self.courseId = self.courseId
        
    def __pre_sheet_call__(self):
        self.courseId = None
        self.session = None
        self.courseCode = None

    def session_handler(self, r, c):
        s = self._peek_right('^(_){0,1}((\d){2}|(\d){4})/((\d){2}|(\d){4})(_){0,1}$', r, c)
        if s == None:
            return
        y2 = s.strip().replace('_','').split('/')[1]
        if len(y2) == 2:
            y2 = '20' + y2
        self.session = int(y2)

    def code_handler(self, r, c):
        code = self._peek_right('^(_){0,1}[A-z]{3}(\s|_){0,1}\d{3}\.\d(_){0,1}$', r, c)
        if code == None:
            return
        c1 = code.replace('_', '').replace(' ', '').lower()
        c2 = re.split('([a-z]{3})(\d{3})\.(\d)', c1)
        self.courseCode = c2[1] + '_' + c2[2] + '_' + c2[3]
        self.courseId = self.courseCode

    def getResultId(self, mat_no):
        return str(self.session) + '-' + self.courseId + '-' + mat_no.replace('/', '-')
   
    def get_results(self):
        return self.get_data()

if __name__ == '__main__':
    # Run a test using sample master sheet
    root = ''
    if __file__ != None:
        root = re.sub('/[^/]+$', '/', __file__.replace('\\', '/')) + '../'

    master = MasterSheet(root + 'static/excel/ENG301.1.xlsx', courseCode='chm_130_1', session=2019)
    results = master.get_results()
    batch = master.batchId
    code = master.courseCode
    session = master.session

    for data in results:
        print(data)
