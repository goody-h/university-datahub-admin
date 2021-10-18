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
                {'search': 'delete', 'key': 'delete'},
            ],)

    def __modify_row__(self, row):
        row.update({'mat_no': row['mat_no'].upper()})
        # TODO tests and sanitize (mat number, score), yada yada yada!
        return True
    
    def get_students(self):
        return self.get_data()

if __name__ == '__main__':
    # Run a test using sample master sheet
    root = ''
    if __file__ != None:
        root = re.sub('/[^/]+$', '/', __file__.replace('\\', '/')) + '../'

    lister = StudentList(root + 'static/excel/ENG301.1.xlsx')
    results = lister.get_students()
    batch = lister.batchId

    for data in results:
        print(data)
