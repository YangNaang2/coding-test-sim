import _sqlworld as w

META = {
    'id': 'S03',
    'title': '휴면 계좌 보유 회원',
    'level': 1,
    'tags': ['JOIN', 'DISTINCT', 'NULL 처리'],
    'ordered': True,
    'description': '''
<p>휴면 계좌 안내문을 보내려고 합니다. <code>USERS</code>와 <code>ACCOUNTS</code> 테이블에서 상태가 <code>'DORMANT'</code>인 계좌를 하나 이상 가진 회원을 조회하려 합니다.</p>
<p>회원 ID(<code>USER_ID</code>), 이름(<code>NAME</code>), 지역(<code>REGION</code>)을 조회하는 SQL 문을 작성해 주세요. 지역이 NULL이면 <code>'미지정'</code>으로 출력합니다. 휴면 계좌를 여러 개 가진 회원도 <b>한 번만</b> 출력하고, 결과는 회원 ID 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<ul>
<li>회원과 계좌를 <code>USER_ID</code>로 JOIN하고 <code>STATUS = 'DORMANT'</code>로 거릅니다.</li>
<li>휴면 계좌가 2개면 JOIN 결과에 같은 회원이 2번 나오므로 <code>DISTINCT</code>(또는 GROUP BY)가 필요합니다.</li>
<li>NULL 대체: 표준 <code>COALESCE(REGION, '미지정')</code>, MySQL <code>IFNULL</code>, Oracle <code>NVL</code>.</li>
<li><code>WHERE USER_ID IN (SELECT USER_ID FROM ACCOUNTS WHERE STATUS = 'DORMANT')</code>처럼 서브쿼리로 쓰면 중복이 생기지 않습니다.</li>
</ul>
''',
}

SCHEMA = [w.USERS, w.ACCOUNTS]


def sample():
    return {
        'USERS': [
            [1, '김민준', '서울', '2020-03-01'],
            [2, '이서연', None, '2021-07-15'],
            [3, '박도윤', '부산', '2019-11-30'],
            [4, '최하은', None, '2022-01-05'],
        ],
        'ACCOUNTS': [
            [1001, 1, 'ACTIVE', 1500000, '2020-03-01'],
            [1002, 2, 'DORMANT', 0, '2021-07-15'],
            [1003, 2, 'DORMANT', 3000, '2021-08-01'],
            [1004, 3, 'CLOSED', 0, '2019-11-30'],
            [1005, 4, 'DORMANT', 52000, '2022-01-05'],
            [1006, 1, 'ACTIVE', 0, '2023-02-02'],
        ],
    }


def hidden(rng):
    users = w.users(rng, 250)
    accounts = w.accounts(rng, users)
    # 휴면 계좌를 여러 개 가진 회원, 지역 NULL 회원을 확실히 넣는다
    aid = 9000
    for u in users[:12]:
        for _ in range(2):
            accounts.append([aid, u[0], 'DORMANT', rng.randint(0, 100000), '2020-01-01'])
            aid += 1
        if u[0] % 3 == 0:
            u[2] = None
    accounts.append([aid, users[-1][0], 'dormant', 0, '2020-01-01'])   # 대소문자가 다른 값은 해당 안 됨
    rng.shuffle(accounts)
    return {'USERS': users, 'ACCOUNTS': accounts}


SOLUTION = '''
SELECT DISTINCT U.USER_ID, U.NAME, COALESCE(U.REGION, '미지정') AS REGION
FROM USERS U
JOIN ACCOUNTS A ON U.USER_ID = A.USER_ID
WHERE A.STATUS = 'DORMANT'
ORDER BY U.USER_ID;
'''

ALT = [
    "SELECT USER_ID, NAME, IFNULL(REGION, '미지정') AS REGION FROM USERS "
    "WHERE USER_ID IN (SELECT USER_ID FROM ACCOUNTS WHERE STATUS = 'DORMANT') ORDER BY USER_ID",
    "SELECT U.USER_ID, U.NAME, NVL(U.REGION, '미지정') REGION FROM USERS U, ACCOUNTS A "
    "WHERE U.USER_ID = A.USER_ID AND A.STATUS = 'DORMANT' GROUP BY U.USER_ID, U.NAME, U.REGION ORDER BY U.USER_ID",
]

WRONG = {
    'DISTINCT 누락': "SELECT U.USER_ID, U.NAME, COALESCE(U.REGION, '미지정') FROM USERS U JOIN ACCOUNTS A "
                   "ON U.USER_ID = A.USER_ID WHERE A.STATUS = 'DORMANT' ORDER BY U.USER_ID",
    'NULL 대체 누락': "SELECT DISTINCT U.USER_ID, U.NAME, U.REGION FROM USERS U JOIN ACCOUNTS A "
                    "ON U.USER_ID = A.USER_ID WHERE A.STATUS = 'DORMANT' ORDER BY U.USER_ID",
    '휴면 조건을 != ACTIVE로': "SELECT DISTINCT U.USER_ID, U.NAME, COALESCE(U.REGION, '미지정') FROM USERS U JOIN ACCOUNTS A "
                          "ON U.USER_ID = A.USER_ID WHERE A.STATUS <> 'ACTIVE' ORDER BY U.USER_ID",
}
