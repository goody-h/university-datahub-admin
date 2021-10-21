import re
from transformers.table_mapper import TableMapper

class CourseList(TableMapper):
    def __init__(self, filename):
        super().__init__(
            filename, table_anchor='^course code$',
            row_check = {'match': '^[A-z]{3}(\s|_){0,1}\d{3}\.\d$', 'key': 'code'},
            column_map = [
                {'search': '^course code$', 'key': 'code'},
                {'search': 'title', 'key': 'title'},
                {'search': 'cu', 'key': 'cu'},
                {'search': '^level$', 'key': 'level'},
                {'search': '^semester$', 'key': 'sem'},
                {'search': '(elective|pair)', 'key': 'pair'},
                {'search': 'delete', 'key': 'delete'},
            ],
            header_map = [
                {'search': '^faculty:', 'exec': self.faculty_handler},
                {'search': '^department:', 'exec': self.department_handler},
                {'search': '^department long:', 'exec': self.department_l_handler},
                {'search': 'hod:', 'exec': self.hod_handler},
                {'search': 'levels:', 'exec': self.levels_handler},
                {'search': 'semesters:', 'exec': self.semesters_handler},
                {'search': '^code:', 'exec': self.code_handler},
                {'search': 'spreadsheet:', 'exec': self.spreadsheet_handler},
                {'search': 'summary:', 'exec': self.summary_handler},
                {'search': '^delete dept:', 'exec': self.delete_handler},
            ])
        
    def __pre_sheet_call__(self):
        self.faculty = None
        self.dept = None
        self.dept_l = None
        self.hod = None
        self.levels = None
        self.sems = None
        self.code = None
        self.spreadsheet = None
        self.summary = None
        self.delete = None

    def __post_header_call__(self):
        if self.levels == None:
            self.levels = 7
        if self.sems == None:
            self.sems = 2
        if self.spreadsheet == None:
            self.spreadsheet = 'spreadsheet_template_generic'
        if self.summary == None:
            self.summary = 'summary_template_generic'
        if self.delete != None and str(self.delete).lower() == 'true':
            self.delete = 'true'
        if self.code != None:
            self.code.upper()
        
    def __is_valid_header__(self):
        return self.dept != None and self.code != None

    def __modify_row__(self, row):
        row.update({'department': self.code, 'type': 'course' })
        if row.get('pair') == None or re.fullmatch('^\d+$',str(row.get('cu'))) == None:
            row['pair'] = 0
        
        c1 = row['code'].replace('_', '').replace(' ', '').lower()
        c2 = re.split('([a-z]{3})(\d{3})\.(\d)', c1)
        row['code'] = c2[1].upper() + ' ' + c2[2] + '.' + c2[3]
        row['id'] = c2[1] + '_' + c2[2] + '_' + c2[3]

        if self.delete == 'true':
            row['delete'] = self.delete

        return ((row.get('title') != None and row.get('title') != ''
            and row.get('cu') != None and re.fullmatch('^\d+\.{0,1}\d*$',str(row.get('cu'))) != None
            and row.get('level') != None and re.fullmatch('^\d+$',str(row.get('level'))) != None
            and row.get('sem') != None and re.fullmatch('^\d+',str(row.get('sem'))) != None ) 
            or str(row.get('delete')).lower() == 'true')
    
    def __post_sheet_call__(self):
        if self.__is_valid_header__() or (self.delete == 'true' and self.code != None):
            self.data_rows.append({'type': 'department', 'faculty': self.faculty,
             'hod': self.hod, 'department': self.dept, 'department_long': self.dept_l, 
             'levels': self.levels,
             'semesters': self.sems, 'code': self.code, 'spreadsheet': self.spreadsheet,
             'summary': self.summary, 'id': self.code, 'delete': self.delete })

    def faculty_handler(self, r, c):
        self.faculty = self.text_handler(r, c)
    def department_handler(self, r, c):
        self.dept = self.text_handler(r, c)
    def department_l_handler(self, r, c):
        self.dept_l = self.text_handler(r, c)
    def hod_handler(self, r, c):
        self.hod = self.text_handler(r, c)
    def levels_handler(self, r, c):
        self.levels = self.digit_handler(r, c)
    def semesters_handler(self, r, c):
        self.sems = self.digit_handler(r, c)
    def code_handler(self, r, c):
        self.code = self.text_handler(r, c)
    def spreadsheet_handler(self, r, c):
        self.spreadsheet = self.text_handler(r, c)
    def summary_handler(self, r, c):
        self.summary = self.text_handler(r, c)
    def delete_handler(self, r, c):
        self.delete = self.text_handler(r, c)
    def text_handler(self, r, c):
        s = self._peek_right('.+', r, c)
        if s is str:
            return s.strip()
        return s
    def digit_handler(self, r, c):
        s = self._peek_right('^\d+$', r, c)
        return s
