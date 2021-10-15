# Touch not
import math
def rectify(sessions):
    if len(sessions.keys()) == 0:
        return []
    s = [0,0,0,0,0,0,0]
    
    ss = []
    ss.extend(sessions.keys())
    ss.sort()

    ma = max(ss)
    m_sem = sessions[ma] % 100

    for sk in ss:
        if s[math.floor(sessions[sk] / 100) - 1] == 0:
            s[math.floor(sessions[sk] / 100) - 1] = sk
            del sessions[sk]
    
    m = min(ss)
    i = s.index(m)
    for j in range(i):
        s[j] = m - i + j

    ss = []
    ss.extend(sessions.keys())
    ss.sort()
    for sk in ss:
        st = 0
        en = 0
        for j in range(6):
            if sk > s[j] and s[j + 1] == 0 and st == 0: 
                st = j + 1
            elif st > 0 and s[j + 1] > 0:
                if s[j + 1] > sk:
                    en = j
                else:
                    st = 0
        if en == 0 or en - st == 0:
            s[st] = sk
        else:
            inx = min([en-st, sk - s[st - 1]])
            s[st + inx] = sk
    
    for j in range(6):
        if s[j + 1] == 0 and s[j] != 0:
            try:
                s.index(s[j] + 1)
            except:
                s[j + 1] = s[j] + 1
    s.sort()
    for j in range(6, 0, -1):
        if s[j - 1] == 0: 
            s[j - 1] = s[j] - 1
    return {'sessions': s, 'last_sem': (s.index(ma) + 1) * 100 + m_sem}