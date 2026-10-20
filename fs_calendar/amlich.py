"""Âm lịch Việt Nam (thuật toán Hồ Ngọc Đức, múi giờ +7) -- cài độc lập để ĐỐI CHIẾU với vnlunar trước khi đưa
số liệu lịch vào kịch bản (vnlunar sai thần/trực/nạp âm, nên không tin một nguồn).

    solar2lunar(dd, mm, yy) -> (ngày âm, tháng âm, năm âm, nhuận 0/1)
    lunar2solar(ld, lm, ly, leap) -> (dd, mm, yy)
"""
import math

TZ = 7.0


def jd_from_date(dd, mm, yy):
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_date(jd):
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return day, month, year


def _new_moon(k):
    T = k / 1236.85
    T2, T3 = T * T, T * T * T
    dr = math.pi / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return Jd1 + C1 - deltat


def new_moon_day(k):
    return int(math.floor(_new_moon(k) + 0.5 + TZ / 24))


def _sun_longitude(jdn):
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = math.pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = (L0 + DL) * dr
    # 15/10/2026: int() cắt về 0 nên trước năm 2000 (T < 0) kinh độ ra âm -> sai tháng 11 / tháng nhuận
    # (Tết 1979, 1982, 1985, 1987, 1990, 1993, 1998 lệch một tháng). Bản gốc Hồ Ngọc Đức dùng floor.
    L = L - math.pi * 2 * math.floor(L / (math.pi * 2))
    return L


def sun_longitude(day_number):
    return int(_sun_longitude(day_number - 0.5 - TZ / 24) / math.pi * 6)


def lunar_month11(yy):
    off = jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = new_moon_day(k)
    if sun_longitude(nm) >= 9:
        nm = new_moon_day(k - 1)
    return nm


def leap_month_offset(a11):
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    arc = sun_longitude(new_moon_day(k + i))
    while True:
        last = arc
        i += 1
        arc = sun_longitude(new_moon_day(k + i))
        if not (arc != last and i < 14):
            break
    return i - 1


def solar2lunar(dd, mm, yy):
    day_number = jd_from_date(dd, mm, yy)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = new_moon_day(k + 1)
    if month_start > day_number:
        month_start = new_moon_day(k)
    a11 = lunar_month11(yy)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = lunar_month11(yy - 1)
    else:
        lunar_year = yy + 1
        b11 = lunar_month11(yy + 1)
    lunar_day = day_number - month_start + 1
    diff = int((month_start - a11) / 29)
    leap = 0
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_diff = leap_month_offset(a11)
        if diff >= leap_diff:
            lunar_month = diff + 10
            if diff == leap_diff:
                leap = 1
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_day, lunar_month, lunar_year, leap


def lunar2solar(ld, lm, ly, leap=0):
    if lm < 11:
        a11, b11 = lunar_month11(ly - 1), lunar_month11(ly)
    else:
        a11, b11 = lunar_month11(ly), lunar_month11(ly + 1)
    k = int(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = lm - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = leap_month_offset(a11)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if leap and lm != leap_month:
            raise ValueError("không có tháng nhuận này")
        if leap or off >= leap_off:
            off += 1
    month_start = new_moon_day(k + off)
    return jd_to_date(month_start + ld - 1)


def month_lengths(ly):
    """[(tháng, nhuận, ngày dương lịch mùng 1, số ngày)] của năm âm ly."""
    out = []
    import datetime as dt
    d = dt.date(*reversed(lunar2solar(1, 1, ly)))
    end = dt.date(*reversed(lunar2solar(1, 1, ly + 1)))
    cur = None
    while d < end:
        ldd, lm, lyy, lp = solar2lunar(d.day, d.month, d.year)
        if ldd == 1:
            cur = [lm, lp, d, 0]
            out.append(cur)
        cur[3] += 1
        d += dt.timedelta(days=1)
    return out
