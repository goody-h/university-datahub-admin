# Whoops! I touched it
import math
def rectify(session_map, levels = 7, semesters = 2, missed_sessions = None):
    if len(session_map.keys()) == 0:
        return []

    if missed_sessions != None:
        for session in missed_sessions:
            if session_map.get(session) != None:
                session_map.pop(session)

    rectified_sessions = []
    for i in range(0, levels):
        rectified_sessions.append(0)
    
    sessions = []
    sessions.extend(session_map.keys())
    sessions.sort()

    max_session = max(sessions)
    max_semester = max(session_map.values())
    previous_level = -1

    for session in sessions:
        level = math.floor(session_map[session] / 100) - 1
        if previous_level >= len(rectified_sessions) - 1:
            break
        if rectified_sessions[level] == 0:
            rectified_sessions[level] = session
            if level > 0:
                reverse = 1
                for i in range(level - 1, -1, -1):
                    if i == previous_level:
                        break
                    new_session = session - reverse
                    if missed_sessions != None:
                        while missed_sessions.count(new_session) > 0:
                            reverse += 1
                            new_session = session - reverse
                    if rectified_sessions.count(new_session) > 0:
                        previous_level = rectified_sessions.index(new_session) - 1
                    rectified_sessions[i] = new_session
                    reverse += 1
            previous_level = level
        else:
            previous_level += 1
            rectified_sessions[previous_level] = session 

    for j in range(levels - 1):
        if rectified_sessions[j + 1] == 0 and rectified_sessions[j] != 0:
            new_session = rectified_sessions[j] + 1
            if missed_sessions != None:
                while missed_sessions.count(new_session) > 0:
                    new_session += 1
            rectified_sessions[j + 1] = new_session

    try:
        i = rectified_sessions.index(max_session) + 1
        if i * 100 >= max_semester:
            max_semester = semesters
        else:
            max_semester = max_semester % 100
    except:
        max_session = rectified_sessions[len(rectified_sessions) - 1]
        max_semester = semesters
    
    return {'sessions': rectified_sessions, 'last_sem': (rectified_sessions.index(max_session) + 1) * 100 + max_semester}