import _sqlworld as w

META = {
    'id': 'S05',
    'title': '주문 이력 없는 계좌',
    'level': 2,
    'tags': ['LEFT JOIN', 'IS NULL', 'NOT EXISTS', 'NOT IN 함정'],
    'ordered': True,
    'description': '''
<p>계좌를 개설하고 <b>한 번도 주문하지 않은</b> 사용 중(<code>STATUS = 'ACTIVE'</code>) 계좌에 첫 거래 혜택을 안내하려 합니다. 취소된 주문이나 대기 중인 주문도 주문한 것으로 봅니다.</p>
<p><code>ACCOUNTS</code>, <code>USERS</code>, <code>ORDERS</code> 테이블에서 계좌 ID(<code>ACCOUNT_ID</code>), 회원 이름(<code>NAME</code>), 개설일(<code>OPENED_AT</code>)을 조회하는 SQL 문을 작성해 주세요. 결과는 개설일 오름차순으로, 같으면 계좌 ID 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<p>"없는 것 찾기"는 세 가지 방법이 있습니다.</p>
<ol>
<li><code>LEFT JOIN ORDERS O ON ...</code> 후 <code>WHERE O.ORDER_ID IS NULL</code></li>
<li><code>WHERE NOT EXISTS (SELECT 1 FROM ORDERS O WHERE O.ACCOUNT_ID = A.ACCOUNT_ID)</code></li>
<li><code>NOT IN</code>: 이 문제에서는 <b>틀립니다</b>. ORDERS.ACCOUNT_ID에 NULL(점검용 주문)이 있어서 <code>x NOT IN (1, 2, NULL)</code>은 항상 참이 될 수 없고(UNKNOWN), 결과가 0행이 됩니다. NOT IN을 쓰려면 서브쿼리에 <code>WHERE ACCOUNT_ID IS NOT NULL</code>을 붙여야 합니다.</li>
</ol>
<p>"취소된 주문도 주문"이므로 ORDERS의 상태로 거르면 안 됩니다.</p>
''',
}

SCHEMA = [w.USERS, w.ACCOUNTS, w.ORDERS]


def sample():
    return {
        'USERS': [[1, '김민준', '서울', '2020-03-01'], [2, '이서연', None, '2021-07-15'], [3, '박도윤', '부산', '2019-11-30']],
        'ACCOUNTS': [
            [1001, 1, 'ACTIVE', 1500000, '2020-03-01'],
            [1002, 2, 'ACTIVE', 0, '2021-07-15'],
            [1003, 3, 'ACTIVE', 30000, '2019-11-30'],
            [1004, 1, 'DORMANT', 0, '2018-05-05'],
            [1005, 3, 'ACTIVE', 0, '2019-11-30'],
        ],
        'ORDERS': [
            [1, 1001, '310010', 'BUY', 50000, 10, 'FILLED', '2026-10-02 09:12:00'],
            [2, 1002, '310020', 'BUY', 25000, 20, 'CANCELED', '2026-10-03 10:00:00'],
            [3, None, '310010', 'SELL', 1000, 1, 'FILLED', '2026-10-04 09:00:00'],
        ],
    }


def hidden(rng):
    users = w.users(rng, 200)
    accounts = w.accounts(rng, users)
    ids = [a[0] for a in accounts]
    rng.shuffle(ids)
    active = [i for i in ids]
    orders = w.orders(rng, 700, active[:len(active) // 2], ['%06d' % (310000 + k) for k in range(20)])
    oid = 80000
    for acc in active[len(active) // 2: len(active) // 2 + 20]:
        orders.append([oid, acc, '310001', 'BUY', 1000, 1, rng.choice(['CANCELED', 'PENDING']), '2026-10-10 10:00:00'])
        oid += 1
    for _ in range(5):
        orders.append([oid, None, '310002', 'SELL', 1000, 1, 'FILLED', '2026-10-11 10:00:00'])
        oid += 1
    # 같은 날 개설한 계좌를 ID 내림차순으로 추가
    for k, aid in enumerate([7090, 7080, 7070]):
        accounts.append([aid, users[k][0], 'ACTIVE', 0, '2024-04-04'])
    rng.shuffle(orders)
    return {'USERS': users, 'ACCOUNTS': accounts, 'ORDERS': orders}


SOLUTION = '''
SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT
FROM ACCOUNTS A
JOIN USERS U ON A.USER_ID = U.USER_ID
LEFT JOIN ORDERS O ON A.ACCOUNT_ID = O.ACCOUNT_ID
WHERE A.STATUS = 'ACTIVE'
  AND O.ORDER_ID IS NULL
ORDER BY A.OPENED_AT, A.ACCOUNT_ID;
'''

ALT = [
    "SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT FROM ACCOUNTS A JOIN USERS U ON A.USER_ID = U.USER_ID "
    "WHERE A.STATUS = 'ACTIVE' AND NOT EXISTS (SELECT 1 FROM ORDERS O WHERE O.ACCOUNT_ID = A.ACCOUNT_ID) "
    "ORDER BY A.OPENED_AT, A.ACCOUNT_ID",
    "SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT FROM ACCOUNTS A JOIN USERS U ON A.USER_ID = U.USER_ID "
    "WHERE A.STATUS = 'ACTIVE' AND A.ACCOUNT_ID NOT IN (SELECT ACCOUNT_ID FROM ORDERS WHERE ACCOUNT_ID IS NOT NULL) "
    "ORDER BY 3, 1",
]

WRONG = {
    'NOT IN (NULL 포함)': "SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT FROM ACCOUNTS A JOIN USERS U ON A.USER_ID = U.USER_ID "
                        "WHERE A.STATUS = 'ACTIVE' AND A.ACCOUNT_ID NOT IN (SELECT ACCOUNT_ID FROM ORDERS) "
                        "ORDER BY A.OPENED_AT, A.ACCOUNT_ID",
    '체결 주문만 주문으로 봄': "SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT FROM ACCOUNTS A JOIN USERS U ON A.USER_ID = U.USER_ID "
                       "LEFT JOIN ORDERS O ON A.ACCOUNT_ID = O.ACCOUNT_ID AND O.STATUS = 'FILLED' "
                       "WHERE A.STATUS = 'ACTIVE' AND O.ORDER_ID IS NULL ORDER BY A.OPENED_AT, A.ACCOUNT_ID",
    '계좌 상태 조건 누락': "SELECT A.ACCOUNT_ID, U.NAME, A.OPENED_AT FROM ACCOUNTS A JOIN USERS U ON A.USER_ID = U.USER_ID "
                     "LEFT JOIN ORDERS O ON A.ACCOUNT_ID = O.ACCOUNT_ID WHERE O.ORDER_ID IS NULL "
                     "ORDER BY A.OPENED_AT, A.ACCOUNT_ID",
}
