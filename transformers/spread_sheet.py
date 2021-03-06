from openpyxl import load_workbook
from openpyxl.comments import Comment
import re
import transformers.session_utils as session_utils
from services.storage import Storage



_sheetMap = {
    'name': 'B6', 'state': 'B7', 'mat_no': 'D6',
    'sex': 'G7', 'marital_status': 'E7', 'session': 'C9',
    'hod': 'B22', 'dept': 'A3', 'faculty': 'A2'
}

class _SharedData(object):
    hod = "22"
    def __init__(self, cache):
        super().__init__()
        self.lead_level = 0
        self.cache = cache

class _Level(object):
    def __init__(self, level, session, wb, shared_data, department, user = None):
        super().__init__()
        self.results = []
        self.total_shift = 0
        self.level = level
        self.session = session
        self.shared_data = shared_data
        self.is_lead = False
        self.department = department
        self.wb = wb
        self.sem_tcu = {}
        self.user = user

        self.tqp = 0
        self.tcu = 0
        self.tco = []
        self.waive = []

        ws = None
        self.tables = None

        if wb != None:
            ws = wb['L' + str(level * 100)]
            self.tables = []
            for i in range(0, department.semesters):
                self.results.append([])
                if ws != None:
                    self.tables.append(ws.tables.get('S{}.{}'.format(level, i + 1)))
        self.ws = ws
        self.result_map = {}
        self.props = []
        self.reject = []
        self.review_flags = []
        if shared_data != None:
            self.reject = shared_data.cache['reject']
            self.review_flags = shared_data.cache['review_flags']

    def evaluate_results(self):
        results = []
        for i in range(len(self.results)):
            sem = self.results[i]
            tcu = self.sem_tcu.get(i+1)
            sem.sort(key = lambda i: (i['_session'], i['code']))
            for i in range(len(sem)-1, -1, -1):
                result = sem[i]
                # Current policy Flag comment them
                if tcu > self.department.max_cu:
                    self.shared_data.cache['review'] = True
                    self.shared_data.cache['review_flags'].append('max-cu')
                    result['comment'] += 'flag* [ Maximum credit load exceeded ]\n'
            results.extend(sem)
        return results
    
    def add_result(self, result, semester):
        if semester > 0:
            if semester > len(self.results):
                for i in range(semester - len(self.results)):
                    self.results.append([])
            
            ne_prop = re.split('(no-extra)', str(result['properties']))

            if self.sem_tcu.get(semester) == None:
               self.sem_tcu[semester] = 0
            
            if len(ne_prop) > 1 and self.props.count('no-extra{}'.format(semester)) == 0 and result.get('score') != None:
                self.props.append('no-extra{}'.format(semester))
                self.sem_tcu[semester] = 0
                for res in self.results[semester - 1]:
                    res['reason'] += '[No extra courses allowed in this session] \n'
                    self.result_map[res['courseCode']] = None
                    self.review_flags.append('no-extra')
                self.reject.extend(self.results[semester - 1])
                self.results[semester - 1].clear()

            if self.props.count('no-extra{}'.format(semester)) == 0 or len(ne_prop) > 1 or result.get('score') == None:
                self.results[semester - 1].append(result)
                self.result_map[result['courseCode']] = result
                au_prop = re.split('(add-unit)', str(result['properties']))
                if not (len(au_prop) > 1 or result.get('cu') == None):
                    self.sem_tcu[semester] += result['cu']
            else:
                result['reason'] += '[No extra courses allowed in this session] \n'
                self.reject.append(result)
                self.review_flags.append('no-extra')
    
    def commit_extra(self, results, wb, tag = 'unknown'):
        b = 'Unknown Courses'
        t = 'Unknown'
        if tag == 'flagged':
            b = 'Flagged Results'
            t = "Flagged"
        elif tag == 'outstanding':
            b = 'Outstanding Courses'
            t = "Outstanding"
        if len(results) > 0 and wb[b] != None and wb[b].tables.get(t) != None:
            ws = wb[b]
            table = ws.tables.get(t)
            ws[_sheetMap['session']] = ' '
            ref = table.ref
            totals = table.totalsRowCount
            row_shift = max(len(results) - 1, 0)
            if row_shift > 0:
                ws.insert_rows(int(self._split_ref(ref)[4]) + 1 - totals, row_shift)
                table.ref = self._shift_range(ref, row_shift)
            top = int(self._split_ref(table.ref)[2]) + 1
            i = 0
            for result in results:
                ws['A' + str(i + top)] = re.split('&None&|&', '&{}&{}'.format(result.get('code'), result.get('courseCode')))[1]
                if result.get('title') == None:
                    result['title'] = '?'
                ws['B' + str(i + top)] = result.get('title')
                cu = result.get('cu') if result.get('cu') != None else result.get('_cu') if result.get('_cu') != None else '?'
                ws['C' + str(i + top)] = cu
                ws['D' + str(i + top)] = result.get('score')
                ws['F' + str(i + top)] = str(result.get('session') - 1) + '/' + str(result.get('session'))
                ws['G' + str(i + top)] = result.get('reason').rstrip(' \n')

                if result.get('comment') == None:
                    result['comment'] = ''
                if result.get('_comment') == None:
                    result['_comment'] = ''
                result['comment'] += result['_comment']
            
                if result.get('comment') != '' and result.get('comment') != None:
                    ws.cell(i + top, 4).comment = Comment('Review:\n' + result.get('comment'), 'Auto', width=300)

                for c in range(1, 8):
                    ws.cell(i + top, c).style = ws.cell(top, c).style
                for c in range(5, 6):
                    ws.cell(i + top, c).value = ws.cell(top, c).value
                i += 1

    def commit(self):
        tqp = 0
        tcu = 0
        tco = []
        waive = []

        self.tables = []
        refs = []
        total_shift = 0
        
        if self.ws != None:
            ws = self.ws
            ws[_sheetMap['session']] = str(self.session - 1) + '/' + str(self.session)
            self.is_lead = str(ws[_sheetMap['dept']].value).count('=') == 0
            
            for s in range(0, len(self.results)):
                self.tables.append(self.ws.tables.get('S{}.{}'.format(self.level, s + 1)))
        for t in range(len(self.results)):
            table = None
            shift = max(len(self.results[t]) - 1, 0)
            if self.ws != None:
                table = self.tables[t]
            if table != None:
                
                ref = table.ref
                totals = table.totalsRowCount
                if totals == None:
                    totals = 0
                if total_shift > 0 or shift > 0:
                    if shift > 0:
                        ws.insert_rows(int(self._split_ref(ref)[4]) + total_shift + 1 - totals, shift)
                    table.ref = self._shift_range(ref, total_shift + shift, total_shift)
                refs.append(int(self._split_ref(table.ref)[2]) + 1)
            else:
                refs.append(None)
            total_shift += shift
        
        if self.ws != None:
            if ws['G' + str(13 + total_shift + self.get_semesters_range())].value != None:
                ws['G' + str(13 + total_shift + self.get_semesters_range())] = ws['G' + str(13 + total_shift + 
                        self.get_semesters_range())].value.replace(str(10 + self.get_semesters_range()),
                                str(10 + total_shift + self.get_semesters_range()))
        
        self.total_shift = total_shift
         
        for c in range(len(self.results)):
            i = 0
            self.results[c].sort(key = lambda i: (i['_session'], i['code']))
            for result in self.results[c]:
                score = result.get('score')
                unit = result['cu']
                
                if unit != None and score != None:
                    scorer = [39.9999, 44.9999, 49.9999, 59.9999, 69.9999, score]
                    scorer.sort()
                    gp = scorer.index(score)
                    if result['flags'].count('carryover') > 0:
                        gp = min(3, gp)
                    if score < 40:
                        if result['flags'].count('waiver') == 0:
                            result['_out'] = 0
                            tco.append(result)
                        else:
                            waive.append(result)
                            result['title'] += '      [W]'
                    tcu += unit
                    tqp += gp * unit
                
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
                    
                    if result.get('comment') == None:
                        result['comment'] = ''
                    if result.get('_comment') == None:
                        result['_comment'] = ''
                    result['comment'] += result['_comment']
                
                    if result.get('comment') != '' and result.get('comment') != None:
                        ws.cell(i + top, 4).comment = Comment('Review:\n' + result.get('comment'), 'Auto', width=300)
                
                i += 1

        self.tqp = tqp
        self.tcu = tcu
        self.tco = tco
        self.waive = waive

        if self.is_lead:
            if self.level > self.shared_data.lead_level:
                self.shared_data.lead_level = self.level
                self.shared_data.hod = str(12 + total_shift + self.get_semesters_range())
            if self.ws != None:
                for key in self.user.keys():
                    if _sheetMap.get(key) != None:
                        self.ws[_sheetMap[key]] = self.user[key]
        
    def _shift_range(self, range, bottom, top=0):
        rng = self._split_ref(range)
        return rng[1] + str(int(rng[2]) + top) + ':' + rng[3] + str(int(rng[4]) + bottom)

    def _split_ref(self, ref):
        return re.split('([A-Z]+)(\d+):([A-Z]+)(\d+)', ref)

    def get_semesters_range(self):
        return 5 * self.department.semesters

    def finish(self):
        if not self.is_lead and self.ws != None:
            hod_cell = str(12 + self.total_shift + self.get_semesters_range())
            self.ws['B' + hod_cell] = self.ws['B' + hod_cell].value.replace(str(12 + self.get_semesters_range()), self.shared_data.hod)

