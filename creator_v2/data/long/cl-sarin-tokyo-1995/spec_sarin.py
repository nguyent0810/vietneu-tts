"""Ghi spec.json (youtube, credits, mix, look...) cho cl-sarin-tokyo-1995. Gọi từ gen_scenes.py sau khi ghi cảnh.

Tác giả/giấy phép lấy từ API Wikimedia Commons ngày 16/11/2026 (bảng CREDITS). Ảnh không có tác giả ghi rõ không dùng.
publish_at + approved: Lead đặt 17/11 theo lời chủ kênh 16/11.
"""
import json
import urllib.parse
from pathlib import Path

D = Path(__file__).resolve().parent

TITLES = ['Gọi Cấp Cứu Cho Vợ, Bị Báo Chí Gọi Là Người Khí Độc',
          'Cảnh Sát Có Cặn Sarin Từ Trước, Tokyo Vẫn Bị Đánh Úp',
          'Chín Tháng Sau Matsumoto, Vì Sao Tokyo Vẫn Bị Sarin?']
TITLE = TITLES[0]
LOOK = 'amber'      # 17/11: steel trùng Mata Hari (29/11, ngay trước) -> variety chặn final; amber dùng lần cuối ở Hòa Thân 15/11

CREDITS = {
    'File:130608 Matsumoto Castle Matsumoto Nagano pref Japan02bs4.jpg': ('663highland', 'CC BY 2.5'),
    'File:Anti-Aum Shinrikyo protest.JPG': ('Abasaa', 'Public domain'),
    'File:Emergency personnel respond to the Tokyo subway sarin attack.png': ('United States Public Health Service', 'Public domain'),
    'File:Hibiya Line-2005-10-24 1.jpg': ('Syohei Arai', 'CC BY-SA 4.0'),
    'File:HibiyaLine ne bound sarin attack.png': ('Torsodog (talk)', 'CC BY-SA 3.0'),
    'File:Japanese-national-railways-203-Mato67-20091001-145254.jpg': ('LERK', 'CC BY 3.0'),
    'File:Kasumigaseki Station platforms 20130302.JPG': ('DAJF', 'CC BY-SA 3.0'),
    'File:Kasumigaseki Station, Tokyo.jpg': ('っ', 'CC BY-SA 3.0'),
    'File:Kofu City Hall Kamikuishiki Branch Office.JPG': ('Sakaori (talk)', 'CC BY 3.0'),
    'File:Lake Motosu03.jpg': ('Captain76', 'CC BY-SA 3.0'),
    'File:Marunouchi-ogi map sarin attack.png': ('Torsodog (talk)', 'CC BY-SA 3.0'),
    'File:Matsumoto Castle Keep Tower.jpg': ('稲妻ノ歯鯨 (Lightning toothed whale)', 'CC BY-SA 4.0'),
    'File:Matsumoto Castle09n4592.jpg': ('663highland', 'CC BY 2.5'),
    'File:Matsumoto castle01s2048.jpg': ('663highland', 'CC BY 2.5'),
    'File:Omachi Dam park Sakamoto Tatsuhiko cenotaph.jpg': ('Qurren', 'CC BY-SA 3.0'),
    'File:PSIA Aum Shinrikyo facility inspection 01.jpg': ('Public Security Intelligence Agency', 'CC BY 4.0'),
    'File:PSIA Aum Shinrikyo facility inspection 02.jpg': ('Public Security Intelligence Agency', 'CC BY 4.0'),
    'File:Self-defense officers spraying decontaminant inside contaminated subway vehicles.jpg': ('陸上自衛隊（Japan Ground Self-Defense Force）', 'CC BY 4.0'),
    'File:Subway sarin attack 1995-2.png': ('防衛省', 'CC BY 3.0'),
    'File:Subway sarin attack 1995.png': ('防衛省', 'CC BY 3.0'),
    'File:Tokyo Chiyoda Line Sarin Attack.jpg': ('J4lambert', 'CC BY-SA 3.0'),
    'File:Tokyo Metro Marunouchi Line above Kanda River 001.jpg': ('ネプチューン', 'Public domain'),
    'File:Tokyo Metro Series 02 02-116F in Yotsuya Station 01.jpg': ('Wikimizuki', 'CC BY-SA 4.0'),
    'File:Tokyo Station Chuo Line platform.jpg': ('Douglas Paul Perkins', 'CC BY 3.0'),
    'File:Tokyo-Metro Hibiya-STA Platform2.jpg': ('MaedaAkihiko', 'CC BY-SA 4.0'),
    'File:Tokyo-metro Kasumigaseki-STA Platform2.jpg': ('MaedaAkihiko', 'CC BY-SA 4.0'),
    'File:TokyoMetro-H10-Tsukiji-station-platform.jpg': ('LERK', 'CC BY 3.0'),
    'File:Tsukiji Police Station.jpg': ('Lombroso', 'Public domain'),
    'File:Tsukiji station - hibiya line - nov 2014.jpg': ('nesnad', 'CC BY 3.0'),
    'File:Tsukiji-STA Platform1.jpg': ('MaedaAkihiko', 'CC0'),
    'File:View to the east of the Metoba River from Sensai Bridge, Matsumoto, 2016.jpg': ('DimiTalen', 'CC0'),
    'File:【地下鉄サリン事件】出発準備完了報告をする自衛隊員（市ヶ谷駐屯地）.jpg': ('陸上自衛隊（Japan Ground Self-Defense Force）', 'CC BY 4.0'),
    'File:【地下鉄サリン事件】化学機動中隊の活動の様子.jpg': ('東京消防庁（Tokyo Fire Department）', 'CC BY 4.0'),
    'File:【地下鉄サリン事件】除染を行う自衛隊員.jpg': ('陸上自衛隊（Japan Ground Self-Defense Force）', 'CC BY 4.0'),
    'File:【地下鉄サリン事件】除染を行う自衛隊員と警察官.jpg': ('陸上自衛隊（Japan Ground Self-Defense Force）', 'CC BY 4.0'),
    'File:【地下鉄サリン事件】除染活動に向かう自衛隊員.jpg': ('陸上自衛隊（Japan Ground Self-Defense Force）', 'CC BY 4.0'),
    'File:サティアン.jpg': ('吉川 祐介', 'CC BY-SA 4.0'),
    'File:サティアン②.jpg': ('吉川 祐介', 'CC BY-SA 4.0'),
    'File:地下鉄サリン事件の災害派遣対応での練馬駐屯地出発.jpg': ('糠谷勝', 'CC0'),
}

