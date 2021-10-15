from openpyxl import load_workbook
from openpyxl.comments import Comment
import re
import transformers.session_utils as session_utils


_sheetMap = {
    'name': 'B6', 'state': 'B7', 'mat_no': 'D6',
    'sex': 'G7', 'marital_status': 'E7', 'session': 'C9',
    'hod': 'B22', 'dept': 'A3', 'faculty': 'A2'
}

class _LeadData(object):
    hod = "22"
    def __init__(self):
        super().__init__()

class _Level(object):
    def __init__(self, level, session, wb, lead_data,  is_lead=False, is_tail=False):
        super().__init__()
        self.results = [[],[]]
        self.total_shift = 0
        self.level = level
        self.session = session
        self.lead_data = lead_data
        self.is_lead = is_lead
        self.is_tail = is_tail

        self.tqp = 0
        self.tcu = 0
        
        ws = None
        self.tables = None
        if wb != None:
            ws = wb['L' + str(level * 100)]
            self.tables = [ws.tables.get('S' + str(level) + '.1'), ws.tables.get('S' + str(level) + '.2')]
        self.ws = ws
    
    def add_result(self, result, semester):
        self.results[semester - 1].append(result)

    def commit(self):
        tqp = 0
        tcu = 0

        refs = None
        ws = None
        row_shift1 = max(len(self.results[0]) - 1, 0)
        row_shift2 = max(len(self.results[1]) - 1, 0)
        total_shift = row_shift1 + row_shift2
        self.total_shift = total_shift
        
        if self.ws != None:
            ws = self.ws
            ws[_sheetMap['session']] = str(self.session - 1) + '/' + str(self.session)
            
            ref1 = self.tables[0].ref
            if row_shift1 > 0:
                ws.insert_rows(int(self._split_ref(ref1)[4]), row_shift1)
                self.tables[0].ref = self._shift_range(ref1, row_shift1)

            ref2 = self.tables[1].ref
            if row_shift1 > 0 or row_shift2 > 0:
                if row_shift2 > 0:
                    ws.insert_rows(int(self._split_ref(ref2)[4]) + row_shift1, row_shift2)
                self.tables[1].ref = self._shift_range(ref2, row_shift1 + row_shift2, row_shift1)
            
            refs = [
                int(self._split_ref(self.tables[0].ref)[2]) + 1,
                int(self._split_ref(self.tables[1].ref)[2]) + 1
            ]
            if self.is_tail:
                ws['G' + str(23 + total_shift)] = ws['G' + str(23 + total_shift)].value.replace('20', str(20 + total_shift))
        
        for c in range(2):
            i = 0
            for result in self.results[c]:
                score = result.get('score')
                unit = result['cu']
                
                if self.ws != None:
                    top = refs[result['sem'] - 1]
                    ws['A' + str(i + top)] = result['code']
                    ws['B' + str(i + top)] = result['title']
                    ws['C' + str(i + top)] = unit
                    ws['D' + str(i + top)] = score
                    for c in range(3, 8):
                        ws.cell(i + top, c).style = ws.cell(top, c).style
                    for c in range(5, 8):
                        ws.cell(i + top, c).value = ws.cell(top, c).value
                    if result.get('comment') != '' and result.get('comment') != None:
                        ws.cell(i + top, 4).comment = Comment('Revisions:\n' + result.get('comment'), 'Auto', width=300)
                
                if unit != None and score != None:
                    scorer = [39.9999, 44.9999, 49.9999, 59.9999, 69.9999, score]
                    scorer.sort()
                    gp = scorer.index(score)
                    tcu += unit
                    tqp += gp * unit
                i += 1

        self.tqp = tqp
        self.tcu = tcu

        if self.is_lead:
            self.lead_data.hod = str(22 + total_shift)
        
    def _shift_range(self, range, bottom, top=0):
        rng = self._split_ref(range)
        return rng[1] + str(int(rng[2]) + top) + ':' + rng[3] + str(int(rng[4]) + bottom)

    def _split_ref(self, ref):
        return re.split('([A-Z]+)(\d+):([A-Z]+)(\d+)', ref)

    def finish(self):
        if not self.is_lead and self.ws != None:
            hod_cell = str(22 + self.total_shift)
            self.ws['B' + hod_cell] = self.ws['B' + hod_cell].value.replace('22', self.lead_data.hod)


