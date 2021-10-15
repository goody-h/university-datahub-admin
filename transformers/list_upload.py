import re
from transformers.table_mapper import TableMapper

class ListUpload(TableMapper):
    def __init__(self, filename):
            super().__init__(
            filename, table_anchor='matric',
            row_check = {'match': '^[u,U]\d{4}/\d{7}$', 'key': 'mat_no'},
            column_map = [
                {'search': 'matric', 'key': 'mat_no'},
            ],)

    def __modify_row__(self, row):
        row.update({'mat_no': row['mat_no'].upper()})
        # TODO tests and sanitize (mat number, score), yada yada yada!
    
if __name__ == '__main__':
    # Run a test using sample master sheet
    root = ''
    if __file__ != None:
        root = re.sub('/[^/]+$', '/', __file__.replace('\\', '/')) + '../'

    lister = ListUpload(root + 'static/excel/ENG301.1.xlsx')
    results = lister.get_data()

    for data in results:
        print(data)
