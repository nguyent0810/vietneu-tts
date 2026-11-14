"""Ghi spec.json (youtube, credits, mix, look...) cho cl-hoang-kim-vinh. Gọi từ gen_scenes.py sau khi ghi cảnh.

Siêu dữ liệu tác giả/giấy phép lấy từ API Wikimedia Commons ngày 13/11/2026 (bảng CREDITS bên dưới).
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent

TITLE = 'HOÀNG KIM VINH Ngoài Đời Thật: Ba Trang Giấy, Một Người'
LOOK = 'classic'
CHAPTER_ORDER_NOTE = 'Bốn mốc, bốn cách kể: 1924, 1930, 1931, 1951.'

# file Commons -> (tác giả, giấy phép)
CREDITS = {
    'File:黄金荣肖像.jpg': ('Tác giả không rõ (Virtual Shanghai)', 'Public domain'),
    'File:Huangjinrong Cangku.JPG': ('Fayhoo', 'CC BY-SA 3.0'),
    'File:Zhang Siaolin.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:民國·張嘯林.png': ('Tác giả không rõ', 'Public domain'),
    'File:East Jinling Rd. in 1930s.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Tcitp d380 french municipal council offices in shanghai.jpg': ('Arnold Wright', 'Public domain'),
    'File:French Concession 1937.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Shanghai 1884.jpg': ('Xu Yucang, "Dian Shi Zhai"', 'Public domain'),
    'File:Shanghai 1935 S1 AMS-WO.jpg': ('United States Army Map Service', 'Public domain'),
    'File:Pearl Harbor Attack, 7 December 1941 (24374354935).jpg': ('National Museum of the U.S. Navy', 'Public domain'),
    'File:Currency issued inside the settlement for use by the British Armed Forces inside the city - circa 1940.jpg': ('British Armed Forces', 'Public domain'),
    'File:American marines holding up a Japanese patrol in Shanghai, 1930s.png': ('Tác giả không rõ', 'Public domain'),
    'File:Stamp Shanghai 1893 1c.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:The mystic flowery land; a personal narrative (1896) (14591881777).jpg': ('Internet Archive Book Images (Charles J. H. Halcombe, 1896)', 'No restrictions'),
    'File:Shanghai 1933.jpg': ('U.S. Army Map Service', 'Public domain'),
    'File:Japanese cruiser Izumo in Shanghai.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:1930 Shanghai.jpg': ('US Signal Corps', 'Public domain'),
    'File:The Bund, Shanghai, c1890s.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:The Great World (Shanghai).jpg': ('Legolas1024', 'CC BY-SA 3.0'),
    'File:Chiang Kai-shek, Wang Jingwei, Borodin and others, Canton, January 1926 (Fu-n086).jpg': ('Fu Bingchang', 'Public domain'),
    'File:Whampoa3.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Nationalist government of Nanking - nominally ruling over entire China, 1930 (2675972715).jpg': ('Japanese Embassy; tải lên bởi tm', 'CC BY 2.0'),
    'File:NRA Generals Northern Expedition1.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:民國五年三十歲的蔣介石.png': ('Tác giả không rõ', 'Public domain'),
    'File:Chiang1926.jpg': ('Tác giả không rõ (International)', 'Public domain'),
    'File:Tcitp d385 native chinese police of the international settlement.jpg': ('Arnold Wright', 'Public domain'),
    'File:Chinese opium smokers.jpg': ('Thomas Allom (vẽ), G. Paterson (khắc)', 'Public domain'),
    'File:China opium den.tif': ('Anonyme, Société de Saint-Augustin, 1896', 'Public domain'),
    'File:A busy stacking room in the opium factory at Patna, India. L Wellcome V0019154.jpg': ('W. S. Sherwill (Wellcome Collection)', 'Public domain'),
    'File:China, Opium smokers by Lai Afong, c1880.JPG': ('Lai Afong', 'Public domain'),
    'File:Opium Smokers - Beijing 1932.jpg': ('Tác giả không rõ', 'CC0'),
    'File:"Map showing where opium is grown in China" in 1908, from book - Present-Day Conditions in China; Notes Designed to Show the Moral and Spiritual Claims of the Chinese Empire, published 1908 (IA presentdaycondit00broo) (page 25 crop).jpg': ('Marshall Broomhall (China Inland Mission), 1908', 'Public domain'),
    'File:Tcitp d385 french settlement police of anamites.jpg': ('Arnold Wright', 'Public domain'),
    'File:Automitrailleuse française à Shangai (Wide World, Les Opérations militaires en Chine, 1930) (cropped).jpg': ('Wide World, 1930', 'Public domain'),
    'File:Shanghai Nanking Road 1930s.jpeg': ('Tác giả không rõ', 'Public domain'),
    'File:Shanghai Sikh 1935.jpg': ('Ảnh bưu thiếp c. 1935', 'Public domain'),
    'File:Shanghai Bund seen from the French Concession.jpg': ('Tác giả không rõ, c. 1934', 'Public domain'),
    'File:Nanking Road, Shanghai, c. 1930s.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Rue de Consulate, Shanghai.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Nanking Road, Shanghai, circa 1930s.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:1937 Shanghai tram map.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Metropole Hotel under construction, Shanghai, 15 September 1930.jpg': ('Historical Photographs of China (Đại học Bristol)', 'Public domain'),
    'File:Jichisan Shokai - Shanghai City Street Map - 上海市市街圖 (1932).jpg': ('Jichishan Shokai', 'Public domain'),
    'File:Tomb of Du Yuesheng.jpg': ('M940504', 'CC BY-SA 4.0'),
}

SOURCES = [
    'https://en.wikipedia.org/wiki/Huang_Jinrong',
    'https://zh.wikipedia.org/zh-cn/%E9%BB%84%E9%87%91%E8%8D%A3',
    'https://en.wikipedia.org/wiki/Du_Yuesheng',
    'https://zh.wikipedia.org/wiki/%E6%9D%9C%E6%9C%88%E7%AC%99',
    'https://zh.wikipedia.org/wiki/%E5%BC%B5%E5%98%AF%E6%9E%97',
    'https://en.wikipedia.org/wiki/Great_World',
    'https://en.wikipedia.org/wiki/Shanghai_massacre_of_1927',
    'https://en.wikipedia.org/wiki/Green_Gang',
    'https://en.wikipedia.org/wiki/The_Bund_(TV_series)',
    'https://en.wikipedia.org/wiki/Shanghai_French_Concession',
    'https://zh.wikisource.org/wiki/%E6%B5%B7%E4%B8%8A%E5%90%8D%E4%BA%BA%E5%82%B3',
    'https://zh.wikisource.org/wiki/%E6%B5%B7%E4%B8%8A%E5%90%8D%E4%BA%BA%E5%82%B3/%E9%BB%83%E9%8C%A6%E9%8F%9E',
    'https://zh.wikisource.org/wiki/%E6%B5%B7%E4%B8%8A%E5%90%8D%E4%BA%BA%E5%82%B3/%E6%9D%9C%E6%9C%88%E7%AC%99',
    'https://zh.wikisource.org/wiki/%E6%B5%B7%E4%B8%8A%E5%90%8D%E4%BA%BA%E5%82%B3/%E5%BC%B5%E5%98%AF%E6%9E%97',
    'https://www.sohu.com/a/123200912_391448',
]


def apply(CH, chapter_titles, used, IMGS):
    path = D / 'spec.json'
    spec = json.loads(path.read_text(encoding='utf-8'))
    used_files = sorted({IMGS[k] for k in used})
    missing = [f for f in used_files if f not in CREDITS]
    if missing:
        raise SystemExit('Thiếu ghi công cho: ' + '; '.join(missing))
    credits = []
    for f in used_files:
        author, lic = CREDITS[f]
        name = f.removeprefix('File:')
        url = 'https://commons.wikimedia.org/wiki/' + __import__('urllib.parse', fromlist=['quote']).quote(f.replace(' ', '_'))
        credits.append(f'{name} — {author} — {lic} — {url}')
    credits.append('Cảnh minh họa chung (clip tạo bằng AI, không người, không chữ): ghi chú "MINH HỌA CHUNG" trên hình; không phải tư liệu.')
    assert len(TITLE) <= 60, len(TITLE)
    spec.update({
        'title': TITLE, 'channel': 'CL', 'theme': 'noir', 'look': LOOK, 'autoTr': True, 'master': True, 'craft': True,
        'endcard': 9, 'endcardSub': 'HỒ SƠ TIẾP THEO',
        'acc': ['hoàng kim vinh', 'đỗ nguyệt sanh', 'trương khiếu lâm'], 'say': SAY, 'chapters': list(CH),
        # Cổng mức nhạc (final): giữ đúng mức Lưu Gù đã qua.
        'mix_levels': {'CL': {'gain': 0.27, 'threshold': 0.08, 'ratio': 3.0}},  # Lead 14/11: sau #376 gain này nhân vào mức tự cân (-14 dB): .45 -> nhạc -5,5 dB; .27 -> khoảng -10 dB
    })
    spec.pop('accent', None)
    yt = spec.setdefault('youtube', {})
    yt.update({
        'titles': [TITLE],
        'summary': 'Hồ sơ Hoàng Kim Vinh qua bốn mốc 1924, 1930, 1931 và 1951: mỗi mốc là một trang giấy khác nhau kể về cùng một người ở Thượng Hải.',
        'more': [],
        'sources': SOURCES,
        'tags': ['hoàng kim vinh', 'thượng hải', 'thanh bang', 'tô giới pháp', 'đại thế giới', 'lịch sử trung quốc', 'hồ sơ lịch sử'],
        'hashtags': ['HoangKimVinh', 'ThuongHai', 'HoSo'],
        'category': '24', 'thumb': 't1.jpg', 'publish_at': '2026-11-19T14:00:00Z', 'playlist': 'Ngoài Đời Thật',
        'chapter_titles': chapter_titles, 'video_credits': credits,
    })
    # Lead 13/11: plan duyệt tối 13/11; slot CL Thứ Năm 19/11 21:00 VN còn trống.
    spec['approved'] = '13/11/2026 — duyet, ban tu dieu phoi theo cach tot nhat nhe, toi di ngu'
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('spec.json:', len(used_files), 'ảnh có ghi công,', len(SOURCES), 'nguồn')


# Phiên âm tên nước ngoài/viết tắt trong lời đọc (khoá viết thường; không neo cảnh vào các từ này).
SAY = {'wikipedia': 'Uých-ki-pi-đi-a', 'tvb': 'Ti Vi Bi', 'wakeman': 'Uây-cờ-man', 'frederic': 'Phơ-rê-đơ-rích',
       'josef': 'Giô-xép', 'sternberg': 'Xtơn-bơ', 'jules': 'Duyn', 'bigot': 'Bi-gô', 'vichy': 'Vi-si', 'edward': 'Ét-uốt', 'von': 'phôn', 'le': 'Lơ'}