class ResultFilter():
    def __init__(self, cache):
        if cache.get('sessions') == None:
            cache.update({'sessions': [], 'last_sem': 100, 'electives': {}, 'reject': [], 'outstanding': [], 'review': False, 'review_flags': []})
        self.hold = []
        self.cache = cache
        self.reject = cache['reject']
        self.outstanding = cache['outstanding']
        self.reset = True
        self.data = {}
    def reset_filter(self):
        pass
    def evaluate_result(self, result):
        if self.reset:
            self.reset = False
            self.data = {}
            self.reset_filter()
        return self._evaluate_result(result)
    def _evaluate_result(self, result):
        return True
    def release_hold(self):
        hold = self.hold
        self.hold = []
        self.reset = True
        return hold

class HeadFilter(ResultFilter):
    def __init__(self, cache, results = []):
        super().__init__(cache)
        self.hold = results
    def reset_filter(self):
        self.cache.update({'electives': {}})

class CourseFilter(ResultFilter):
    def __init__(self, cache, courses, wb):
        super().__init__(cache)
        self.reject = []
        self.courses = courses
        self.wb = wb

    def _evaluate_result(self, result):
        result.update({'_session': result['session'], 'comment': '', 'flags': [], 'reason': '', 'priority': 0})
        if result.get('_comment') == None:
            result['_comment'] = ''
        course = self.courses.get(result['courseCode'])
        if course == None:
            self.reject.append(result)
            return False
        result.update(course)
        return super()._evaluate_result(result)

    def release_hold(self):
        if self.wb != None:
            unknown = _Level(None, None, None, None, None)
            unknown.commit_extra(self.reject, self.wb)
        return super().release_hold()