SOURCES = [
    'https://en.wikipedia.org/wiki/Tokyo_subway_sarin_attack',
    'https://en.wikipedia.org/wiki/Matsumoto_incident',
    'https://en.wikipedia.org/wiki/Aum_Shinrikyo',
    'https://en.wikipedia.org/wiki/Shoko_Asahara',
    'https://en.wikipedia.org/wiki/Yoshiyuki_K%C5%8Dno_%28victim%29',
    'https://ja.wikipedia.org/wiki/' + urllib.parse.quote('地下鉄サリン事件'),
    'https://www.nippon.com/en/japan-topics/bg900563',
    'https://www.nippon.com/en/nipponblog/m00033/',
    'https://www.aljazeera.com/news/2004/2/27/japan-cult-guru-gets-death-sentence',
    'https://abcnews.go.com/International/wireStory/30-years-after-deadly-tokyo-subway-gassing-survivors-119973324',
    'https://www.ebsco.com/research-starters/politics-and-government/terrorists-use-sarin-gas-tokyo-subway-attack',
]

# Phiên âm cho TTS (bảng cuối script.md)
SAY = {'matsumoto': 'Mát-sư-mô-tô', 'nagano': 'Na-ga-nô', 'kono': 'Cô-nô', 'yoshiyuki': 'Giô-si-yu-ki', 'sumiko': 'Su-mi-cô', 'aum shinrikyo': 'Ao-m Shin-ri-kyô', 'asahara': 'A-sa-ha-ra', 'shoko': 'Sô-cô', 'kamikuishiki': 'Ka-mi-ku-i-shi-ki', 'satyan': 'Sa-chi-an', 'kasumigaseki': 'Ka-su-mi-ga-sê-ki', 'tsukiji': 'Su-ki-gi', 'marunouchi': 'Ma-ru-nô-u-chi', 'hibiya': 'Hi-bi-ya', 'chiyoda': 'Chi-yô-đa', 'yomiuri': 'Giô-mi-u-ri', 'asahi': 'A-sa-hi', 'tsuneishi': 'Su-nê-i-shi', 'kakimi': 'Ka-ki-mi', 'sakamoto': 'Sa-ka-mô-tô', 'kariya': 'Ka-ri-ya', 'nonaka': 'Nô-na-ka', 'yanagisawa': 'Gia-na-gi-sa-wa', 'nippon.com': 'Nít-pôn chấm com'}


