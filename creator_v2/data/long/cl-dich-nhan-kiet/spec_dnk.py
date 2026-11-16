"""Ghi spec.json (youtube, credits, mix, look...) cho cl-dich-nhan-kiet. Gọi từ gen_scenes.py sau khi ghi cảnh.

Siêu dữ liệu tác giả/giấy phép lấy từ API Wikimedia Commons ngày 15/11/2026 (bảng CREDITS bên dưới).
"""
import json
import urllib.parse
from pathlib import Path

D = Path(__file__).resolve().parent

TITLE = 'Tể Tướng Tự Nhận Mình Phản: Ba Chữ Cứu Mạng Địch Nhân Kiệt'
TITLES = [TITLE, 'Mảnh Lụa Giấu Trong Áo Bông: Tể Tướng Thoát Chết Ra Sao?', 'Xử Xong Cho 17.000 Người Không Ai Oan, Rồi Nhận Mình Phản?']
LOOK = 'rose'      # khác ba video CL lân cận trên lịch: classic (Hoàng Kim Vinh), jade (Lưu Gù), sulfur (Đông Lang)

# file Commons -> (tác giả, giấy phép)
CREDITS = {
    'File:102 S-312 Tang Kaiyuan, Gaozu, 618-626 ff, 25mm.jpg': ('Gary Lee Todd', 'CC0'),
    'File:2017-02-25 Tomb of Di Renjie.jpg': ('Windmemories', 'CC BY-SA 4.0'),
    'File:20210220 A model of Luoyang in Sui and Tang dynasty, Henan Museum.jpg': ('Windmemories', 'CC BY-SA 4.0'),
    'File:20210220 Wu Zetian Gold Strip, Henan Museum.jpg': ('Windmemories', 'CC BY-SA 4.0'),
    'File:20251018 Tomb of Di Renjie.jpg': ('Windmemories', 'CC BY-SA 4.0'),
    'File:A palace concert.jpg': ('anonymous', 'Public domain'),
    'File:Ancient Buddhist Grottoes at Longmen- Fengxian Temple, Vairocana, Said to be Carved in Image of Wu Zetian.jpg': ('Gary Todd', 'CC0'),
    'File:CMOC Treasures of Ancient China exhibit - pottery horse, detail 1.jpg': ('Editor at Large', 'CC BY-SA 2.5'),
    'File:CMOC Treasures of Ancient China exhibit - tri-coloured figure of a civil official.jpg': ('Editor at Large', 'CC BY-SA 2.5'),
    'File:Cernuschi Museum 20060812 162.jpg': ('Guillaume Jacquet', 'CC BY-SA 3.0'),
    "File:Chang'an City in Tang Dynasty (9833496374).jpg": ('Gary Todd', 'CC0'),
    "File:Chinese - The Twenty-Four Ministers of the Tang -T'ang- Dynasty Emperor Taizong -T'ai-Tsung- - Walters 3557 - View A.jpg": ('Tác giả không rõ (Trung Quốc)', 'Public domain'),
    'File:Court Ladies Preparing Newly Woven Silk (cropped to show the ironing).jpg': ('Zhang Xuan', 'Public domain'),
    'File:Court Ladies Preparing Newly Woven Silk (cropped).jpg': ('Zhang Xuan', 'Public domain'),
    'File:Court Ladies of the Tang.jpg': ('Họa sĩ vô danh đời Đường (tranh vách mộ)', 'Public domain'),
    'File:Court Official (Minqi), Tang Dynasty, China, ceramic with glazes - Mount Holyoke College Art Museum - DSC04556.JPG': ('Daderot', 'CC0'),
    'File:Court ladies pounding silk from a painting (捣练图) by Emperor Huizong.jpg': ('Tống Huy Tông / bản chép theo Trương Huyên', 'Public domain'),
    'File:Di Renjie.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Emperor Taizong gives an audience to the ambassador of Tibet.jpg': ('Yan Liben', 'Public domain'),
    'File:Figure of a Tang dynasty official, V&A London.jpg': ('14GTR', 'CC0'),
    'File:Gilt silver jar with pattern of dancing horses.jpg': ('User Mountain on zh.wikipedia', 'Public domain'),
    'File:Gokturk cav.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Grutes de longmen.jpg': ('Marcdf', 'Public domain'),
    "File:History of Xi'an.jpg": ('SY', 'CC BY-SA 4.0'),
    'File:Honour guard of Princess Changle (长乐公主墓), Zhao Mausoleum, Shaanxi province. Tang Zhenguan year 17, ie 644 CE.jpg': ('Họa sĩ vô danh thế kỷ 7 (tranh vách mộ)', 'Public domain'),
    "File:Lo-yang and Ch'ang-an Ancient and Modern.jpg": ('Albert Herrmann & Georg Westermann', 'Public domain'),
    'File:Lokapala and Officials Tang Dynasty 618-907 CE Henan Province China.jpg': ('Mary Harrsch', 'CC BY-SA 4.0'),
    'File:Luoyang 2006 7-29.jpg': ('G41rn8', 'CC BY-SA 4.0'),
    'File:Luoyang in Sui & Tang Dynasties (10233766646).jpg': ('Gary Todd', 'CC0'),
    'File:Map of the First Turkic Khaganate.png': ('Ktrinko, Greenvert', 'CC BY-SA 4.0'),
    'File:Map of the Second Turkic Khaganate.png': ('naturalearthdata.com, offered to the Public Domain per Terms of Use', 'CC0'),
    'File:Mirror with phoenixes, birds, and flowers - Google Art Project.jpg': ('anonymous', 'Public domain'),
    "File:Model of Hanguang Gate, Chang'an, Tang Dynasty, Covered by Later Wall (9949773254).jpg": ('Gary Todd', 'CC0'),
    'File:Mogao Cave 156 battle.jpg': ('Họa sĩ vô danh, cuối đời Đường', 'Public domain'),
    'File:Mogao Cave 220 Tang Dynasty emperor and officials 莫高窟220窟东壁门北 初唐君臣帝王.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Officer of the Guard of Honour. Tomb of Princess Changle (长乐公主墓), Zhao Mausoleum, Shaanxi province. Tang Zhenguan year 17, ie 644 CE.jpg': ('Họa sĩ vô danh thế kỷ 7 (tranh vách mộ)', 'Public domain'),
    'File:Portraits of Famous Men - Di Renjie 2.jpg': ('Unknown Chinese artist', 'Public domain'),
    'File:Portraits of Famous Men - Di Renjie.jpg': ('Unknown Chinese artist', 'Public domain'),
    'File:Portraits of Famous Men - Yao Chong.jpg': ('Unknown Chinese artist', 'Public domain'),
    'File:Qianling Mausoleum 02 2013-08.JPG': ('猫猫的日记本', 'CC BY-SA 3.0'),
    'File:Qianling Mausoleum 36 2013-08.JPG': ('猫猫的日记本', 'CC BY-SA 3.0'),
    'File:Qianling Mausoleum statue (cropped).jpg': ('猫猫的日记本', 'CC BY-SA 4.0'),
    'File:Qianling Mausoleum, dignitary with braids.jpg': ('Felix Filnkoessl', 'CC BY-SA 2.0'),
    'File:Seated bodhisattva, excavated from the White Horse Monastery, Loyang, Henan, China, c. 530 AD, limestone - Museum of Fine Arts, Boston - DSC02802.JPG': ('Daderot', 'CC0'),
    'File:Soldiers of the Guard of Honour. Tomb of Princess Changle (长乐公主墓), Zhao Mausoleum, Shaanxi province. Tang Zhenguan year 17, ie 644 CE.jpg': ('Họa sĩ vô danh thế kỷ 7 (tranh vách mộ)', 'Public domain'),
    'File:Spring Outing of the Tang Court.jpg': ('Zhang Xuan', 'Public domain'),
    'File:Stone Relief Panel of Zhaoling- Battle Steed of Tang Emperor Taizong 1.jpg': ('Gary Todd', 'CC0'),
    'File:Stone Relief Panel of Zhaoling- Battle Steed of Tang Emperor Taizong 2.jpg': ('Gary Todd', 'CC0'),
    'File:Stone Relief Panel of Zhaoling- Battle Steed of Tang Emperor Taizong 6.jpg': ('Gary Todd', 'CC0'),
    'File:Tang China 669AD.jpg': ('Louis le Grand', 'CC BY-SA 2.5'),
    'File:Tang Dynasty circa 700 CE.png': ('Ian Kiu', 'CC BY-SA 3.0'),
    'File:Tang Dynasty emissaries at the court of Varkhuman in Samarkand carrying silk and a string of silkworm cocoons, 648-651 CE, Afrasiyab murals, Samarkand.jpg': ('Northeast Asian History Foundation', 'Public domain'),
    'File:Tang Dynasty, sancai pottery, civil official.JPG': ('Gary Lee Todd', 'CC BY-SA 4.0'),
    'File:Tang Emperor Taizong.jpg': ('Yan Liben', 'Public domain'),
    'File:Tang Empress Wu Zetian Diorama.jpg': ('Gary Todd', 'CC0'),
    'File:Tang Pottery Civil Official & Maid-servant.jpg': ('Gary Todd', 'CC0'),
    'File:Tang Sancai Official.jpg': ('Gary Lee Todd', 'CC0'),
    'File:Tang Sancai Porcelain Civil Official, Xinxiang 02.jpg': ('Gary Todd', 'CC0'),
    'File:Tang Sancai Porcelain Official.jpg': ('Gary Todd', 'CC0'),
    'File:Tang Sancai Porcelain with Musicians on a Camel (no background).jpg': ('Gary Todd', 'CC0'),
    'File:Tang Warrior.jpg': ('Flickr user Gary Todd', 'CC BY-SA 4.0'),
    'File:TangBodhisattva.JPG': ('PHG', 'Public domain'),
    'File:Tomb figures of two officials with a guardian animal, China, Tang dynasty, earthenware with three-color lead glaze - Östasiatiska museet, Stockholm - DSC09620.JPG': ('Daderot', 'CC0'),
    'File:Tomb figurine of a horse with rider, China, Tang dynasty, 618-906 AD, earthenware with traces of red and yellow glaze - Östasiatiska museet, Stockholm - DSC09585.JPG': ('Daderot', 'CC0'),
    'File:Tomb figurine of a horse, China, Tang dynasty, early 600s AD, glazed earthenware - Östasiatiska museet, Stockholm - DSC09590.JPG': ('Daderot', 'CC0'),
    'File:Turkic Head of Koltegin Statue (35324303410).jpg': ('Gary Todd', 'CC0'),
    'File:Turkic horsemen with unidentifiable ambassadors on top.jpg': ('Unidentified photographer', 'Public domain'),
    'File:Wuhou (2).jpg': ('Tác giả không rõ', 'Public domain'),
    'File:Zhao Mausoleum.JPG': ('Acstar', 'CC BY-SA 4.0'),
    'File:升仙太子碑拓片局部.jpg': ('顾心阳', 'Public domain'),
    'File:唐后行從圖 (局部) - 武則天.png': ('Có thể là Trương Huyên', 'Public domain'),
    'File:武曌像.jpg': ('Tác giả không rõ', 'Public domain'),
    'File:洛阳明堂天堂遗址中明堂的复原模型 (cropped).jpg': ('Ghrkya', 'CC BY-SA 4.0'),
    'File:洛阳白马寺内狄仁杰墓.jpg': ('Gisling', 'CC BY-SA 3.0'),
    'File:狄仁杰.jpg': ('Tác giả không rõ', 'Public domain'),
}

