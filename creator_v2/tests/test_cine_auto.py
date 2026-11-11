import copy

from motion.long import cine_auto, floor, scene_params


def scenes():
    return [{'type': 'photo', 'img': 'a', 't0': i * 4, 't1': (i + 1) * 4} for i in range(30)]


def test_cine_deterministic_coverage_and_variety():
    a, b = scenes(), scenes()
    cine_auto.Director('topic').apply(a, {})
    cine_auto.Director('topic').apply(b, {})
    assert a == b
    stats = cine_auto.distribution(a)
    assert stats['cam_pct'] >= 60 and stats['longest_run'] == 1
    assert len(stats['cams']) >= 3
    assert all(s.get('frame') is False for s in a)
    assert not scene_params.validate_topic([('ch', a)])['errors']
    assert floor.cine_warning(a) is None


def test_cine_preserves_manual_fields_and_text_background():
    manual = {'type': 'photo', 'img': 'a', 'cam': 'pan', 'fx': 'fog', 'frame': True, 'transition_in': 'whip', 't0': 0, 't1': 5}
    original = copy.deepcopy(manual)
    text = {'type': 'question', 'bg': 'a', 'text': 'why', 't0': 5, 't1': 10}
    cine_auto.Director('x').apply([manual, text], {})
    assert manual == original
    assert text['cam'] in {'push_in', 'pan'}


def test_cine_pano_respects_limits_and_anchors():
    s = {'type': 'photo', 'img': 'wide', 't0': 0, 't1': 12, 'stops': [{'x': 0, 'at': 1}, {'x': .4, 'at': 10}]}
    cine_auto.Director('x', total_duration=100).apply([s], {'wide': {'w': 2400, 'h': 1000}})
    assert s['type'] == 'pano'
    assert not scene_params.validate_topic([('ch', [s])])['errors']
    s = {'type': 'photo', 'img': 'wide', 't0': 0, 't1': 12, 'stops': [{'x': 0, 'at': 1}, {'x': .4, 'at': 10}]}
    cine_auto.Director('x', total_duration=100, existing_panos=6).apply([s], {'wide': {'w': 2400, 'h': 1000}})
    assert s['type'] == 'photo'


def test_cine_fx_context_and_warning():
    a = scenes()
    cine_auto.Director('x').apply(a, {}, context='cơn mưa')
    assert all(s['fx'] == 'rain' for s in a if s.get('fx'))
    assert floor.cine_warning(scenes())


def test_cine_alternates_text_and_image_cameras():
    sequence = [
        {'type': 'kinetic', 'bg': 'a', 'items': [], 't0': 0, 't1': 4},
        {'type': 'slam', 'bg': 'a', 'text': 'x', 't0': 4, 't1': 8},
        {'type': 'photo', 'img': 'a', 't0': 8, 't1': 12},
        {'type': 'question', 'bg': 'a', 'text': 'x', 't0': 12, 't1': 16},
    ]
    cine_auto.Director('x').apply(sequence, {})
    cams = [s['cam'] for s in sequence if s.get('cam')]
    assert all(a != b for a, b in zip(cams, cams[1:]))


def test_cine_broll_is_opt_in_and_restricted():
    scene = {'type': 'broll', 'vid': 'v', 't0': 0, 't1': 5}
    cine_auto.Director('x').apply([scene], {})
    assert 'cam' not in scene
    scene['cam'] = 'pan'
    assert scene_params.validate_topic([('ch', [scene])])['errors']
