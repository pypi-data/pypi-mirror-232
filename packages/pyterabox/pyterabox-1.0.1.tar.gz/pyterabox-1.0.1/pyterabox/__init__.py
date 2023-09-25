import requests
from json import loads
from bs4 import BeautifulSoup

session = requests.session()

def download(url):
	ids = url.split("/")[-1]
	resp = session.get(f"https://terabox-dl.qtcloud.workers.dev/api/get-info?shorturl={ids}&pwd=")
	data = loads(resp.text)
	body = {
		'shareid': data["shareid"],
		'uk': data["uk"],
		'sign': data["sign"],
		'timestamp': data["timestamp"],
	}
	try:
		body['fs_id'] = data["list"][0]["children"][0]["fs_id"]
	except:
		body['fs_id'] = data["list"][0]["fs_id"]
	resp = session.post("https://terabox-dl.qtcloud.workers.dev/api/get-download",json=body,headers={"Content-Type":"application/json"})
	data2 = loads(resp.text)
	url = data2["downloadLink"]
	return {"filename":data["list"][0]["filename"],"filesize":data["list"][0]["size"],"url":url}