class OverflowFilter(ResultFilter):
    def __init__(self, cache, dept, courses, user):
        super().__init__(cache)
        self.min_level = int(dept.levels)
        self.min_sess = int(re.split('U(\d{4})/.*$', user['mat_no'])[1]) + 1
        self.miss =  user.get('missed_sessions') if user.get('missed_sessions') != None else []
        self.levels = [i for i in range(self.min_sess, self.min_sess + dept.levels + len(self.miss) + 1) if self.miss.count(i) == 0]
        for course in courses.values():
            l = int(course['level'] / 100)
            self.min_level = min(self.min_level, l)
            if l == 1: break

    def _evaluate_result(self, result):
        level_session = self.levels[int(result['level']/100) - self.min_level]
        if result['session'] < level_session and self.miss.count(result['session']) == 0:
            old = result['session']
            result['priority'] = 10
            result['session'] = level_session
            result['_session'] = level_session
            result['_comment'] += 'flag* [Academic session was corrected from {}/{} to {}/{}]\n'.format(old - 1, old, level_session -1, level_session)
            self.cache['review'] = True
            self.cache['review_flags'].append('wrong-session')
        return super()._evaluate_result(result)

class SessionFilter(ResultFilter):
    def __init__(self, cache, department, missed_sessions):
        super().__init__(cache)
        self.department = department
        self.missed_sessions = missed_sessions

    def reset_filter(self):
        self.data.update({ 'sessions': {}, 'last_sem': 100})

    def _evaluate_result(self, result):
        l_session = self.data['sessions'].get(result['session'])
        if l_session == None:
            l_session = 100
        sem_id = result['level'] + result['sem']
        if result['sem'] > l_session % 100:
            sem_id = max(l_session - (l_session % 100), result['level']) + result['sem']
        if l_session == None or sem_id > l_session:
            self.data['sessions'][result['session']] = sem_id
        if sem_id > self.data['last_sem']:
            self.data['last_sem'] = sem_id
        self.hold.append(result)
        return False

    def release_hold(self):
        self.cache.update(session_utils.rectify(self.data['sessions'], self.department.levels, self.department.semesters, self.missed_sessions))
        return super().release_hold()

