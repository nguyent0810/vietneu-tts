import json
from pathlib import Path

items = [
 ('ck-e5-thuong-tet-khau-tru', 'lib198/ai_22.png'),
 ('ck-e6-bon-trieu-tam-rut-mot-lan', 'lib198b/ai_44.png'),
 ('ck-a2-mot-nua-sau-muoi-sau-nam', 'lib198/ai_26.png'),
 ('ck-e5-mot-dua-tre-mot-to-dang-ky', 'lib198b/ai_31.png'),
 ('ck-e6-tro-cap-540-nghin', 'lib198b/ai_34.png'),
 ('ck-a2-thang-chin-nam-phay', 'lib198b/ai_39.png'),
 ('ck-dien-sinh-hoat-bac-mot-1901', 'lib198/ai_28.png'),
 ('ck-ho-kinh-doanh-duoi-mot-ty', 'lib198/ai_27.png'),
 ('ck-tran-tro-cap-that-nghiep-26-trieu', 'lib198/ai_31.png'),
]
for slug, asset in items:
    path = Path('data/stier/specs') / (slug + '.json')
    with path.open(encoding='utf-8') as f:
        spec = json.load(f)
    spec['imgs']['opening'] = 'local:output/asset_library/' + asset
    opening = spec['scenes'][0]
    opening['type'] = 'photo'
    opening['label'] = opening.pop('items')[0]['text']
    opening['mode'] = 'full'
    opening['img'] = 'opening'
    opening['credit'] = False
    for scene in spec['scenes']:
        if scene['type'] == 'ledger':
            scene['type'] = 'cards3d'
            scene['cards'] = scene.pop('rows')
    with path.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
        f.write('\n')
