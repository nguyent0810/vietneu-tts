import json,sys,urllib.parse,urllib.request,re
UA={"User-Agent":"vietneu-tts/1.0 (pilot131 research preview)"}
def api(**p):
    p.update(format="json")
    return json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p),headers=UA),timeout=60))
def search(q,n=12):
    return [x["title"] for x in api(action="query",list="search",srnamespace=6,srlimit=n,srsearch=q)["query"]["search"]]
def info(titles):
    r=api(action="query",prop="imageinfo",iiprop="url|size|extmetadata",iiurlwidth=2000,titles="|".join(titles))
    out=[]
    for pg in r["query"]["pages"].values():
        ii=(pg.get("imageinfo") or [{}])[0]; m=ii.get("extmetadata",{})
        g=lambda k: re.sub("<[^>]+>","",m.get(k,{}).get("value",""))[:80]
        out.append(dict(title=pg["title"],w=ii.get("width"),h=ii.get("height"),thumb=ii.get("thumburl"),lic=g("LicenseShortName"),artist=g("Artist"),date=g("DateTimeOriginal")))
    return out
if __name__=="__main__":
    for q in sys.argv[1:]:
        print("==",q)
        for x in info(search(q)): print(x["w"],x["h"],x["lic"],"|",x["artist"][:40],"|",x["title"])