class MaxSessionFilter(ResultFilter):
    def _evaluate_result(self, result):
        if self.cache['sessions'].count(result['session']) == 0:
            last_sess = max(self.cache['sessions'])
            if result['session'] > last_sess:
                result['reason'] += '[Maximum academic sessions exceeded] \n'
                self.cache['review_flags'].append('max-session')
            else:
                result['reason'] += '[This is a missed academic session] \n'
                self.cache['review_flags'].append('missed-session')
            self.reject.append(result)
            return False
        return super()._evaluate_result(result)

class SignatureFilter(ResultFilter):
    def _evaluate_result(self, result):
        if result.get('verified') == False:
            result['reason'] += '[This result failed signature verification] \n'
            self.cache['review_flags'].append('invalid-signature')
            self.reject.append(result)
            return False
        return super()._evaluate_result(result)

class CarryoverFilter(ResultFilter):
    def reset_filter(self):
        self.cache['result_map'] = {}
        self.data = self.cache['result_map']

    def _evaluate_result(self, result):
        map = self.data.get(result['courseCode'])
        if map == None or (map['score'] < 40 and result['session'] > map['session']):
            if map != None:
                result['comment'] = (map['comment'] + '[ session: ' + str(map['session'] - 1) + '/' 
                    + str(map['session']) + ', score: ' + str(map['score']) + ']\n')
                result['_session'] = result['session'] + 0.4
                result['code'] += '*'
                result['flags'].append('carryover')
                map['_cu'] = map.get('cu')
                map['cu'] = None
                self.data[map['courseCode'] + '_' + str(map['session'])] = map
            elif result['level'] / 100 != self.cache['sessions'].index(result['session']) + 1:
                result['_session'] = result['session'] + 0.2

            self.data[result['courseCode']] = result
        elif map != None:
            self.data[result['courseCode'] + '_' + str(result['session'])] = result

        return super()._evaluate_result(result)

class DuplicateFilter(ResultFilter):
    def reset_filter(self):
        if self.cache.get('result_map') == None:
            self.cache['result_map'] = {}
        self.data = self.cache.get('result_map')

    def _evaluate_result(self, result):
        map = self.data.get(result['courseCode'])
        if map != None and  result['session'] == map['session'] and result != map:
            if map['priority'] < result['priority']:
                self.data[result['courseCode']]['_comment'] = (map['_comment'] + 'flag* [ Duplicate session | session: ' + str(result['session'] - 1) + '/' 
                    + str(result['session']) + ', score: ' + str(result['score']) + ']\n')
                result['reason'] += '[Duplicate session {}/{}] \n'.format(map['session'] - 1, map['session'])
                self.reject.append(result)
            else:
                self.data[result['courseCode']] = result
                self.data[result['courseCode']]['_comment'] = (result['_comment'] + 'flag* [ Duplicate session | session: ' + str(map['session'] - 1) + '/' 
                    + str(map['session']) + ', score: ' + str(map['score']) + ']\n')
                map['reason'] += '[Duplicate session {}/{}] \n'.format(map['session'] - 1, map['session'])
                self.reject.append(map)
            self.cache['review_flags'].append('duplicate-result')
        return False

    def release_hold(self):
        self.hold = self.data.values()
        return super().release_hold()


class RetakeFilter(ResultFilter):
    def __init__(self, cache, flag_only = False):
        super().__init__(cache)
        self.flag_only = flag_only

    def reset_filter(self):
        if self.cache.get('result_map') == None:
            self.cache['result_map'] = {}
        self.data = self.cache.get('result_map')

    def _evaluate_result(self, result):
        map = self.data.get(result['courseCode'])
        if not (map == None or (map['score'] < 40 and result['session'] > map['session'])) and result['session'] != map['session']:
            self.data[result['courseCode']]['comment'] = (map['comment'] + 'flag* [ session: ' + str(result['session'] - 1) + '/' 
                + str(result['session']) + ', score: ' + str(result['score']) + ']\n')
            result['reason'] += '[Course has already been passed in session {}/{}] \n'.format(map['session'] - 1, map['session'])
            if not self.flag_only:
                self.reject.append(result)
                self.cache['review_flags'].append('retake')
                return False
        return super()._evaluate_result(result)

