import urllib.request as u,json,concurrent.futures
H={'User-Agent':'Mozilla/5.0','Referer':'https://www.printables.com/','Origin':'https://www.printables.com'}
def download(pair):
 a,b=pair
 Q={'query':'mutation($printId:ID!,$ids:[ID!]!,$ft:DownloadFileTypeEnum!){getDownloadLink(printId:$printId,source:model_detail,files:[{fileType:$ft,ids:$ids}]){ok errors{field messages code} output{link ttl}}}','variables':{'printId':str(a),'ids':[str(b)],'ft':'stl'}}
 with u.urlopen(u.Request('https://api.printables.com/graphql/',data=json.dumps(Q).encode(),headers={**H,'Content-Type':'application/json'})) as r:url=json.load(r)['data']['getDownloadLink']['output']['link']
 with u.urlopen(u.Request(url,headers=H)) as r:open(str(b)+'.geom','wb').write(r.read())
with concurrent.futures.ThreadPoolExecutor() as ex:list(ex.map(download,[(1747851,7280858),(872878,3689772),(1441905,6064460)]))
