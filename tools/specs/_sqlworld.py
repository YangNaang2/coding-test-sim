"""SQL 문제 공통 테이블 정의와 채점용 데이터 생성기."""
import datetime as dt


def col(name, typ, desc, nullable=False):
    return {'name': name, 'type': typ, 'nullable': nullable, 'desc': desc}


USERS = {'name': 'USERS', 'desc': '회원 정보', 'columns': [
    col('USER_ID', 'INT', '회원 ID'),
    col('NAME', 'VARCHAR(20)', '이름'),
    col('REGION', 'VARCHAR(20)', '거주 지역. 입력하지 않았으면 NULL', True),
    col('JOINED_AT', 'DATE', '가입일'),
]}
ACCOUNTS = {'name': 'ACCOUNTS', 'desc': '증권 계좌', 'columns': [
    col('ACCOUNT_ID', 'INT', '계좌 ID'),
    col('USER_ID', 'INT', '계좌 주인의 회원 ID'),
    col('STATUS', 'VARCHAR(10)', "계좌 상태: 'ACTIVE'(사용), 'DORMANT'(휴면), 'CLOSED'(해지)"),
    col('BALANCE', 'BIGINT', '예수금 잔고(원)'),
    col('OPENED_AT', 'DATE', '개설일'),
]}
STOCKS = {'name': 'STOCKS', 'desc': '상장 종목', 'columns': [
    col('CODE', 'VARCHAR(6)', '종목 코드'),
    col('NAME', 'VARCHAR(30)', '종목명'),
    col('MARKET', 'VARCHAR(10)', "시장: 'KOSPI' 또는 'KOSDAQ'"),
    col('SECTOR', 'VARCHAR(10)', "업종: 'IT', 'BIO', 'FIN', 'AUTO', 'CHEM'. 분류 전이면 NULL", True),
    col('LISTED_AT', 'DATE', '상장일'),
]}
ORDERS = {'name': 'ORDERS', 'desc': '주문', 'columns': [
    col('ORDER_ID', 'INT', '주문 ID'),
    col('ACCOUNT_ID', 'INT', '주문한 계좌 ID. 시스템 점검용 주문이면 NULL', True),
    col('CODE', 'VARCHAR(6)', '종목 코드'),
    col('SIDE', 'VARCHAR(4)', "'BUY'(매수) 또는 'SELL'(매도)"),
    col('PRICE', 'INT', '주문 가격(원)'),
    col('QTY', 'INT', '주문 수량(주)'),
    col('STATUS', 'VARCHAR(10)', "'FILLED'(체결), 'CANCELED'(취소), 'PENDING'(대기)"),
    col('ORDERED_AT', 'DATETIME', '주문 시각'),
]}
TRADES = {'name': 'TRADES', 'desc': '체결 내역', 'columns': [
    col('TRADE_ID', 'INT', '체결 ID'),
    col('ORDER_ID', 'INT', '주문 ID'),
    col('PRICE', 'INT', '체결 가격(원)'),
    col('QTY', 'INT', '체결 수량(주)'),
    col('TRADED_AT', 'DATETIME', '체결 시각'),
]}
DAILY_PRICES = {'name': 'DAILY_PRICES', 'desc': '일별 시세', 'columns': [
    col('CODE', 'VARCHAR(6)', '종목 코드'),
    col('TRADE_DATE', 'DATE', '거래일'),
    col('CLOSE_PRICE', 'INT', '종가(원)'),
    col('VOLUME', 'BIGINT', '거래량(주)'),
]}

SURNAMES = '김이박최정강조윤장임한오서신권황안송류홍'
GIVEN = ['민준', '서연', '도윤', '하은', '지호', '수아', '예준', '지유', '시우', '서윤', '주원', '하린', '지훈', '채원',
         '건우', '다은', '현우', '소율', '우진', '예린', '선우', '유나', '연우', '은서', '정우', '가은', '준서', '나연']
REGIONS = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '제주']
SECTORS = ['IT', 'BIO', 'FIN', 'AUTO', 'CHEM']
PREFIX = ['한빛', '누리', '다온', '새솔', '가람', '온새', '푸른', '하늘', '미래', '은빛', '바른', '참길', '세움', '라온',
          '해솔', '별빛', '아라', '도담', '이음', '나래']
SUFFIX = {'IT': ['소프트', '테크', '전자', '시스템'], 'BIO': ['바이오', '제약', '헬스'], 'FIN': ['금융', '증권', '캐피탈'],
          'AUTO': ['모터스', '오토', '부품'], 'CHEM': ['화학', '소재', '케미칼'], None: ['홀딩스', '산업']}


def day(rng, start, end):
    a, b = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    return (a + dt.timedelta(days=rng.randint(0, (b - a).days))).isoformat()


def moment(rng, start, end):
    d = day(rng, start, end)
    return '%s %02d:%02d:%02d' % (d, rng.randint(9, 15), rng.randint(0, 59), rng.randint(0, 59))


def name(rng):
    return rng.choice(SURNAMES) + rng.choice(GIVEN)


def users(rng, n, start_id=1):
    return [[start_id + k, name(rng), rng.choice(REGIONS) if rng.random() > 0.15 else None,
             day(rng, '2018-01-01', '2026-09-30')] for k in range(n)]


def accounts(rng, user_rows, start_id=1001, max_per_user=3):
    out, aid = [], start_id
    for u in user_rows:
        for _ in range(rng.randint(0, max_per_user)):
            st = rng.choices(['ACTIVE', 'DORMANT', 'CLOSED'], [70, 15, 15])[0]
            bal = int(10 ** rng.uniform(3, 8.6)) if rng.random() > 0.05 else 0
            out.append([aid, u[0], st, bal, day(rng, '2018-01-01', '2026-09-30')])
            aid += 1
    return out


def stocks(rng, n, start_code=100000):
    out = []
    codes = rng.sample(range(start_code, start_code + n * 7), n)
    for c in codes:
        sec = rng.choice(SECTORS) if rng.random() > 0.08 else None
        out.append(['%06d' % c, rng.choice(PREFIX) + rng.choice(SUFFIX[sec]), rng.choice(['KOSPI', 'KOSDAQ']), sec,
                    day(rng, '2000-01-01', '2026-09-30')])
    return out


def orders(rng, n, account_ids, codes, start_id=1, start='2026-09-01', end='2026-11-30'):
    out = []
    for k in range(n):
        acc = rng.choice(account_ids) if rng.random() > 0.02 else None
        out.append([start_id + k, acc, rng.choice(codes), rng.choice(['BUY', 'SELL']), rng.randint(10, 3000) * 100,
                    rng.randint(1, 50), rng.choices(['FILLED', 'CANCELED', 'PENDING'], [70, 20, 10])[0],
                    moment(rng, start, end)])
    return out


def trading_days(start, end):
    a, b = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    out = []
    while a <= b:
        if a.weekday() < 5:
            out.append(a.isoformat())
        a += dt.timedelta(days=1)
    return out


def prices(rng, codes, start='2026-09-21', end='2026-11-06', missing=0.05):
    out = []
    days = trading_days(start, end)
    for c in codes:
        p = rng.randint(20, 5000) * 100
        for d in days:
            if rng.random() < missing:
                continue
            p = max(100, int(p * rng.uniform(0.95, 1.05)) // 100 * 100)
            out.append([c, d, p, rng.randint(1000, 2000000)])
    return out