class WaiverFilter(ResultFilter):
    def __init__(self, cache, waivers):
        super().__init__(cache)
        self.waivers = waivers

    def reset_filter(self):
        if self.cache.get('result_map') == None:
            self.cache['result_map'] = {}
        self.data = self.cache.get('result_map')

    def release_hold(self):
        if self.waivers != None and len(self.waivers) > 0:
            for waiver in self.waivers:
                map = self.data.get(waiver)
                map['flags'].append('waiver')
        return super().release_hold()

class ElectiveFilter(ResultFilter):
    def _evaluate_result(self, result):
        sem_id = result['level'] + result['sem']
        prop = re.split('(elective-pair):(\d+)', str(result['properties']))
        if len(prop) > 1:
            result['_session'] = result['session'] + 0.1
            if self.cache['electives'].get(sem_id) == None:
                self.cache['electives'][sem_id] = { 'all': [result['courseCode']]}
            else:
                self.cache['electives'][sem_id]['all'].append(result['courseCode'])
            self.hold.append(result)
            return False
        return super()._evaluate_result(result)

    def release_hold(self):
        # Current policy Flag comment them
        for i in range(len(self.hold)-1, -1, -1):
            result = self.hold[i]
            prop = re.split('(elective-pair):(\d+)', str(result['properties']))
            elective_pair = int(prop[2])
            sem_id = result['level'] + result['sem']
            cache = self.cache
            all = set(cache['electives'][sem_id]['all'])
            if len(all) > elective_pair:
                cache['review'] = True
                result['comment'] += 'flag* [ Excess electives taken{} ]\n'.format(all)
                cache['review_flags'].append('excess-electives')
        return super().release_hold()

class LevelFilter(ResultFilter):
    def __init__(self, cache, levels, wb, department, user):
        super().__init__(cache)
        self.levels = levels
        self.level_data = _SharedData(self.cache)
        self.department = department
        self.wb = wb
        self.results = []
        self.user = user

    def reset_filter(self):
        self.level_data.lead_level = 0
        self.levels.clear()

    def _evaluate_result(self, result):
        level = self.cache['sessions'].index(result['session']) + 1
        sem = result['sem']
        if self.levels.get(level) == None:
            self.levels[level] = _Level(level, result['session'], self.wb, self.level_data, self.department, self.user)
        self.levels[level].add_result(result, sem)
        return False
    
    def release_hold(self):
        results = []
        for level in self.levels.values():
            _results = level.evaluate_results()
            results.extend(_results)
        if len(self.levels) == 0 and len(self.cache['sessions']) > 0:
            self.levels[1] = _Level(1, self.cache['sessions'][0], self.wb, self.level_data, self.department, self.user)
        results.sort(key = lambda i: (i['_session'], i['code']))
        self.hold = results
        self.results = results
        return super().release_hold()

class MissingFilter(ResultFilter):
    def __init__(self, cache, levels, courses):
        super().__init__(cache)
        self.levels = levels
        self.courses = courses

    def release_hold(self):
        results = {}
        courses = self.courses
        department = None
        wb = None
        level_data = None
        for level in self.levels.values():
            department = level.department
            wb = level.wb
            level_data = level.shared_data
            user = level.user
            results.update(level.result_map)

        for key in courses.keys():
            sem_id = courses[key]['level'] + courses[key]['sem']
            elective_pair = 0
            prop = re.split('(elective-pair):(\d+)', str(courses[key]['properties']))
            prop_opt = re.split('(optional)', str(courses[key]['properties']))
            if len(prop_opt) > 1:
                continue
            if len(prop) > 1:
                elective_pair = int(prop[2])
            if (results.get(key) == None and sem_id <= self.cache['last_sem']
                and (elective_pair == 0 or self.cache['electives'].get(sem_id) == None or 
                len(set(self.cache['electives'][sem_id]['all'])) < elective_pair)
            ):
                result = {}
                result.update(courses[key])
                session = self.cache['sessions'][int(courses[key]['level']/100) - 1]
                result.update({'courseCode': key, 'cu': None, '_cu': result.get('cu'), '_session': session + 0.5, 'session': session, 'comment': '', 'flags': [], 'reason': '' })

                level = self.cache['sessions'].index(result['session']) + 1
                sem = result['sem']
                if self.levels.get(level) == None:
                    self.levels[level] = _Level(level, result['session'], wb, level_data, department, user)
                if elective_pair > 0:
                    result['title'] += ' [E]'
                self.levels[level].add_result(result, sem)                    
                result['_out'] = 1
                self.outstanding.append(result)
                
        return super().release_hold()