def apply(CH, chapter_titles, used, IMGS):
    path = D / 'spec.json'
    spec = json.loads(path.read_text(encoding='utf-8'))
    used_files = sorted({IMGS[k] for k in used if not str(IMGS[k]).startswith('EXT:')})
    missing = [f for f in used_files if f not in CREDITS or not CREDITS[f][0]]
    if missing:
        raise SystemExit('Thiếu ghi công cho: ' + '; '.join(missing))
    credits = []
    for f in used_files:
        author, lic = CREDITS[f]
        name = f.removeprefix('File:')
        url = 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(f.replace(' ', '_'))
        credits.append(f'{name} — {author} — {lic} — {url}')
    credits.append('Ảnh minh họa chung và cảnh PHỎNG DỰNG (ảnh/clip tạo bằng AI, không người rõ mặt, không chữ): có nhãn trên hình; không phải ảnh chụp hiện trường.')
    credits.append('Clip stock: Pexels (pexels.com), giấy phép Pexels; clip minh họa chung do AI tạo, ghi chú MINH HỌA CHUNG trên hình.')
    for t in TITLES:
        assert len(t) <= 60, (len(t), t)
    spec.update({
        'title': TITLE, 'channel': 'CL', 'theme': 'noir', 'look': LOOK, 'autoTr': True, 'master': True, 'craft': True,
        'endcard': 9, 'endcardSub': 'HỒ SƠ TIẾP THEO',
        'acc': ['sarin', 'matsumoto', 'aum shinrikyo', 'kono'], 'say': SAY, 'chapters': list(CH),
        'mix_levels': {'CL': {'gain': 0.27, 'threshold': 0.08, 'ratio': 3.0}},
    })
    spec.pop('accent', None)
    yt = spec.setdefault('youtube', {})
    yt.update({
        'titles': TITLES,
        'summary': 'Tokyo, 20/3/1995: sarin trên năm chuyến tàu điện ngầm. Chín tháng trước, ở Matsumoto, người gọi cấp cứu cho vợ bị báo chí gọi là "Người Khí Độc". '
                   'Chuỗi quyết định điều tra giữa hai ngày ấy: cái tên bị chọn nhầm, mẫu đất ở chân núi Phú Sĩ, ngày khám xét đến chậm hai ngày, và cái giá phải trả.',
        'more': [],
        'sources': SOURCES,
        'tags': ['sarin tokyo 1995', 'aum shinrikyo', 'matsumoto 1994', 'yoshiyuki kono', 'tàu điện ngầm tokyo', 'vụ án nhật bản', 'hồ sơ lịch sử', 'ngoài đời thật'],
        'hashtags': ['SarinTokyo', 'AumShinrikyo', 'HoSo'],
        'category': '24', 'playlist': 'Ngoài Đời Thật',
        'chapter_titles': chapter_titles, 'video_credits': credits,
    })
    yt['publish_at'] = '2026-12-01T14:00:00Z'   # CL Tue-Thu-Sun; Lead 17/11 chọn slot
    spec['approved'] = '16/11/2026 — ok sau khi xong moi bai thi schedule upload len nhe'
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('spec.json:', len(used_files), 'ảnh có ghi công,', len(SOURCES), 'nguồn')
