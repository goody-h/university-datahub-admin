from models.config import Config
from models.course import Course
from models.department import Department
from models.result import Result
from models.student import Student
from models.upload import Upload
from services.time import Time
import json

class Stager(object):
    def __init__(self, session, is_writer) -> None:
        super().__init__()
        self.session = session
        self.is_writer = is_writer
        self.staged_records = None
        self.timer = Time()

    def stage_config(self, crypto = None):
        if self.is_writer:
            records = self.session.query(Config).filter(Config.annotation == "key").all()
            for record in records:
                self.stage_record(record, 'config', crypto)

    def stage_results(self):
        if self.is_writer:
            records = self.session.query(Result).all()
            for record in records:
                self.stage_record(record, 'resultId')

    def stage_departments(self):
        if self.is_writer:
            records = self.session.query(Department).all()
            for record in records:
                self.stage_record(record, 'id')

    def stage_courses(self):
        if self.is_writer:
            records = self.session.query(Course).all()
            for record in records:
                self.stage_record(record, 'courseId')

    def stage_bio(self):
        if self.is_writer:
            records = self.session.query(Student).all()
            for record in records:
                self.stage_record(record, 'mat_no')

    def stage_record(self, record, primary, crypto = None):
        if self.is_writer:
            obj, string = self.serialize_object(record)
            upload = Upload(
                key = obj[primary],
                table = str(type(record)),
                value = string,
                _timestamp_ = self.timer.get_next_time_in_micro()
            )
            if crypto != None:
                upload._signature_ = crypto.sign(upload)
            self.session.merge(upload)
    
    def commit(self):
        self.session.commit()
        self.session.close()

    def serialize_object(self, obj):
        encoder = json.JSONEncoder(skipkeys=True, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys= True, default=lambda o: '<non-serializable>')
        value = encoder.encode(obj)
        if value == '"<non-serializable>"':
            obj = { attr: obj.__getattribute__(attr) for attr in dir(obj) if not callable(obj.__getattribute__(attr)) and self.is_serializable(obj.__getattribute__(attr)) and not attr.startswith('__') }
            value = encoder.encode(obj)
        return obj, value

    def is_serializable(self, value):
        try: json.JSONEncoder().encode(value)
        except: return False
        return True

    def get_update_stamp(self):
        stamp = self.session.query(Config).filter(Config.config == "update-stamp").first()
        if stamp != None:
            return int(stamp.value)
        return stamp

    def set_update_stamp(self, value):
        config = Config(
            config = "update-stamp",
            value = str(value),
            annotation = "update-stamp",
            status = "UP",
            _timestamp_ = self.timer.get_next_time_in_micro(),
            _signature_ =  ""
        )
        self.session.merge(config)

    def has_staged_records(self):
        self.staged_records = self.session.query(Upload).order_by(Upload._timestamp_).all()
        print(len(self.staged_records))
        return len(self.staged_records) > 0

    def push_to_remote(self, remote, crypto = None, pub_key = None, on_push = lambda c: None):
        if self.is_writer:
            total = len(self.staged_records)
            sum = 0
            self.staged_records = self.session.query(Upload).order_by(Upload._timestamp_).limit(100).all()
            remote_session = remote.Session()
            remote.session = remote_session
            try:
                while len(self.staged_records) > 0:
                    if not remote.has_lock():
                        print('no lock')
                        break
                    ts = self.get_update_stamp()
                    ps = 0
                    for record in self.staged_records:
                        stamp = None
                        table = str(record.table)
                        data = json.JSONDecoder().decode(record.value)
                        current, object = self.map_data_to_object(data, table)
                        if object != None:
                            current = current.first()
                        if object != None and ((current == None and data['status'] == 'DELETE')
                            or (current != None and int(current._timestamp_) == data['_timestamp_'] 
                                and str(current._signature_) == data['_signature_'])):
                            object.status = data.get('status')
                            time = self.timer.get_next_time_in_micro()
                            object._timestamp_ = time
                            object._signature_ = data.get('_signature_')
                            stamp = time
                            if type(object) is Config:
                                if crypto.verify_signature(record, str(record._signature_)) or pub_key == None:
                                    remote_session.merge(object)
                                    ts = max(ts, stamp)
                            elif crypto.verify_signature(record, str(record._signature_)) or crypto.verify_signature(object, str(object._signature_)):
                                remote_session.merge(object)
                                ts = max(ts, stamp)
                        ps = max(ps, int(record._timestamp_))
                    if not remote.has_lock():
                        print('no lock')
                        break
                    remote_session.commit()
                    self.set_update_stamp(ts)
                    self.session.query(Upload).filter(Upload._timestamp_ <= ps).delete()
                    self.session.commit()
                    sum += len(self.staged_records)
                    try:
                        on_push('{}/{}'.format(sum, total))
                    except: pass
                    print('pushed {}'.format(len(self.staged_records)))
                    self.staged_records = self.session.query(Upload).order_by(Upload._timestamp_).limit(100).all()
                remote_session.close()
            except Exception as e:
                remote_session.close()
                raise e

    
    def assert_remote(self, remote, session):
         if remote.is_cancelled:
            session.close()
            assert False, "Remote session has ended" 

    def pull_from_remote(self, remote, crypto = None):
        session = remote.Session()
        remote.session = session
        try:
            self.assert_remote(remote, session)
            stamp = self.get_update_stamp()
            records = session.query(Config).filter(Config.annotation == "key", Config._timestamp_ > stamp).all()
            records.extend(session.query(Result).filter(Result._timestamp_ > stamp).all())
            records.extend(session.query(Department).filter(Department._timestamp_ > stamp).all())
            records.extend(session.query(Course).filter(Course._timestamp_ > stamp).all())
            records.extend(session.query(Student).filter(Student._timestamp_ > stamp).all())
            for update in records:
                self.assert_remote(remote, session)
                obj, _ = self.serialize_object(update)
                current, object = self.map_data_to_object(obj, str(type(update)))
                c_data = current.first()
                if c_data == None or int(update._timestamp_) > int(c_data._timestamp_) or str(update._signature_) == str(c_data._signature_) or type(update) is Config:
                    if str(update.status) == "DELETE":
                        current.delete()
                    else:
                        object._timestamp_ = self.timer.get_next_time_in_micro()
                        object._signature_ = obj.get('_signature_')
                        self.session.merge(object)
                stamp = max(stamp, int(update._timestamp_))
            
            self.assert_remote(remote, session)
            self.set_update_stamp(stamp)
            session.close()
            self.session.commit()
        except Exception as e:
            session.close()
            raise e


    def map_data_to_object(self, data, table):
        object = None
        current = None
        if table == str(type(Config())):
            current = self.session.query(Config).filter(Config.config == data.get('config'))
            object = Config(
                config = data.get('config'),
                value = data.get('value'),
                annotation = data.get('annotation')
            )
        elif table == str(type(Result())):
            current = self.session.query(Result).filter(Result.resultId == data.get('resultId'))
            object = Result(
                resultId = data.get('resultId'),
                batchId = data.get('batchId'),
                session = data.get('session'),
                courseId = data.get('courseId'),
                courseCode = data.get('courseCode'),
                mat_no = data.get('mat_no'),
                annotation = data.get('annotation'),
                score = data.get('score')
            )
        elif table == str(type(Course())):
            current = self.session.query(Course).filter(Course.courseId == data.get('courseId'))
            object = Course(
                courseId = data.get('courseId'),
                id = data.get('id'),
                code = data.get('code'),
                title = data.get('title'),
                cu = data.get('cu'),
                properties = data.get('properties'),
                level = data.get('level'),
                sem = data.get('sem'),
                department = data.get('department')
            )
        elif table == str(type(Department())):
            current = self.session.query(Department).filter(Department.id == data.get('id'))
            object = Department(
                id = data.get('id'),
                faculty = data.get('faculty'),
                department = data.get('department'),
                department_long = data.get('department_long'),
                code = data.get('code'),
                hod = data.get('hod'),
                semesters = data.get('semesters'),
                levels = data.get('levels'),
                summary = data.get('summary'),
                spreadsheet = data.get('spreadsheet'),
                max_cu = data.get('max_cu')
            )
        elif table == str(type(Student())):
            current = self.session.query(Student).filter(Student.mat_no == data.get('mat_no'))
            object = Student(
                batchId = data.get('batchId'),
                mat_no = data.get('mat_no'),
                state = data.get('state'),
                sex = data.get('sex'),
                marital_status = data.get('marital_status'),
                department = data.get('department'),
                annotation = data.get('annotation'),
                last_name = data.get('last_name'),
                first_name = data.get('first_name'),
                other_names = data.get('other_names')
            )
        return current, object
