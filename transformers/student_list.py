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
                {'search': '(missed (session){0,1}|defer)', 'key': 'missed_sessions'},
                {'search': 'graduate', 'key': 'graduate'},
                {'search': 'waive(r){0,1}', 'key': 'waiver'},
                {'search': 'delete', 'key': 'delete'},
            ],)

    def __modify_row__(self, row):
        row.update({'mat_no': row['mat_no'].upper()})

        def re_list_pattern(base):
            return '^\s*,{0,1}\s*' + base + '(\s*,\s*' + base + ')*\s*,{0,1}\s*$'
        if re.match(re_list_pattern('\d{4}/\d{4}'), str(row.get('missed_sessions'))) != None:
            ms = row.get('missed_sessions').strip().strip(',').strip()
            ms = re.split('\s*,\s*', ms)
            for i in range(len(ms)):
                ms[i] = int(ms[i].split('/')[1])
            row['annotation']['missed_sessions'] = ms
        elif 'missed_sessions' in row.keys():
            row['annotation']['missed_sessions'] = None
            
        if re.match(re_list_pattern('[A-z]{3}(\s|_){0,1}\d{3}\.\d'), str(row.get('waiver'))) != None:
            ms = row.get('waiver').strip().strip(',').strip()
            ms = re.split('\s*,\s*', ms)
            if len(ms) < 3:
                for i in range(len(ms)):
                    c1 = ms[i].replace('_', '').replace(' ', '').lower()
                    c2 = re.split('([a-z]{3})(\d{3})\.(\d)', c1)
                    ms[i] = c2[1] + '_' + c2[2] + '_' + c2[3]
                row['annotation']['waiver'] = ms
        elif 'waiver' in row.keys():
            row['annotation']['waiver'] = None

        if str(row.get('graduate')).lower() == 'true':
            row['annotation']['graduate'] = 'YES'
        elif str(row.get('graduate')).lower() == 'false':
            row['annotation']['graduate'] = 'NO'
        elif 'graduate' in row.keys():
            row['annotation']['graduate'] = None

        return True
    
    def get_students(self):
        return self.get_data()
