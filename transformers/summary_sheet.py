from openpyxl import load_workbook
from openpyxl.comments import Comment
import re
import transformers.session_utils as session_utils

class SummarySheet(object):
    def __init__(self):
        super().__init__()

    def generate(self, results, template = '', filename = ''):
        _wb = load_workbook(template)
        self._wb = _wb
        response = {}
        output = []
        ws = _wb['Summary']

        for res in results:
            tcu = 0
            tqp = 0
            cgpa = 0
            for value in res['level_data'].values():
                tcu += value['tcu']
                tqp += value['tqp']
            if tcu != 0:
                cgpa = tqp / tcu
            res['user'].update({'cgpa': cgpa, 'tcu': tcu, 'tqp': tqp})
            output.append(res['user'])
            
        output.sort(key = lambda e: (-e['cgpa']))

        row_shift = max(len(output) - 1, 0)

        table = ws.tables.get('SummaryTable')
        ref = table.ref

        if row_shift > 0:
            ws.insert_rows(int(self._split_ref(ref)[4]), row_shift)
            table.ref = self._shift_range(ref, row_shift)

        top = int(self._split_ref(table.ref)[2]) + 1

        i = 0
        for out in output:
            ws['A' + str(i + top)] = out['mat_no']
            ws['B' + str(i + top)] = out['name']
            ws['C' + str(i + top)] = out['tcu']
            ws['D' + str(i + top)] = out['tqp']
            ws['E' + str(i + top)] = out['cgpa']
            for c in range(1, 6):
                ws.cell(i + top, c).style = ws.cell(top, c).style
            i += 1

        try:
            _wb.save(filename)
            response.update({'status': 'success', 'message': 'Summary sheet generated successfully'})
        except Exception as e:
            response.update({'status': 'error', 'message': 'The file {}, is already opened by another program. Please, close the file and try again'.format(filename)})
        finally:
            _wb.close()
            _wb = None

    def _shift_range(self, range, bottom, top=0):
        rng = self._split_ref(range)
        return rng[1] + str(int(rng[2]) + top) + ':' + rng[3] + str(int(rng[4]) + bottom)

    def _split_ref(self, ref):
        return re.split('([A-Z]+)(\d+):([A-Z]+)(\d+)', ref)

