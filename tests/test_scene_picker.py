import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scene_picker',ROOT/'library/tools/scene_picker.py')
sp=importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
CAT=sp.load_json(sp.CATALOG)

class ScenePickerTests(unittest.TestCase):
    def profile(self, tags=None, forbidden=None, k=4):
        return {'window_k':k,'forbidden_types':forbidden or [],'tags':tags if tags is not None else sp.load_profile(None,'fs')['tags']}
    def test_multiple_meanings_and_separate_semantics(self):
        tags={x['tag'] for x in sp.classify('Năm 2020 có 40%, nhưng năm 2021 chỉ còn 20% ở Hà Nội.')}
        self.assertTrue({'co_cau','so_sanh','dong_thoi_gian','ban_do','anh_dia_danh'} <= tags)
        self.assertIn('co_cau',{x['tag'] for x in sp.classify('Cơ cấu chiếm 40%.')})
        self.assertIn('so_don',{x['tag'] for x in sp.classify('Có 40 người tham dự.')})
        self.assertNotIn('gio_trong_ngay',{x['tag'] for x in sp.classify('Người không bao giờ viết di chúc.')})
        self.assertIn('gio_trong_ngay',{x['tag'] for x in sp.classify('Lúc 9 giờ 30, trời đã tối.')})
        self.assertIn('gio_trong_ngay',{x['tag'] for x in sp.classify('Canh Tý vừa qua, trời sáng dần.')})
        self.assertNotIn('so_don',{x['tag'] for x in sp.classify('Năm 2020, vùng đất vẫn khô hạn.')})
    def test_fallback_for_unmatched(self):
        row={'id':'x','series':'fs','script':['Một ngày dài khép lại.'],'visuals':{},'media':{}}
        out,log=sp.choose(row,self.profile(),CAT)
        self.assertEqual({},out); self.assertTrue(log['decisions'][0]['fallback'])
    def test_locked_qa_never_selected(self):
        cat=json.loads(json.dumps(CAT)); next(x for x in cat['scenes'] if x['type']=='stat')['qa']['trang_thai']='khoa'
        prof=self.profile({'so_don':[{'type':'stat','requires':['mot_so_lieu']}]})
        row={'id':'x','series':'fs','script':['Có 42 người.'],'visuals':{},'media':{}}
        out,log=sp.choose(row,prof,cat)
        self.assertNotIn('stat',[x.get('type') for x in out.values()])
        self.assertIn('khóa QA',str(log['decisions'][0]['candidates']))
    def test_intervening_scene_breaks_streak(self):
        # Stat, list, then stat: intervening visual cuts the repeat run; new stat can be chosen.
        prof=self.profile({'so_don':[{'type':'stat','requires':['mot_so_lieu']}], 'liet_ke':[{'type':'list','requires':[]}]},k=1)
        row={'id':'x','series':'fs','script':['Có 11 người.','Danh sách gồm ba điều.','Có 12 người.'],'visuals':{'1':{'type':'stat'},'2':{'type':'list'}},'media':{}}
        out,_=sp.choose(row,prof,CAT)
        self.assertEqual('stat',out['3']['type'])
    def test_bud_rejects_all_fs_astrology_types(self):
        row={'id':'x','series':'bud','script':['Nạp âm theo tuổi Tý, nhìn quẻ kinh dịch.'],'visuals':{},'media':{}}
        out,log=sp.choose(row,sp.load_profile(None,'bud'),CAT)
        forbidden=sp.FS_ONLY
        self.assertFalse(forbidden & {v['type'] for v in out.values()})
    def test_deterministic(self):
        row={'id':'fixed','series':'fs','script':['Năm 2020 có 40 người, nhưng năm 2021 còn 20 người.'],'visuals':{},'media':{}}
        self.assertEqual(sp.choose(row,self.profile(),CAT),sp.choose(row,self.profile(),CAT))
    def test_custom_profile_without_code_change(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'profile.yaml'; p.write_text(json.dumps({'kenh':'custom','canh':{'window_k':2,'forbidden_types':[],'tags':{'so_don':[{'type':'stat','requires':['mot_so_lieu']}]}}}))
            self.assertEqual(2,sp.load_profile(str(p),'fs')['window_k'])
    def test_map_and_photo_are_distinct(self):
        tags={x['tag'] for x in sp.classify('Tại Hà Nội, quần thể di tích còn lưu dấu.')}
        self.assertIn('ban_do',tags); self.assertIn('anh_dia_danh',tags)
        profile=self.profile({'ban_do':[{'type':'map','requires':['dia_danh_trong_hf_geo']}], 'anh_dia_danh':[{'type':'photo','requires':['dia_danh_xac_dinh']}]})
        row={'id':'x','series':'fs','script':['Tại Hà Nội, quần thể di tích còn lưu dấu.'],'visuals':{},'media':{}}
        _,log=sp.choose(row,profile,CAT)
        candidates={x['type'] for x in log['decisions'][0]['candidates'] if x['eligible']}
        self.assertEqual({'map','photo'},candidates)
    def test_bud_profile_explicitly_excludes_astrology(self):
        p=sp.load_profile(None,'bud')
        for tag in ('nap_am','que_dich','sao_chieu_menh','so_cuu_cung','huong_phuong_vi','quan_he_con_giap'):
            self.assertNotIn(tag,p['tags'])
        self.assertTrue(sp.FS_ONLY <= set(p['forbidden_types']))
    def test_forbidden_types_come_from_profile_not_series(self):
        # series bud nhưng hồ sơ không cấm → vẫn chọn được cảnh tử vi
        prof=self.profile({'nap_am':[{'type':'napam','requires':['nam_sinh_or_can_chi']}]}, forbidden=[])
        row={'id':'x','series':'bud','script':['Nạp âm theo tuổi Tý.'],'visuals':{},'media':{}}
        out,log=sp.choose(row,prof,CAT)
        self.assertEqual('napam', out['1']['type'])
        self.assertNotIn('series', str(log['decisions'][0]['candidates']))
        # series fs nhưng hồ sơ cấm stat → không chọn stat
        prof2=self.profile({'so_don':[{'type':'stat','requires':['mot_so_lieu']}]}, forbidden=['stat'])
        row2={'id':'x','series':'fs','script':['Có 42 người.'],'visuals':{},'media':{}}
        out2,log2=sp.choose(row2,prof2,CAT)
        self.assertNotIn('stat',[v.get('type') for v in out2.values()])
        self.assertIn('hồ sơ kênh', str(log2['decisions'][0]['candidates']))
    def test_review_79r_false_meanings(self):
        c228='Huế dạy ta rằng, phong thủy giỏi nhất không phải là tìm được đất đẹp. Mà là biết **sống cùng** đất ấy, cả lúc nắng đẹp lẫn mùa nước lên.'
        c58='Con trưởng của ông là thái tử **Phù Tô**, người được coi là sẽ nối ngôi. Nhưng Phù Tô đang ở biên cương phía bắc.'
        c99='Trong đoạn văn về ngôi mộ, Tư Mã Thiên còn chép một chi tiết kỳ lạ: người ta lấy mỡ **nhân ngư** làm nến, tính cho cháy thật lâu không tắt.'
        c103='Đây là một ví dụ rõ về cách một chi tiết nhỏ trong sử sách, qua nhiều lần kể lại, biến thành một **lời đồn** huyền bí.'
        self.assertNotIn('ban_do', {x['tag'] for x in sp.classify(c228)})
        self.assertNotIn('so_sanh', {x['tag'] for x in sp.classify(c58)})
        self.assertNotIn('so_sanh', {x['tag'] for x in sp.classify(c99)})
        self.assertNotIn('liet_ke', {x['tag'] for x in sp.classify(c103)})
        prof=sp.load_profile(None,'fs')
        for text, banned in ((c228,'map'),(c58,'compare'),(c99,'compare'),(c103,'list')):
            out,_=sp.choose({'id':'x','series':'fs','script':[text],'visuals':{},'media':{}}, prof, CAT)
            self.assertNotEqual(banned, (out.get('1') or {}).get('type'))
        for title in ('**Chương 1: Ba lớp của tuổi Mão năm nay**','**Chương 6: Nhìn sang năm 2027**'):
            self.assertNotIn('so_don', {x['tag'] for x in sp.classify(title)})
            out,_=sp.choose({'id':'x','series':'fs','script':[title],'visuals':{},'media':{}}, prof, CAT)
            self.assertNotEqual('stat', (out.get('1') or {}).get('type'))
        self.assertIn('so_sanh', {x['tag'] for x in sp.classify('Năm 2020 có 40 người, nhưng năm 2021 còn 20 người.')})
        self.assertIn('liet_ke', {x['tag'] for x in sp.classify('Bộ gồm kim, mộc và thủy.')})
        self.assertIn('ban_do', {x['tag'] for x in sp.classify('Tại Hà Nội, quần thể di tích còn lưu dấu.')})
    def test_word_numbers_and_menh(self):
        self.assertEqual([700000.0], sp.quantities('Có bảy mươi vạn người.'))
        self.assertEqual([1974.0], sp.quantities('một nghìn chín trăm bảy mươi tư'))
        self.assertEqual([1888.0], sp.quantities('một nghìn tám trăm tám mươi tám'))
        self.assertEqual([88.0], sp.quantities('tám mươi tám'))
        self.assertEqual([2.0], sp.quantities('sâu chừng hai mét'))
        self.assertEqual([], sp.quantities('Năm một nghìn chín trăm bảy mươi tư.'))
        self.assertEqual([], sp.quantities('Tháng Ba năm một nghìn chín trăm bảy mươi tư.'))
        self.assertEqual([], sp.quantities('Một vùng quê nghèo.'))
        self.assertEqual([], sp.quantities('Kỷ Mão 1999'))
        self.assertEqual([], sp.quantities('thế kỷ mười sáu'))
        self.assertIn('dong_thoi_gian', {x['tag'] for x in sp.classify('Sách thế kỷ mười sáu gọi là sông Kim Trà.')})
        self.assertNotIn('so_don', {x['tag'] for x in sp.classify('Sách thế kỷ mười sáu gọi là sông Kim Trà.')})
        self.assertIn('so_don', {x['tag'] for x in sp.classify('Có bảy mươi vạn người.')})
        self.assertIn('nap_am', {x['tag'] for x in sp.classify('Mệnh của bạn là Kim Bạch Kim.')})
        self.assertNotIn('nap_am', {x['tag'] for x in sp.classify('Nhà vua khấn: đâu dám không vâng mệnh.')})
        self.assertNotIn('nap_am', {x['tag'] for x in sp.classify('Thêm một lớp nữa là sao chiếu mệnh.')})
        self.assertNotIn('dong_thoi_gian', {x['tag'] for x in sp.classify('**Chương 2: Quý Mão 1963**')})
        if sp._atlas_centroids():  # tên nước cần world-atlas trong chunks_cache (không có trên CI)
            self.assertIn('Nhật Bản', sp.gazetteer())
            self.assertIn('ban_do', {x['tag'] for x in sp.classify('Tại Nhật Bản, ngôi chùa còn lưu dấu.')})
    def test_compass_dirs_required(self):
        prof=sp.load_profile(None,'fs')
        text='Vì sao người Việt thích nhà hướng Nam?'
        out,log=sp.choose({'id':'x','series':'fs','script':[text],'visuals':{},'media':{}}, prof, CAT)
        self.assertEqual('compass', out['1']['type'])
        self.assertEqual([{'dir':'south','label':'Nam','at':1}], out['1']['dirs'])
        out2,_=sp.choose({'id':'x','series':'fs','script':['Chỉ nói la bàn, không nêu hướng.'],'visuals':{},'media':{}}, prof, CAT)
        self.assertNotEqual('compass', (out2.get('1') or {}).get('type'))
        # Hướng chéo bị bỏ qua: compass chỉ có ô Đông/Tây/Nam/Bắc/Trên/Dưới, ép về Bắc/Nam sẽ sai nghĩa (79br).
        self.assertEqual([], sp.extract_dirs('Nhà hướng đông bắc đón gió.'))
        self.assertEqual(['east'], [d['dir'] for d in sp.extract_dirs('Cửa hướng đông bắc, bếp hướng đông.')])
        self.assertTrue(log['decisions'][0]['timeline_source'] in ('tts','uoc_a_plus_4'))
    def test_timeline_real_seconds_else_estimate_flag(self):
        script=['Có 11 người.','Câu nối giữa.','Có 12 người.']
        segs=[{'start':0,'end':10},{'start':10,'end':20},{'start':20,'end':30}]
        prof=self.profile({'so_don':[{'type':'stat','requires':['mot_so_lieu']}]})
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.json'
            p.write_text(json.dumps({'segments':segs}), encoding='utf-8')
            row={'id':'x','series':'fs','script':script,'visuals':{},'media':{'1':{'kind':'image'}},'_tts_json':str(p)}
            out,log=sp.choose(row, prof, CAT)
            self.assertEqual('tts', log['timeline_source'])
            self.assertEqual('stat', out['3']['type'])
            self.assertNotIn('2', out)
        row2={'id':'khong_co_tts_79b','series':'fs','script':script,'visuals':{},'media':{'1':{'kind':'image'}}}
        out2,log2=sp.choose(row2, prof, CAT)
        self.assertEqual('uoc_a_plus_4', log2['timeline_source'])
        self.assertEqual({}, out2)

if __name__=='__main__': unittest.main()
