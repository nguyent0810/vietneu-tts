#!/usr/bin/env python3
"""Deterministic semantic scene selector for long-form plan rows (ticket #51)."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'library/scenes/catalog.json'
CHANNELS = ROOT / 'library/channels'
OUT_DIR = ROOT / 'output/cl_staging/long/out'
ATLAS = ROOT / 'chunks_cache/geo/countries-50m.json'
HOLD_MAX_S = 22.0
FS_ONLY = {'napam','hexagram','cuudieu','luoshu','compass','bagua','chiwheel','wheel','elements'}

# Thành phố / điểm đã có toạ độ trong repo. Không tự đoán thêm.
# Bồ Đề Đạo Tràng: test_hf_longform.py. Quảng Bình Quan: hf_geo_region.py.
CITIES = {
 'Hà Nội':(105.8342,21.0278,'Vietnam'),'Huế':(107.5909,16.4637,'Vietnam'),'Sài Gòn':(106.6297,10.8231,'Vietnam'),
 'Thành phố Hồ Chí Minh':(106.6297,10.8231,'Vietnam'),'Đà Nẵng':(108.2022,16.0544,'Vietnam'),'Hội An':(108.338,15.88,'Vietnam'),
 'Tây An':(108.94,34.34,'China'),'Yên Tử':(106.7,21.1,'Vietnam'),'Thăng Long':(105.8342,21.0278,'Vietnam'),
 'Đại La':(105.8342,21.0278,'Vietnam'),'Mekong':(105.0,10.0,'Vietnam'),
 'Lâm Tỳ Ni':(83.276,27.469,'Nepal'),'Bồ Đề Đạo Tràng':(84.9913,24.6951,'India'),
 'Quảng Bình Quan':(106.62405,17.46334,'Vietnam')}
# Tên tiếng Việt → tên nước trong world-atlas mà hf_geo.bake vẽ được.
COUNTRY_ALIAS = {
 'Việt Nam':'Vietnam','Trung Quốc':'China','Ấn Độ':'India','Nepal':'Nepal','Nhật Bản':'Japan',
 'Hàn Quốc':'South Korea','Triều Tiên':'North Korea','Thái Lan':'Thailand','Lào':'Laos',
 'Campuchia':'Cambodia','Miến Điện':'Myanmar','Myanmar':'Myanmar','Đài Loan':'Taiwan',
 'Mông Cổ':'Mongolia','Bangladesh':'Bangladesh','Bhutan':'Bhutan','Sri Lanka':'Sri Lanka',
 'Indonesia':'Indonesia','Malaysia':'Malaysia','Singapore':'Singapore','Philippines':'Philippines',
 'Hoa Kỳ':'United States of America','Vương quốc Anh':'United Kingdom','nước Pháp':'France','nước Nga':'Russia'}
_GEO_CACHE: dict | None = None

_START = {'một','hai','ba','bốn','sáu','bảy','tám','chín','mười'}
_SCALE_NEXT = {'mươi','trăm','nghìn','ngàn','vạn','triệu','tỷ','tỉ'}
_MEASURE = {'mét','km','trận','lần','phần','tuổi','độ','cân','tạ','giờ','ngày','tháng','năm','suất','lượt','dặm','hộc','tấn','yến','ly','thước'}
_UNIT = {'không':0,'một':1,'mốt':1,'hai':2,'ba':3,'bốn':4,'tư':4,'năm':5,'lăm':5,'nhăm':5,'sáu':6,'bảy':7,'tám':8,'chín':9}
_CONTRAST = re.compile(r'\b(?:nhưng|trái lại|ngược lại|so với|cao hơn|thấp hơn|khác với|trong khi)\b')
_DIR_RE = re.compile(r'(?:hướng|phương|tọa)\s+(đông\s+bắc|đông\s+nam|tây\s+bắc|tây\s+nam|đông|tây|nam|bắc|trên|dưới)', re.I)
_DIR_MAP = {
 # Hướng chéo: compass hiện chỉ có ô Đông/Tây/Nam/Bắc/Trên/Dưới -> bỏ qua thay vì ép về Bắc/Nam (79br).
 'đông bắc':None,'đông nam':None,'tây bắc':None,'tây nam':None,
 'đông':('east','Đông'),'tây':('west','Tây'),'nam':('south','Nam'),'bắc':('north','Bắc'),'trên':('up','Trên'),'dưới':('down','Dưới')}
_LOCATIVE = ('ở ','tại ','đến ','tới ','từ ','gần ','thuộc ','ven ','phía ','thành phố','kinh thành','kinh đô','ngôi chùa','di tích','bản đồ','tỉnh ','sông ','núi ','đô thành')
_MENH_SKIP = re.compile(r'vâng mệnh|sứ mệnh|mệnh lệnh|tính mệnh|mệnh danh|mệnh hệ|mệnh trời')


def _norm(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').lower().replace('đ','d'))

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def load_yaml_or_json(path: Path) -> Any:
    raw=path.read_text(encoding='utf-8')
    try: return json.loads(raw)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise ValueError('profile không phải JSON-compatible YAML; cần PyYAML') from exc
        return yaml.safe_load(raw)

def load_profile(path: str | None, channel: str) -> dict:
    p=Path(path) if path else CHANNELS/f'{channel}.yaml'
    data=load_yaml_or_json(p)
    if 'canh' not in data: raise ValueError(f"profile thiếu khối canh: {p}")
    return data['canh']

def _atlas_centroids() -> dict[str, tuple[float, float]]:
    """Tâm bbox từng nước trong world-atlas mà hf_geo đọc. Thiếu file thì bỏ qua."""
    if not ATLAS.is_file():
        return {}
    topo=json.loads(ATLAS.read_text(encoding='utf-8'))
    sx, sy = topo['transform']['scale']
    tx, ty = topo['transform']['translate']
    arcs=topo['arcs']
    out={}
    for g in topo['objects']['countries']['geometries']:
        name=(g.get('properties') or {}).get('name')
        polys=g['arcs'] if g.get('type')=='MultiPolygon' else [g.get('arcs') or []]
        minx=miny=10**18; maxx=maxy=-10**18; seen=False
        for poly in polys:
            for ring in poly:
                for idx in ring:
                    arc=arcs[idx if idx>=0 else ~idx]
                    x=y=0
                    for dx, dy in arc:
                        x+=dx; y+=dy
                        minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y); seen=True
        if name and seen:
            out[name]=((minx+maxx)/2*sx+tx, (miny+maxy)/2*sy+ty)
    return out

def gazetteer() -> dict[str, tuple[float, float, str]]:
    global _GEO_CACHE
    if _GEO_CACHE is None:
        geo=dict(CITIES)
        cents=_atlas_centroids()
        for vi, en in COUNTRY_ALIAS.items():
            if vi not in geo and en in cents:
                lon, lat=cents[en]
                geo[vi]=(lon, lat, en)
        _GEO_CACHE=geo
    return _GEO_CACHE

def _lesson(text: str) -> bool:
    n=(text or '').lower()
    return bool(re.search(r'dạy (?:ta|chúng ta)|bài học', n))

def places_in(text: str) -> list[str]:
    """Địa danh gazetteer đang được dùng như nơi chốn, không phải câu triết lý."""
    if _lesson(text):
        return []
    n=_norm(text)
    occupied=[False]*len(n)
    found=[]
    cues=tuple(_norm(c) for c in _LOCATIVE)
    for name in sorted(gazetteer(), key=len, reverse=True):
        key=_norm(name)
        if not key:
            continue
        start=0
        while True:
            i=n.find(key, start)
            if i<0:
                break
            j=i+len(key)
            before=n[i-1] if i else ' '
            after=n[j] if j<len(n) else ' '
            start=j
            if before.isalnum() or after.isalnum() or any(occupied[i:j]):
                continue
            window=n[max(0,i-48):j+24]
            if not any(c in window for c in cues):
                continue
            for k in range(i,j):
                occupied[k]=True
            found.append((i, name))
    found.sort()
    return [name for _, name in found]

def _tokens(raw: str) -> list[str]:
    return re.findall(r'\d+(?:[.,]\d+)?%?|[^\W\d_]+', (raw or '').lower())

def _take_words(tokens: list[str], i: int):
    """(kind, value, end) hoặc None. kind year = mốc năm, không phải số liệu."""
    if i>=len(tokens):
        return None
    t0=tokens[i]
    nxt=tokens[i+1] if i+1<len(tokens) else ''
    if not (t0=='mười' or t0 in _START or (t0=='năm' and nxt in _SCALE_NEXT)):
        return None
    total=0; group=0; seen=False; j=i
    while j<len(tokens):
        t=tokens[j]
        nxt=tokens[j+1] if j+1<len(tokens) else ''
        prev=tokens[j-1] if j else ''
        if t in ('linh','lẻ') and j!=i:
            j+=1; continue
        if t=='mười':
            group+=10; seen=True; j+=1; continue
        if t=='mươi' and j!=i:
            ones=group%10
            group=group-ones+(ones or 1)*10
            seen=True; j+=1; continue
        if t=='trăm' and j!=i and group<10:
            group=(group or 1)*100; seen=True; j+=1; continue
        if t in ('nghìn','ngàn') and j!=i:
            total+=(group or 1)*1000; group=0; seen=True; j+=1; continue
        if t=='vạn' and j!=i:
            total+=(group or 1)*10000; group=0; seen=True; j+=1; continue
        if t=='triệu' and j!=i:
            total+=(group or 1)*1000000; group=0; seen=True; j+=1; continue
        if t in ('tỷ','tỉ') and j!=i:
            total+=(group or 1)*1000000000; group=0; seen=True; j+=1; continue
        if t in _UNIT and (j==i or t!='năm' or nxt in _SCALE_NEXT or prev in ('mươi','mười','lẻ','linh','trăm')):
            if t=='năm' and j!=i and prev not in ('mươi','mười','lẻ','linh','trăm') and nxt not in _SCALE_NEXT:
                break
            group+=_UNIT[t]; j+=1; continue
        break
    if j==i:
        return None
    value=total+group
    if not seen:
        # "một ngày" là mạo từ. "Tháng Ba năm 1974": chữ năm mở mốc năm, không phải đơn vị của số 3.
        meas=j<len(tokens) and tokens[j] in _MEASURE and value>=2
        if meas and tokens[j]=='năm':
            nxt=tokens[j+1] if j+1<len(tokens) else ''
            if nxt in _START or nxt=='mười' or re.fullmatch(r'\d+', nxt or ''):
                meas=False
        if not meas:
            return None
    prev=tokens[i-1] if i else ''
    if prev=='năm' and 1000<=value<=2100:
        return ('year', value, j)
    return ('qty', value, j)

def is_chapter(raw: str) -> bool:
    return bool(re.match(r'^\s*(?:\*\*)?\s*chương\s+\d+\b', raw or '', re.I))

def quantities(raw: str) -> list[float]:
    """Số liệu đo được. Bỏ tiêu đề chương, bỏ năm lịch sử đứng sau chữ 'năm'."""
    if is_chapter(raw):
        return []
    tokens=_tokens(raw)
    vals=[]; i=0
    while i<len(tokens):
        tok=tokens[i]
        if re.fullmatch(r'\d+(?:[.,]\d+)?%?', tok):
            num=float(tok.replace('%','').replace(',','.'))
            prev=tokens[i-1] if i else ''
            # Số có 4 chữ số trong khoảng năm lịch sử là mốc năm, không phải một trị số đếm.
            yearish=not tok.endswith('%') and num==int(num) and 1000<=num<=2100
            if yearish or prev in ('chương','kỷ'):
                i+=1; continue
            vals.append(num); i+=1; continue
        got=_take_words(tokens, i)
        if not got:
            i+=1; continue
        kind, value, j=got
        prev=tokens[i-1] if i else ''
        if kind=='qty' and prev!='kỷ':
            vals.append(float(value))
        i=max(j, i+1)
    return vals

def two_measurable_sides(text: str) -> bool:
    """Đối chiếu chỉ khi ít nhất hai vế, mỗi vế có một đối tượng đo được."""
    parts=_CONTRAST.split(_norm(text))
    if len(parts)<2:
        return False
    return sum(1 for p in parts if quantities(p))>=2

def has_list(text: str) -> bool:
    raw=(text or '').lower()
    ords=re.findall(r'thứ\s+(?:nhất|hai|ba|tư|năm|sáu|bảy|tám|chín|mười)', raw)
    if len(ords)>=2:
        return True
    m=re.search(r'(?:bao gồm|gồm có|các loại|ví dụ|chẳng hạn|gồm)\s*:?\s*([^.]{0,200})', raw)
    if not m:
        return False
    parts=[p.strip(' *:') for p in re.split(r',|\s+và\s+|\s+hay\s+', m.group(1)) if p.strip(' *')]
    # Mỗi mục phải ngắn. Dấu phẩy trong câu kể ("ví dụ … sử sách, qua nhiều lần") không phải danh sách.
    return len(parts)>=2 and all(len(p.split())<=8 for p in parts)

def extract_dirs(text: str) -> list[dict]:
    out=[]; seen=set()
    for m in _DIR_RE.finditer(text or ''):
        key=re.sub(r'\s+', ' ', m.group(1).lower())
        slot=_DIR_MAP.get(key)
        if not slot or slot in seen:
            continue
        seen.add(slot)
        out.append({'dir':slot[0], 'label':slot[1]})
    return out

def _nap_am(raw: str) -> bool:
    n=(raw or '').lower()
    if 'nạp âm' in n:
        return True
    if re.search(r'mệnh\s*(kim|mộc|thủy|hỏa|thổ)|(kim|mộc|thủy|hỏa|thổ)\s*mệnh', n):
        return True
    bare=re.sub(r'chiếu mệnh','', n)
    if re.search(r'\bmệnh\b', bare) and not _MENH_SKIP.search(bare):
        return True
    return False

def classify(text: str, channel: str='fs', source: str='') -> list[dict]:
    raw=text or ''; n=_norm(raw); tags=[]
    def add(tag, why):
        if tag not in [x['tag'] for x in tags]: tags.append({'tag':tag,'reason':why})
    nums=quantities(raw)
    if '%' in raw or any(w in n for w in ('chiem','co cau','phan bo','ty le','tỷ lệ','cơ cấu','chiếm','phân bổ')):
        add('co_cau','tỷ lệ/cơ cấu được nêu')
    if two_measurable_sides(raw):
        add('so_sanh','hai vế, mỗi vế có đối tượng đo được')
    if len(nums)==1 and 'co_cau' not in [x['tag'] for x in tags] and not is_chapter(raw):
        add('so_don','một trị số được nêu')
    if not is_chapter(raw) and re.search(r'\b(19|20)\d{2}\b|thế kỷ|năm (?:một nghìn|hai nghìn|mười tám|mười chín|hai mươi)', raw.lower()):
        add('dong_thoi_gian','có mốc năm/thời kỳ')
    if re.search(r'\b\d{1,2}\s*giờ(?:\s*\d{1,2})?\b|\b(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười) giờ\b|\b(?:lúc|vào|khoảng)\s+\d{1,2}[:.]\d{2}\b|\bcanh\s*(?:[1-5]|một|hai|ba|tư|năm|tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b|\bgiờ (?:tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b|\b(?:tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi) thời\b|\bbuổi (?:sáng|trưa|chiều|tối)\b|\bban đêm\b', raw.lower()):
        add('gio_trong_ngay','có giờ/canh giờ')
    places=places_in(raw)
    if places:
        add('ban_do','địa danh thuộc gazetteer có tọa độ, dùng như nơi chốn')
        if any(w in n for w in ('ở ','tại ','đến ','den ','thanh pho','thành phố','ngoi chua','ngôi chùa','di tich','di tích')):
            add('anh_dia_danh','địa danh gắn với địa điểm cụ thể')
    if re.search(r'\b(tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b', raw.lower()) and any(w in raw.lower() for w in ('xung','hợp','hại','hình','tam hợp','lục hợp')):
        add('quan_he_con_giap','nêu quan hệ giữa địa chi')
    if _nap_am(raw):
        add('nap_am','nạp âm hoặc chữ mệnh')
    if any(w in raw.lower() for w in ('quẻ','kinh dịch','bát quái')):
        add('que_dich','thuật ngữ quẻ dịch')
    if any(w in raw.lower() for w in ('cửu diệu','sao la hầu','sao kế đô','sao thái bạch')):
        add('sao_chieu_menh','tên sao chiếu mệnh')
    if any(w in raw.lower() for w in ('lạc thư','cửu cung')):
        add('so_cuu_cung','lạc thư/cửu cung')
    if extract_dirs(raw) or any(w in raw.lower() for w in ('la bàn','tọa hướng')):
        add('huong_phuong_vi','nêu hướng/phương vị')
    if '"' in raw or '“' in raw or '”' in raw or any(w in n for w in ('theo loi','theo lời','trich','trích','ghi rang','ghi rằng','viet rang','viết rằng')):
        add('trich_dan','dấu hiệu trích dẫn')
    if has_list(raw):
        add('liet_ke','liệt kê từ hai mục trở lên')
    if '?' in raw:
        add('cau_hoi','câu hỏi')
    if source and any(w in _norm(source) for w in ('sutta','kinh','nguồn','nguon','source')):
        add('trich_dan','có trường nguồn')
    if not tags:
        if any(w in n for w in ('la gi','là gì','nghia la','nghĩa là','khai niem','khái niệm','tuong trung','tượng trưng','bieu tuong','biểu tượng')):
            add('khai_niem','câu giải thích khái niệm')
        elif any(w in n for w in ('hinh dung','hình dung','tuong tuong','tưởng tượng','buc tranh','bức tranh','hinh anh','hình ảnh','canh tuong','cảnh tượng','vi nhu','ví như','giong nhu','giống như')):
            add('mo_ta_khai_niem','có so sánh/hình ảnh gợi hình rõ')
    return tags

def condition_ok(cond: str, text: str, row: dict) -> tuple[bool,str]:
    n=_norm(text)
    if cond in {'mot_so_lieu','ty_le_or_co_cau'}:
        ok=bool(quantities(text)); return ok,'có số liệu' if ok else 'thiếu số liệu'
    if cond=='hai_ve_so_sanh':
        ok=two_measurable_sides(text); return ok,'hai vế có đối tượng đo được' if ok else 'thiếu hai vế đo được'
    if cond=='moc_nam':
        ok=bool(re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b|the ky|thế kỷ|năm (?:mot nghin|hai nghin|muoi tam|muoi chin|hai muoi)|năm (?:một nghìn|hai nghìn|mười tám|mười chín|hai mươi)', n))
        return ok,'có mốc năm/thời kỳ' if ok else 'thiếu mốc thời gian'
    if cond=='gio_or_canh_gio':
        ok=bool(re.search(r'\b\d{1,2}\s*giờ(?:\s*\d{1,2})?\b|\b(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười) giờ\b|\b\d{1,2}[:.]\d{2}\b|\bcanh\s*(?:[1-5]|một|hai|ba|tư|năm|tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b|\bgiờ (?:tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b|\b(?:tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi) thời\b|\bbuổi (?:sáng|trưa|chiều|tối)\b|\bban đêm\b', (text or '').lower()))
        return ok,'có giờ/canh' if ok else 'thiếu giờ/canh'
    if cond in {'dia_danh_trong_hf_geo','dia_danh_xac_dinh'}:
        ok=bool(places_in(text)); return ok,'địa danh có tọa độ trong gazetteer' if ok else 'địa danh chưa có trong hf_geo/gazetteer hoặc chỉ là câu triết lý'
    if cond=='can_chi':
        ok=bool(re.search(r'\b(ty|suu|dan|mao|thin|ngo|mui|than|dau|tuat|hoi|tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b', n))
        return ok,'có địa chi' if ok else 'thiếu can chi'
    if cond=='nam_sinh_or_can_chi':
        ok=bool(re.search(r'\b(19|20)\d{2}\b|\b(ty|suu|dan|mao|thin|ngo|mui|than|dau|tuat|hoi|tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi)\b', n))
        return ok,'có năm sinh/can chi' if ok else 'thiếu năm sinh/can chi'
    if cond=='que_dich':
        ok=bool(re.search(r'quẻ\s+\w+|que\s+\w+', n)); return ok,'có tên quẻ' if ok else 'thiếu tên quẻ'
    if cond=='so_cuu_cung':
        ok='cửu cung' in (text or '').lower() or 'lạc thư' in (text or '').lower() or 'cuu cung' in n or 'lac thu' in n
        return ok,'có dữ liệu cửu cung' if ok else 'thiếu dữ liệu cửu cung'
    if cond=='huong':
        ok=bool(extract_dirs(text)) or 'tọa hướng' in (text or '').lower() or 'toa huong' in n
        return ok,'có hướng' if ok else 'thiếu hướng'
    if cond=='co_dirs':
        ok=bool(extract_dirs(text)); return ok,'có dirs cho la bàn' if ok else 'thiếu dirs'
    if cond=='sao_chieu_menh':
        ok=any(x in (text or '').lower() for x in ('cửu diệu','la hầu','kế đô','thái bạch','thái dương','thái âm'))
        return ok,'có sao chiếu mệnh' if ok else 'thiếu sao chiếu mệnh'
    if cond=='nguon_trich_dan':
        ok=bool(row.get('source') or re.search(r'“|”|"|theo lời|trích|ghi rằng', (text or '').lower()))
        return ok,'có nguồn/trích dẫn' if ok else 'thiếu nguồn trích dẫn'
    if cond=='co_cau_dinh_luong':
        ok='%' in (text or '') or any(w in n for w in ('co cau','cơ cấu','ty trong','tỷ trọng','phan bo','phân bổ'))
        return ok,'có cơ cấu định lượng' if ok else 'thiếu dữ liệu cơ cấu'
    if cond=='tai_lieu_hien_co':
        ok=bool(row.get('source') or row.get('media')); return ok,'có trường nguồn/media' if ok else 'thiếu tài liệu nguồn'
    if cond=='tu_lieu_hien_co':
        ok=bool(row.get('media')); return ok,'có media tư liệu' if ok else 'thiếu tư liệu'
    if cond=='di_vat_xac_dinh':
        ok=bool(row.get('media')); return ok,'có tư liệu di vật' if ok else 'thiếu di vật xác định'
    if cond=='device_hop_le':
        return False,'cần thông tin device'
    return True,'không yêu cầu dữ liệu bổ sung'

def _line_text(line) -> str:
    return line if isinstance(line, str) else str((line or {}).get('text',''))

def _is_heading(line) -> bool:
    s=_line_text(line).strip()
    return s.startswith('**') and s.endswith('**') and s.count('**')==2

def _clock(row: dict, n: int) -> tuple[list[dict] | None, str]:
    """Giây từng câu từ out/<id>.json. Không có thì ước lượng, kèm cờ."""
    override=row.get('_tts_json')
    path=Path(override) if override else OUT_DIR/f"{row.get('id','')}.json"
    if not str(row.get('id') or override) or not path.is_file():
        return None, 'uoc_a_plus_4'
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        segs=data.get('segments') or []
        if len(segs)<n or n==0:
            return None, 'uoc_a_plus_4'
        parsed=[{'start':float(s['start']),'end':float(s['end'])} for s in segs[:n]]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None, 'uoc_a_plus_4'
    return parsed, 'tts'

def _timeline(row: dict, n: int, segs: list[dict] | None) -> list[tuple[int,int,str,str]]:
    """Khoảng câu đang có cảnh/ảnh. Ảnh giữ tới mốc kế hoặc 22 giây; không có TTS thì a+4 câu."""
    lines=row.get('script') or row.get('sentences') or row.get('lines') or []
    visuals=row.get('visuals') or {}; media=row.get('media') or {}; spans=[]
    if isinstance(visuals,list):
        visuals={str(x.get('sentence_id',i+1)):x for i,x in enumerate(visuals) if isinstance(x,dict)}
    for k,spec in visuals.items():
        try: a=int(k)
        except: continue
        if 1<=a<=n and isinstance(spec,dict):
            ats=[int(z['at']) for z in (spec.get('steps') or spec.get('items') or spec.get('pins') or []) if isinstance(z,dict) and str(z.get('at','')).isdigit()]
            spans.append((a,min(n,int(spec.get('until') or max([a]+ats))),'visual',str(spec.get('type',''))))
    mids=[]
    if isinstance(media,dict):
        mids=[int(k) for k in media if str(k).isdigit() and 1<=int(k)<=n]
    headings={i for i,line in enumerate(lines,1) if _is_heading(line)}
    bounds=set(mids) | {a for a,_,_,_ in spans} | headings
    for a in mids:
        if segs is None:
            boundary=min([x for x in bounds if x>a]+[a+4, n+1])
            spans.append((a, min(n, boundary-1), 'media', 'media'))
            continue
        k=a-1
        start=segs[k]['start']
        while k+1<n:
            nxt=k+2
            if nxt in bounds:
                break
            if segs[k+1]['end']-start>HOLD_MAX_S:
                break
            k+=1
        spans.append((a, k+1, 'media', 'media'))
    return sorted(spans)

def choose(row: dict, profile: dict, catalog: dict) -> tuple[dict,dict]:
    lines=row.get('script') or row.get('sentences') or row.get('lines') or []
    if not isinstance(lines,list): raise ValueError('plan row script must be a list')
    segs, clock=_clock(row, len(lines))
    spans=_timeline(row, len(lines), segs)
    old=row.get('visuals') or {}; media=row.get('media') or {}; occupied=set()
    for k in old:
        try: occupied.add(int(k))
        except: pass
    if isinstance(media,dict):
        occupied.update(int(k) for k in media if str(k).isdigit())
    ca={x['type']:x for x in catalog['scenes']}; sem_by_type={t:set(x['y_nghia']) for t,x in ca.items()}
    tag_priority={tag:i for i,tag in enumerate(profile.get('tags',{}))}
    for a,b,_,_ in spans:
        occupied.update(range(a,b+1))
    recent=[]; suggestions={}; decisions=[]; k=max(0,int(profile.get('window_k',4)))
    visual_starts={}
    raw_visuals=row.get('visuals') or {}
    if isinstance(raw_visuals,dict):
        visual_starts={int(sid):str(spec.get('type','')) for sid,spec in raw_visuals.items() if str(sid).isdigit() and isinstance(spec,dict)}
    media_starts={int(sid) for sid in media if str(sid).isdigit()} if isinstance(media,dict) else set()
    seed=str(row.get('id',''))
    forbidden=set(profile.get('forbidden_types') or [])
    for idx,line in enumerate(lines,1):
        if idx in media_starts:
            recent=[]
        if idx in visual_starts:
            typ=visual_starts[idx]
            if typ in ca: recent.append(typ); recent=recent[-k:] if k else []
        if idx in occupied: continue
        text=_line_text(line)
        tags=classify(text,str(row.get('series','fs')),str(row.get('source','')))
        candidate_log=[]; choices=[]
        for tag in tags:
            for candidate_order,item in enumerate(profile.get('tags',{}).get(tag['tag'],[])):
                typ=item['type']; obj=ca.get(typ)
                if typ in [x['type'] for x in choices]: continue
                reason=[]; valid=True
                if typ not in ca: reason.append('không có trong catalog'); valid=False
                elif obj['qa']['trang_thai']!='dat': reason.append('khóa QA: '+obj['qa'].get('ly_do','')); valid=False
                if typ in forbidden:
                    reason.append('loại cảnh bị cấm trong hồ sơ kênh'); valid=False
                if obj and tag['tag'] not in sem_by_type[typ]: reason.append('không khớp thẻ nghĩa'); valid=False
                conds=[]
                for c in list(item.get('requires') or [])+list((obj or {}).get('dieu_kien') or []):
                    if c not in conds: conds.append(c)
                for cond in conds:
                    ok,why=condition_ok(cond,text,row)
                    if not ok: reason.append('thiếu dữ liệu: '+why); valid=False
                if typ in recent: reason.append('trùng loại trong cửa sổ chống lặp'); valid=False
                motion=obj.get('motion_label') if obj else None
                active_motion={ca.get(t,{}).get('motion_label') for t in recent if t in ca}
                if motion and motion in active_motion: reason.append('trùng loại chuyển động gần đây'); valid=False
                candidate_log.append({'type':typ,'semantic':tag['tag'],'eligible':valid,'reasons':reason})
                if valid: choices.append({'type':typ,'tag':tag['tag'],'requires':item.get('requires',[]),'priority':(tag_priority.get(tag['tag'],10**6),int(item.get('priority',candidate_order)))})
        selected=None; why=''
        if choices:
            best=min(x['priority'] for x in choices)
            tied=[x for x in choices if x['priority']==best]
            rank=int(hashlib.sha256(f'{seed}:{idx}'.encode()).hexdigest()[:8],16)%len(tied)
            selected=tied[rank]; why='ứng viên đạt QA, đủ điều kiện, khớp nghĩa; ưu tiên hồ sơ, tie-break theo seed id+câu'
            typ=selected['type']; suggestions[str(idx)]={'type':typ}
            if typ=='map':
                found=places_in(text)
                if found:
                    countries=[]; pins=[]
                    for name in found[:6]:
                        lon,lat,country=gazetteer()[name]
                        if country not in countries: countries.append(country)
                        pins.append({'name':name,'lon':float(lon),'lat':float(lat),'at':idx})
                    suggestions[str(idx)].update({'countries':countries,'pins':pins})
            if typ=='compass':
                suggestions[str(idx)]['dirs']=[{**d,'at':idx} for d in extract_dirs(text)]
            recent.append(typ); recent=recent[-k:] if k else []
        else:
            selected={'type':'anh_tinh_ken_burns'}; why='không có ứng viên phù hợp; giữ media hiện có hoặc cần ảnh tĩnh + Ken Burns'
            candidate_log.append({'type':'anh_tinh_ken_burns','eligible':True,'reasons':['fallback khi không có ứng viên đạt điều kiện']})
            recent=[]
        decisions.append({'sentence':idx,'text':text,'semantic_tags':tags,'candidates':candidate_log,'selected':selected,'reason':why,'motion_preset':None,'fallback':selected['type']=='anh_tinh_ken_burns','timeline_source':clock})
    return suggestions,{'id':seed,'timeline_source':clock,'decisions':decisions,'stats':{'sentences':len(lines),'existing_scene_or_media':len(occupied),'considered':len(decisions),'with_candidate':sum(not d['fallback'] for d in decisions),'fallback':sum(d['fallback'] for d in decisions),'timeline_source':clock,'semantic_tags':{t:sum(t in [z['tag'] for z in d['semantic_tags']] for d in decisions) for t in sorted({z['tag'] for d in decisions for z in d['semantic_tags']})}}}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--plan',required=True); ap.add_argument('--id',required=True); ap.add_argument('--profile'); ap.add_argument('--log'); ap.add_argument('--suggest-visuals')
    a=ap.parse_args(argv); data=load_json(Path(a.plan)); row=next((x for x in data if isinstance(x,dict) and str(x.get('id'))==a.id),None) if isinstance(data,list) else data
    if row is None: raise SystemExit(f'plan row id not found: {a.id}')
    channel=str(row.get('series') or 'fs'); profile=load_profile(a.profile,channel); catalog=load_json(CATALOG)
    visuals,result=choose(row,profile,catalog)
    if a.log: Path(a.log).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in result['decisions']),encoding='utf-8')
    if a.suggest_visuals: Path(a.suggest_visuals).write_text(json.dumps(visuals,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['stats'],ensure_ascii=False,sort_keys=True))
if __name__=='__main__': main()