def _src(zh):
    return 'https://zh.wikisource.org/wiki/' + urllib.parse.quote(zh)


SOURCES = [
    _src('舊唐書/卷89'),
    _src('新唐書/卷115'),
    _src('資治通鑑/卷202'),
    _src('資治通鑑/卷204'),
    _src('資治通鑑/卷205'),
    _src('資治通鑑/卷206'),
    _src('資治通鑑/卷207'),
    'https://en.wikipedia.org/wiki/Di_Renjie',
    'https://zh.wikipedia.org/wiki/' + urllib.parse.quote('狄仁杰'),
    'https://en.wikipedia.org/wiki/Lai_Junchen',
    'https://en.wikipedia.org/wiki/Judge_Dee',
    'https://en.wikipedia.org/wiki/Zhang_Jianzhi_(Tang_dynasty)',
    'https://en.wikipedia.org/wiki/Yao_Chong',
]

# Phiên âm tên nước ngoài/viết tắt trong lời đọc (khoá viết thường; không neo cảnh vào các từ này).
SAY = {'wikipedia': 'Uých-ki-pi-đi-a', 'cctv': 'Xi Xi Ti Vi', 'robert': 'Rô-bớt', 'van': 'Van', 'gulik': 'Gu-lích',
       'judge': 'Giắt', 'dee': 'Đi'}


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
        url = 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(f.replace(' ', '_'))
        credits.append(f'{name} — {author} — {lic} — {url}')
    credits.append('Cảnh minh họa chung (clip tạo bằng AI, không người, không chữ): ghi chú "MINH HỌA CHUNG" trên hình; không phải tư liệu.')
    assert len(TITLE) <= 60, len(TITLE)
    spec.update({
        'title': TITLE, 'channel': 'CL', 'theme': 'noir', 'look': LOOK, 'autoTr': True, 'master': True, 'craft': True,
        'endcard': 9, 'endcardSub': 'HỒ SƠ TIẾP THEO',
        'acc': ['địch nhân kiệt', 'võ tắc thiên', 'lai tuấn thần'], 'say': SAY, 'chapters': list(CH),
        # Cổng mức nhạc (final): từ #376 gain nhân vào mức tự cân (-14 dB); .27 -> khoảng -10 dB (.45 làm nhạc quá to).
        'mix_levels': {'CL': {'gain': 0.27, 'threshold': 0.08, 'ratio': 3.0}},
    })
    spec.pop('accent', None)
    yt = spec.setdefault('youtube', {})
    yt.update({
        'titles': TITLES,
        'summary': 'Địch Nhân Kiệt, vị tể tướng sống sót dưới chế độ mật vụ của Võ Tắc Thiên bằng một lời nhận tội "phản là thật" và một mảnh lụa giấu trong áo bông. '
                   'Từ cây bách ở Chiêu Lăng, Dự Châu, cuốn sổ tố giác của Lai Tuấn Thần đến cậu bé chưa mười tuổi và cuộc tranh ngôi thái tử: cái giá của việc cứu người giữa thời khủng bố.',
        'more': [],
        'sources': SOURCES,
        'tags': ['địch nhân kiệt', 'võ tắc thiên', 'lai tuấn thần', 'thần thám địch nhân kiệt', 'nhà đường', 'võ chu', 'lịch sử trung quốc', 'hồ sơ lịch sử'],
        'hashtags': ['DichNhanKiet', 'VoTacThien', 'HoSo'],
        'category': '24', 'thumb': 't1.jpg', 'publish_at': '2026-11-24T14:00:00Z', 'playlist': 'Ngoài Đời Thật',
        'chapter_titles': chapter_titles, 'video_credits': credits,
    })
    spec['approved'] = '13/11/2026 — duyet, ban tu dieu phoi theo cach tot nhat nhe, toi di ngu'
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('spec.json:', len(used_files), 'ảnh có ghi công,', len(SOURCES), 'nguồn')
