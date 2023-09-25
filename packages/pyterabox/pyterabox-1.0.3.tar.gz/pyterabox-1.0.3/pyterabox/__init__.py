from json import loads
from bs4 import BeautifulSoup
import asyncio
import aiohttp

async def download(url):
	ids = url.split("/")[-1]
	async with aiohttp.ClientSession() as session:
		async with session.get(f"https://terabox-dl.qtcloud.workers.dev/api/get-info?shorturl={ids}&pwd=") as resp:
			html = await resp.text()
		data = loads(html)
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
		async with session.post("https://terabox-dl.qtcloud.workers.dev/api/get-download",json=body,headers={"Content-Type":"application/json"}) as resp:
			html = await resp.text()
		data2 = loads(html)
		url = data2["downloadLink"]
		return (data["list"][0]["filename"],data["list"][0]["size"],url,session)