#!/usr/bin/env python3
"""Refresh a structured global radio catalogue from Radio Browser and Akashvani indexes."""
import hashlib, json, os, re, urllib.parse, urllib.request
from datetime import datetime, timezone
import pycountry

OUT="catalogue/data/radio-directory.json"
RB="https://de1.api.radio-browser.info"
UA="PTTRadioCatalogue/1.0 (+public directory refresh)"
TAG_FEEDS=["news","talk","folk","jazz","classical","dance","party","indian","bollywood","hindi","devotional","sports","culture","weather","rock","pop","electronic","world","community","oldies","reggae","hip-hop","ambient"]
GENRE_MAP={"news":["news"],"talk":["talk","debate","interview"],"folk":["folk","traditional"],"jazz":["jazz"],"classical":["classical","opera"],"party":["party","dance","club"],"indian":["indian","bollywood"],"devotional":["devotional","religious","bhajan"],"sports":["sports"],"culture":["culture","community"],"weather":["weather"],"rock":["rock"],"pop":["pop"],"electronic":["electronic","edm"],"world":["world"],"oldies":["oldies","classic hits"],"reggae":["reggae"],"hip-hop":["hip-hop","rap"],"ambient":["ambient","chill"]}
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.loads(r.read().decode("utf-8"))
def split(v):
    if isinstance(v,list):return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip().lower() for x in re.split(r"[,;/|]",str(v or "")) if x.strip()]
LANGUAGE_ALIASES={"arabi":"Arabic","arapça":"Arabic","arabic.":"Arabic","eng":"English","hindi":"Hindi","gujarati":"Gujarati","marathi":"Marathi","bengali":"Bengali","punjabi":"Punjabi","tamil":"Tamil","telugu":"Telugu","kannada":"Kannada","malayalam":"Malayalam","urdu":"Urdu","assamese":"Assamese","arabesk":"","portuguese":"Portuguese","spanish":"Spanish","french":"French","german":"German","japanese":"Japanese","chinese":"Chinese","nepali":"Nepali"}
def canonical_country(code,raw):
    country=pycountry.countries.get(alpha_2=str(code or "").upper())
    return country.name if country else (str(raw or "").strip() or "Unknown")
def canonical_languages(values):
    out=set()
    for raw in values:
        v=re.sub(r"\s+"," ",str(raw).strip().strip(" .,:;()[]")).casefold()
        if not v: continue
        alias=LANGUAGE_ALIASES.get(v)
        if alias is not None:
            if alias: out.add(alias)
            continue
        try:
            lang=pycountry.languages.lookup(v)
            label=getattr(lang,"name",None) or getattr(lang,"common_name",None)
            if label: out.add(label)
        except LookupError:
            continue
    return sorted(out) or ["Unknown"]
def canonical_region(country_code,raw):
    value=str(raw or "").strip()
    if not value or not country_code: return ""
    cc=str(country_code).upper()
    if "-" in value and value.split("-",1)[0].upper()==cc:
        sub=pycountry.subdivisions.get(code=value.upper())
        if sub: return sub.name
    key=re.sub(r"[^a-z0-9]","",value.casefold())
    for sub in pycountry.subdivisions:
        if sub.country_code==cc and re.sub(r"[^a-z0-9]","",sub.name.casefold())==key: return sub.name
    return ""
def genres(tags,name):
    text=" ".join([name.lower()]+[x.lower() for x in tags]); found=[g for g,words in GENRE_MAP.items() if any(w in text for w in words)]
    return found or ["general"]
def normalise(s):
    url=str(s.get("url_resolved") or s.get("url") or "").strip();name=str(s.get("name") or "").strip()
    if not name or not url.startswith(("http://","https://")):return None
    tags=split(s.get("tags"));langs=canonical_languages(split(s.get("language")))
    try:lat=float(s.get("geo_lat")) if s.get("geo_lat") not in (None,"") else None;lon=float(s.get("geo_long")) if s.get("geo_long") not in (None,"") else None
    except (ValueError,TypeError):lat=lon=None
    uid=str(s.get("stationuuid") or hashlib.sha256(url.encode()).hexdigest()[:20])
    return {"id":"rb-"+uid,"name":name,"country":canonical_country(s.get("countrycode"),s.get("country")),"countrycode":str(s.get("countrycode") or "").upper(),"region":canonical_region(s.get("countrycode"),s.get("state")),"city":str(s.get("city") or ""),"language":langs,"genres":genres(tags,name),"tags":tags,"url":url,"homepage":str(s.get("homepage") or ""),"codec":str(s.get("codec") or ""),"bitrate":int(s.get("bitrate") or 0),"geo_lat":lat,"geo_long":lon,"clickcount":int(s.get("clickcount") or 0),"source":"Radio Browser","verified":"directory-listed"}
def main():
    by_url={};sources={}
    feeds=[("popular",RB+"/json/stations/topclick/10000")]+[("tag:"+t,RB+"/json/stations/bytag/"+urllib.parse.quote(t)+"?limit=500") for t in TAG_FEEDS]
    for name,url in feeds:
        try:
            rows=fetch(url);sources[name]=len(rows)
            for row in rows:
                item=normalise(row)
                if item:
                    old=by_url.get(item["url"])
                    if old:
                        old["genres"]=sorted(set(old["genres"]+item["genres"]));old["tags"]=sorted(set(old["tags"]+item["tags"]))
                    else:by_url[item["url"]]=item
        except Exception as e:sources[name+"_error"]=str(e);print("Feed failed",name,e)
    # Add official public broadcaster entries when the upstream Akashvani list is available.
    try:
        raw=fetch("https://raw.githubusercontent.com/codito/akashvani/master/stations.json")
        rows=raw if isinstance(raw,list) else raw.get("stations",raw.get("data",[]));sources["akashvani"]=len(rows)
        for s in rows:
            name=str(s.get("name") or s.get("station_name") or "").strip();url=str(s.get("stream_url") or s.get("url") or "").strip()
            if not name or not url.startswith(("http://","https://")):continue
            lang=canonical_languages(split(s.get("language")));uid=str(s.get("epg_id") or hashlib.sha256(url.encode()).hexdigest()[:16])
            by_url[url]={"id":"air-"+uid,"name":name,"country":"India","countrycode":"IN","region":canonical_region("IN",s.get("state") or s.get("region")),"city":str(s.get("city") or ""),"language":lang,"genres":genres(["public service","india"]+lang,name),"tags":["akashvani","india","public service"],"url":url,"homepage":"","codec":"HLS" if ".m3u8" in url.lower() else "","bitrate":0,"geo_lat":None,"geo_long":None,"clickcount":0,"source":"Akashvani public catalogue","verified":"directory-listed"}
    except Exception as e:sources["akashvani_error"]=str(e);print("Akashvani unavailable",e)
    items=sorted(by_url.values(),key=lambda x:(x["country"].casefold(),x["region"].casefold(),x["name"].casefold()))
    unique=lambda key:sorted({v for x in items for v in x.get(key,[]) if v and v.lower() not in ("unknown","various")})
    payload={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"station_count":len(items),"country_count":len({x["country"] for x in items}),"countries":sorted({x["country"] for x in items if x["country"]!="Unknown"}),"regions":sorted({x["region"] for x in items if x["region"]}),"languages":unique("language"),"genres":unique("genres"),"sources":sources,"stations":items,"note":"Discovery index only. Availability and rebroadcast rights are not guaranteed."}
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,"w",encoding="utf-8") as f:json.dump(payload,f,ensure_ascii=False,indent=2);f.write("\n")
    print("Published",len(items),"stations across",payload["country_count"],"countries")
if __name__=="__main__":main()
