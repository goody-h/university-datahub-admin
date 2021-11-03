import re
from transformers.table_mapper import TableMapper

class MasterSheet(TableMapper):
    def __init__(self, filename, courseCode=None, session=None):
        super().__init__(
            filename, table_anchor='matric',
            row_check = {'match': '^[u,U]\d{4}/\d{7}$', 'key': 'mat_no'},
            column_map = [
                {'search': 'matric', 'key': 'mat_no'},
                {'search': '(total|score)', 'key': 'score'},
                {'search': 'delete', 'key': 'delete'},
                {'search': 'session', 'key': 'session'},
                {'search': 'course (code|no)', 'key': 'code'},
            ],
            header_map = [{'search': 'session', 'exec': self.session_handler}, {'search': 'course (code|no)', 'exec': self.code_handler}]),
            
        self._courseId = courseCode
        self._session = session
        self._courseCode = courseCode

    def __modify_row__(self, row):
        if re.match('^(_){0,1}(\d){4}/(\d){4}(_){0,1}$', str(row.get('session'))) != None:
            row['session'] = int(row['session'].strip().replace('_','').split('/')[1])
        elif self.session != None:
            row['session'] = self.session
        else:
            return False
        if re.match('^(_){0,1}[A-z]{3}(\s|_){0,1}\d{3}\.\d(_){0,1}', str(row.get('code'))) != None:
            c1 = row['code'].replace('_', '').replace(' ', '').lower()
            c2 = re.split('([a-z]{3})(\d{3})\.(\d)', c1)
            courseCode = c2[1] + '_' + c2[2] + '_' + c2[3]
            row.update({'courseCode': courseCode, 'courseId': courseCode})
        elif self.courseCode != None:
            row.update({'courseCode': self.courseCode, 'courseId': self.courseCode})
        else:
            return False

        row.update({
            'mat_no': row['mat_no'].upper(),
            'resultId': self.getResultId(row['mat_no'].upper(), row['session'], row['courseCode'])
        })
        # TODO tests and sanitize (mat number, score), yada yada yada!
        return ((row.get('score') != None and re.fullmatch('^\d+\.{0,1}\d*$',str(row.get('score'))) != None) 
            or str(row.get('delete')).lower() == 'true')
    
    # def __is_valid_header__(self):
        # return self.session != '' and self.courseCode != ''

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
        code = self._peek_right('^(_){0,1}[A-z]{3}(\s|_){0,1}\d{3}\.\d(_){0,1}', r, c)
        if code == None:
            return
        c1 = code.replace('_', '').replace(' ', '').lower()
        c2 = re.split('([a-z]{3})(\d{3})\.(\d)', c1)
        self.courseCode = c2[1] + '_' + c2[2] + '_' + c2[3]
        self.courseId = self.courseCode

    def getResultId(self, mat_no, session, code):
        return str(session) + '-' + code + '-' + mat_no.replace('/', '-')
   
    def get_results(self):
        return self.get_data()

