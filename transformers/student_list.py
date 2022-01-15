import re
from transformers.table_mapper import TableMapper
#This is where we have the student Biodata!

class StudentList(TableMapper):
    def __init__(self, filename):
            super().__init__(
            filename, table_anchor='matric',
            row_check = {'match': '^[u,U]\d{4}/\d{7}$', 'key': 'mat_no'},
            column_map = [
                {'search': 'matric', 'key': 'mat_no'},
                {'search': 'first', 'key': 'first_name'},
                {'search': '(last|surname)', 'key': 'last_name'},
                {'search': '(middle|other)', 'key': 'other_names'},
                {'search': '(sex|gender)', 'key': 'sex'},
                {'search': 'state', 'key': 'state'},
                {'search': 'marital', 'key': 'marital_status'},
                {'search': 'department', 'key': 'department'},
                {'search': 'missed (session){0,1}', 'key': 'missed_sessions'},
                {'search': 'graduate', 'key': 'graduate'},
                {'search': 'delete', 'key': 'delete'},
            ],)

    def __modify_row__(self, row):
        row.update({'mat_no': row['mat_no'].upper()})
        if re.match('^\s*,{0,1}\s*\d{4}/\d{4}(\s*,\s*\d{4}/\d{4})*\s*,{0,1}\s*$', str(row.get('missed_sessions'))) != None:
            ms = row.get('missed_sessions').strip().strip(',').strip()
            ms = re.split('\s*,\s*', ms)
            for i in range(len(ms)):
                ms[i] = int(ms[i].split('/')[1])
            row['annotation']['missed_sessions'] = ms
        if str(row.get('graduate')).lower() == 'true':
            row['annotation']['graduate'] = 'YES'
        if str(row.get('graduate')).lower() == 'false':
            row['annotation']['graduate'] = 'NO'
        # TODO tests and sanitize (mat number, score), yada yada yada!
        return True
    
    def get_students(self):
        return self.get_data()