class StopFilter(ResultFilter):
    def __init__(self, cache, levels, wb):
        super().__init__(cache)
        self.levels = levels
        self.wb = wb
        self.waivers = []

    def release_hold(self):
        for level in self.levels.values():
            level.commit()
        for level in self.levels.values():
            level.finish()
            self.outstanding.extend(level.tco)
            self.waivers.extend(level.waive)
            self.levels[level.level] = {'tco': len(level.tco), 'tcu': level.tcu, 'tqp': level.tqp, 'session': level.session }
        if self.wb != None:
            unknown = _Level(None, None, None, None, None)
            unknown.commit_extra(self.reject, self.wb, tag = 'flagged')
            self.outstanding.sort(key = lambda i: (i['_out'], i['_session'], i['sem'], i['code']))
            unknown.commit_extra(self.outstanding, self.wb, tag = 'outstanding')
        return super().release_hold()

class SpreadSheet(object):
    def evaluate(self, filters, index = 0):
        for result in filters[index].release_hold():
            for i in range(index + 1, len(filters)):
                if not filters[i].evaluate_result(result):
                    break
        if index < len(filters) - 1:
            self.evaluate(filters, index + 1)

    def __init__(self):
        super().__init__()
        self._wb = None
        self.scored_results = []
        self.invalid_results = []

    def generate(self, user, results, courses, department, filename = ''):
        user['name'] = (user['last_name'].upper() + ', ' + 
            user['first_name'].capitalize() + ' ' + user['other_names'].capitalize()).strip().rstrip(',')
        if department.faculty != None:
            user['faculty'] = department.faculty
        if department.department_long != None:
            user['dept'] = department.department_long
        if department.hod != None:
            user['hod'] = department.hod

        _sheetMap['hod'] = 'B{}'.format(12 + (5 * department.semesters))

        if filename != None and filename != '':
            store = Storage()
            _wb = load_workbook(store.find_template('{}.xlsx'.format(department.spreadsheet)))
            self._wb = _wb
        
        cache = {}
        levels = {}
        course_filter = CourseFilter(cache, courses, self._wb)
        session_filter = SessionFilter(cache, department, user.get('missed_sessions'))
        max_session_filter = MaxSessionFilter(cache)
        carryover_filter = CarryoverFilter(cache)
        duplicate_filter = DuplicateFilter(cache)
        retake_filter1 = RetakeFilter(cache, flag_only= True)
        retake_filter2 = RetakeFilter(cache)
        waiver_filter = WaiverFilter(cache, user.get('waiver'))
        elect_filter = ElectiveFilter(cache)
        level_filter = LevelFilter(cache, levels, self._wb, department, user)
        miss_filter = MissingFilter(cache, levels, courses)
        stop = StopFilter(cache, levels, self._wb)
        filters = [HeadFilter(cache, results), course_filter]

        if user.get('fix_overflow') == True:
            overflow_filter = OverflowFilter(cache, department, courses, user)
            filters.append(overflow_filter)
            
        filters.extend([
            session_filter, SignatureFilter(cache), max_session_filter, carryover_filter, duplicate_filter, retake_filter1, level_filter,
            HeadFilter(cache),
            course_filter, session_filter, carryover_filter, retake_filter2, waiver_filter, elect_filter, level_filter, miss_filter,
            stop
        ])

        self.evaluate(filters)
         
        self.scored_results = results
        self.invalid_results = []
        self.invalid_results.extend(course_filter.reject)
        self.invalid_results.extend(cache['reject'])
        review = 'NO'
        if len(self.invalid_results) > 0 or cache['review']:
            if len(course_filter.reject) > 0:
                cache['review_flags'].append('unknown-course')
            review = 'YES'

        review_flags = ''
        for f in set(cache['review_flags']):
            review_flags += f + ', '
        
        outstanding = ''
        for c in stop.outstanding:
            outstanding += c['code'] + ', '

        waiver = ''
        for w in stop.waivers:
            waiver += w['code'] + ', '
        
        response = {
            'status': 'success', 'message': '', 'level_data': levels, 'user': user, 'review': review,
            'outstanding': outstanding.removesuffix(', '), 'review_flags': review_flags.removesuffix(', '),
            'waiver': waiver.removesuffix(', '),
        }
        print('Written {} results'.format(len(self.scored_results)))

        # step 4: remove unused sheets
        if self._wb != None:
            for sheet in _wb.worksheets:
                if sheet[_sheetMap['session']].value == None:
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