class SpreadSheet(object):

    def __init__(self):
        super().__init__()
        self._wb = None
        self.scored_results = []

    def generate(self, user, results, courses, template = '', filename = ''):

        user['name'] = (user['last_name'].upper() + ', ' + 
            user['first_name'].capitalize() + ' ' + user['other_names'].capitalize()).strip().rstrip(',')

        if template != None and template != '':
            _wb = load_workbook(template)
            self._wb = _wb
        
            for key in user.keys():
                if _sheetMap.get(key) != None:
                    _wb['L100'][_sheetMap[key]] = user[key]
        
        level_status = { 'sessions': {}, 'last_sem': 100 }
        result_map = {}

        # step 1: remove carry-overs
        for result in results:
            result.update(courses[result['courseCode']])
            result.update({'_session': result['session'], 'comment': ''})
            map = result_map.get(result['courseCode'])

            l_session = level_status['sessions'].get(result['session'])
            if l_session == None or result['level'] + result['sem'] > l_session:
                level_status['sessions'][result['session']] = result['level'] + result['sem']
            
            if result['level'] + result['sem'] > level_status['last_sem']:
                level_status['last_sem'] = result['level'] + result['sem']
            if result['score'] < 40:
                result['cu'] = 0
            if map == None or (map['score'] < 40 and result['session'] > map['session']):
                if map != None:
                    result['comment'] = (map['comment'] + '[ session: ' + str(map['session'] - 1) + '/' 
                        + str(map['session']) + ', score: ' + str(map['score']) + ']\n')
                    result['_session'] = result['session'] + 0.4
                result_map[result['courseCode']] = result
            else:
                result_map[result['courseCode']]['comment'] = (map['comment'] + 'flag* [ session: ' + str(result['session'] - 1) + '/' 
                    + str(result['session']) + ', score: ' + str(result['score']) + ']\n')

        self.scored_results.extend(results)

        level_status.update(session_utils.rectify(level_status['sessions']))

        # step 2: add missing courses till last semester    
        for key in courses.keys():
            if result_map.get(key) == None and courses[key]['level'] + courses[key]['sem'] <= level_status['last_sem']:
                result_map[key] = {}
                result_map[key].update(courses[key])
                session = level_status['sessions'][int(courses[key]['level']/100) - 1]
                result_map[key].update({'courseCode': key, 'cu': None, '_session': session + 0.5, 'session': session })

        final_results = []
        final_results.extend(result_map.values())
        final_results.sort(key = lambda i: (i['_session'], i['code']))

        # step 3: write reuluts to sheet
        level_data = self._write_results(final_results, level_status)
        response = {'status': 'success', 'message': '', 'level_data': level_data, 'user': user}

        print('Written {} results'.format(len(self.scored_results)))

        # step 4: remove unused sheets
        if self._wb != None:
            for sheet in _wb.worksheets:
                if sheet[_sheetMap['session']].value == None and sheet.title != 'L100':
                    _wb.remove(sheet)

            try:
                _wb.save(filename)
                response.update({'status': 'success', 'message': 'Spreadsheet generated successfully'})
            except Exception as e:
                response.update({'status': 'error', 'message': 'The file {}, is already opened by another program. Please, close the file and try again'.format(filename)})
            finally:
                _wb.close()
                _wb = None

        return response


    def _write_results(self, results, status):
        levels = {}
        lead_data = _LeadData()
        for result in results:
            level = status['sessions'].index(result['session']) + 1
            sem = result['sem']
            if levels.get(level) == None:
                levels[level] = _Level(level, result['session'], self._wb, lead_data, is_lead=level == 1, is_tail=level>=5)
            levels[level].add_result(result, sem)
        for level in levels.values():
            level.commit()
        for level in levels.values():
            level.finish()
            levels[level.level] = {'tcu': level.tcu, 'tqp': level.tqp}
        return levels


if __name__ == '__main__':
    # Run a test using sample data
    from sample_data.result import user, result
    from sample_data.courses import MEG, MCT
    import os

    # sort results by only session
    result.sort(key = lambda i: (i['session']))
    courses = MEG
    root = ''

    if user['department'] == 'MCT':
        courses = MCT
    
    if __file__ != None:
        root = re.sub('/[^/]+$', '/', __file__.replace('\\', '/')) + '../'
    
    try:
        os.mkdir(root + 'output')
        print('output directory created')
    except:
        print('output directory already exists, skipping')

    spread_sheet = SpreadSheet()
    spread_sheet.generate(
        user, result, courses, 
        filename=root + 'output/sample_spreadsheet.xlsx',
        template=root + 'static/excel/spreadsheet_template.xlsx',
    )

