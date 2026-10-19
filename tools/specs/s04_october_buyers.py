import _sqlworld as w

META = {
    'id': 'S04',
    'title': '10월 매수 체결 상위 회원',
    'level': 2,
    'tags': ['다중 JOIN', 'GROUP BY', 'HAVING', '날짜 범위'],
    'ordered': True,
    'description': '''
<p><code>ORDERS</code>, <code>ACCOUNTS</code>, <code>USERS</code> 테이블을 이용해, <b>2026년 10월</b>에 주문한 <b>매수</b>(<code>SIDE = 'BUY'</code>) 주문 중 <b>체결된</b>(<code>STATUS = 'FILLED'</code>) 주문의 금액(<code>PRICE × QTY</code>) 합계가 <b>1,000,000원 이상</b>인 회원을 조회하려 합니다. 주문 시각은 <code>ORDERED_AT</code>입니다.</p>
<p>회원 ID(<code>USER_ID</code>), 이름(<code>NAME</code>), 합계(<code>TOTAL_AMOUNT</code>)를 조회하는 SQL 문을 작성해 주세요. 결과는 합계 내림차순으로, 같으면 회원 ID 오름차순으로 정렬해 주세요.</p>
''',
    'explanation': '''
<p>ORDERS → ACCOUNTS → USERS 순서로 JOIN한 뒤, 행 조건은 WHERE에, 집계 결과 조건은 HAVING에 둡니다.</p>
<ul>
<li><b>날짜 범위</b>: <code>ORDERED_AT</code>은 시각까지 있는 DATETIME입니다. <code>BETWEEN '2026-10-01' AND '2026-10-31'</code>은 <code>'2026-10-31 00:00:00'</code>까지만 포함해서 10월 31일 낮 주문이 빠집니다. <code>ORDERED_AT &gt;= '2026-10-01' AND ORDERED_AT &lt; '2026-11-01'</code>처럼 다음 달 1일 미만으로 쓰거나, <code>DATE_FORMAT(ORDERED_AT, '%Y-%m') = '2026-10'</code>(MySQL), <code>TO_CHAR(ORDERED_AT, 'YYYY-MM') = '2026-10'</code>(Oracle)을 쓰세요.</li>
<li>합계 조건 <code>SUM(PRICE * QTY) &gt;= 1000000</code>은 그룹을 만든 뒤에 판단하므로 HAVING에 씁니다.</li>
<li>ACCOUNT_ID가 NULL인 점검용 주문은 JOIN에서 자연히 빠집니다.</li>
</ul>
''',
}

SCHEMA = [w.USERS, w.ACCOUNTS, w.ORDERS]


def sample():
    return {
        'USERS': [[1, '김민준', '서울', '2020-03-01'], [2, '이서연', None, '2021-07-15'], [3, '박도윤', '부산', '2019-11-30']],
        'ACCOUNTS': [[1001, 1, 'ACTIVE', 0, '2020-03-01'], [1002, 2, 'ACTIVE', 0, '2021-07-15'],
                     [1003, 3, 'ACTIVE', 0, '2019-11-30'], [1004, 1, 'DORMANT', 0, '2022-05-05']],
        'ORDERS': [
            [1, 1001, '310010', 'BUY', 50000, 10, 'FILLED', '2026-10-02 09:12:00'],
            [2, 1004, '310020', 'BUY', 25000, 20, 'FILLED', '2026-10-31 14:30:00'],
            [3, 1002, '310010', 'BUY', 70000, 20, 'CANCELED', '2026-10-05 10:00:00'],
            [4, 1002, '310030', 'BUY', 99000, 10, 'FILLED', '2026-10-15 11:00:00'],
            [5, 1003, '310010', 'SELL', 80000, 50, 'FILLED', '2026-10-20 13:00:00'],
            [6, 1003, '310040', 'BUY', 120000, 10, 'FILLED', '2026-09-30 15:20:00'],
            [7, None, '310010', 'BUY', 999900, 10, 'FILLED', '2026-10-10 09:00:00'],
        ],
    }


def hidden(rng):
    users = w.users(rng, 120)
    accounts = w.accounts(rng, users)
    ids = [a[0] for a in accounts]
    orders = w.orders(rng, 1500, ids, ['%06d' % (310000 + k) for k in range(30)], start='2026-09-25', end='2026-11-05')
    oid = 90000
    # 10월 31일 오후, 11월 1일 0시, 정확히 1,000,000원 경계를 넣는다
    for k, acc in enumerate(ids[:15]):
        when = ['2026-10-31 15:20:00', '2026-11-01 00:00:00', '2026-10-01 00:00:00'][k % 3]
        orders.append([oid, acc, '310001', 'BUY', 100000, 10, 'FILLED', when])
        oid += 1
    rng.shuffle(orders)
    return {'USERS': users, 'ACCOUNTS': accounts, 'ORDERS': orders}


SOLUTION = '''
SELECT U.USER_ID, U.NAME, SUM(O.PRICE * O.QTY) AS TOTAL_AMOUNT
FROM ORDERS O
JOIN ACCOUNTS A ON O.ACCOUNT_ID = A.ACCOUNT_ID
JOIN USERS U ON A.USER_ID = U.USER_ID
WHERE O.SIDE = 'BUY'
  AND O.STATUS = 'FILLED'
  AND O.ORDERED_AT >= '2026-10-01'
  AND O.ORDERED_AT < '2026-11-01'
GROUP BY U.USER_ID, U.NAME
HAVING SUM(O.PRICE * O.QTY) >= 1000000
ORDER BY TOTAL_AMOUNT DESC, U.USER_ID;
'''

ALT = [
    "SELECT U.USER_ID, U.NAME, SUM(O.PRICE * O.QTY) AS TOTAL_AMOUNT FROM USERS U "
    "JOIN ACCOUNTS A ON U.USER_ID = A.USER_ID JOIN ORDERS O ON O.ACCOUNT_ID = A.ACCOUNT_ID "
    "WHERE O.SIDE = 'BUY' AND O.STATUS = 'FILLED' AND DATE_FORMAT(O.ORDERED_AT, '%Y-%m') = '2026-10' "
    "GROUP BY U.USER_ID, U.NAME HAVING TOTAL_AMOUNT >= 1000000 ORDER BY 3 DESC, 1",
    "SELECT U.USER_ID, U.NAME, SUM(O.PRICE * O.QTY) TOTAL_AMOUNT FROM ORDERS O, ACCOUNTS A, USERS U "
    "WHERE O.ACCOUNT_ID = A.ACCOUNT_ID AND A.USER_ID = U.USER_ID AND O.SIDE = 'BUY' AND O.STATUS = 'FILLED' "
    "AND TO_CHAR(O.ORDERED_AT, 'YYYY-MM') = '2026-10' GROUP BY U.USER_ID, U.NAME "
    "HAVING SUM(O.PRICE * O.QTY) >= 1000000 ORDER BY TOTAL_AMOUNT DESC, U.USER_ID",
]

WRONG = {
    "BETWEEN '10-01' AND '10-31'": SOLUTION.replace("O.ORDERED_AT >= '2026-10-01'\n  AND O.ORDERED_AT < '2026-11-01'",
                                                    "O.ORDERED_AT BETWEEN '2026-10-01' AND '2026-10-31'"),
    '체결 상태 조건 누락': SOLUTION.replace("  AND O.STATUS = 'FILLED'\n", ''),
    '합계 > 1,000,000 (경계 미포함)': SOLUTION.replace('>= 1000000', '> 1000000'),
}
