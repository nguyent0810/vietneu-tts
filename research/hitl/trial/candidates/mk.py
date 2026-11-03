import json,sys
def C(cid,summ,title,thumb,ff,v,esc,pay,claims,why,tags):
    return dict(candidate_id=cid,angle_summary=summ,title=title,thumbnail_text=thumb,first_frame_0_1s=ff,voice_0_3s=v,escalation_3_10s=esc,payoff=pay,claims=[dict(field=a,span=b,fact_ids=c) for a,b,c in claims],why_this_angle=why,tags_for_history=dict(zip(['mechanism','opener_shape','first_frame_type','title_shape'],tags)))
def save(topic,channel,fmt,sc,cands):
    d=dict(topic_id=topic,channel=channel,format=fmt,publish_date="2026-11-20",series_context=sc,video_id=topic+"_v1",candidates=cands)
    for c in cands:
        lim=70 if fmt=="Long" else 50
        assert len(c['title'])<=lim,(c['title'],len(c['title']))
    json.dump(d,open(topic+".json","w"),ensure_ascii=False,indent=1)
