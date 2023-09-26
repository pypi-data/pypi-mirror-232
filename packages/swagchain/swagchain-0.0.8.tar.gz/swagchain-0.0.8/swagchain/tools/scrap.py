import asyncio
from typing import AsyncGenerator, List

from aiohttp import ClientSession, TCPConnector
from bs4 import BeautifulSoup  # pylint: disable=import-error

from ..llm import *
from ..memory import *
from ..utils import chunker, handle_errors, process_time, setup_logging

logger = setup_logging(__name__)

HEADERS = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
	"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}
BAD_EXT = (
	"png",
	"jpg",
	"jpeg",
	"gif",
	"pdf",
	"doc",
	"docx",
	"ppt",
	"pptx",
	"xls",
	"xlsx",
	"zip",
	"rar",
	"gz",
	"7z",
	"exe",
	"mp3",
	"mp4",
	"avi",
	"mkv",
	"mov",
	"wmv",
	"flv",
	"swf",
)

connector = TCPConnector(limit=1000)

logger = setup_logging(__name__)



@process_time
@handle_errors
async def sitemap_urls(url: str, session: ClientSession) -> List[str]:
	"""
	Fetches all urls from a sitemap
	"""
	urls: List[str] = []
	if not url.endswith("xml"):
		url = f"{url.rstrip('/')}/sitemap.xml"
	async with session.get(url) as response:
		text = await response.text()
		soup = BeautifulSoup(text, features="xml")
		for loc in soup.findAll("loc"):
			if loc.text.endswith(BAD_EXT):
				continue
			urls.append(loc.text)
			logger.info("Found url: %s", loc.text)
		for nested_sitemap in soup.findAll("sitemap"):
			urls.extend(await sitemap_urls(nested_sitemap.loc.text, session))
	return urls



@process_time
@handle_errors
async def fetch_website(url: str, session: ClientSession, max_size: int = 40960) -> str:
	"""
	Fetches a single website
	"""
	async with session.get(url) as response:
		html = await response.text()
		soup = BeautifulSoup(html, features="lxml")
		data = soup.get_text(strip=True,separator=" ")
		logger.info("Fetched %s", url)
		logger.info("Length: %s", len(data))
		return data[:max_size]


async def sitemap_pipeline(
	url: str,
	namespace: str,
	session: ClientSession,
	memory: Memory = Memory(),
	chunk_size: int = 64,
)->AsyncGenerator[float, None]:
	"""
	Fetches all urls from a sitemap
	"""
	urls: List[str] = await sitemap_urls(url, session)
	length: int = len(urls)
	inserted: int = 0
	while urls:
		try:
			chunk = urls[:chunk_size]
			urls = urls[chunk_size:]
			contents:list[str] = await asyncio.gather(
				*[fetch_website(url, session) for url in chunk]
			)
			
			for chunk in chunker(contents, 128):
				inserted += await memory.save(
					texts=list(chunk), namespace=namespace
				)
				progress = inserted / length
				logger.info("Progress: %s", progress)
				yield progress
				if progress >= 1:
					logger.info("Succesfully inserted %s documents", inserted)
					break
		except Exception as exc: # pylint: disable=broad-except
			logger.error(exc)
			continue
		

@process_time
@handle_errors
async def scrap_urls(url: str, session: ClientSession) -> List[str]:
	"""
	Find all children of a website
	"""
	async with session.get(url + "/index.html") as response:
		html: str = await response.text()
		soup = BeautifulSoup(html, features="lxml")
		results = soup.find_all("a", href=True)
		logger.info("Found %s results", len(results))
		responses: List[str] = []
		for result in results:
			if result["href"].startswith("http"):
				responses.append(result["href"])
			else:
				responses.append(f"{url.rstrip('/')}/{result['href'].lstrip('/')}")
		return responses


@process_time
@handle_errors
async def scrape_urls_recursive(url: str, session: ClientSession) -> List[str]:
	urls = await scrap_urls(url, session)
	"""
	Find all children of a website recursively
	"""
	for url in urls:
		urls.extend(await scrape_urls_recursive(url, session))
	return urls


async def scrape_pipeline(
	url: str,
	namespace: str,
	session: ClientSession,
	memory: Memory = Memory(),
	chunk_size: int = 64,
):
	"""
	Scrapes a website
	"""
	urls = await scrap_urls(url, session)
	logger.info("Found %s urls", len(urls))
	logger.info("Fetching all children")
	length = len(urls)
	inserted = 0
	while urls:
		chunk = urls[:chunk_size]
		urls = urls[chunk_size:]
		try:
			contents = await asyncio.gather(
				*[fetch_website(url, session) for url in chunk]
			)
			# Chunk each page into groups of 128 characters
			for chunk in chunker(contents, 128):
				inserted += await memory.save(
					texts=list(chunk), namespace=namespace
				)
				progress = inserted / length
				logger.info("Progress: %s", progress)
				yield progress
				if progress >= 1:
					logger.info("Succesfully inserted %s documents", inserted)
					break
		except Exception as exc: # pylint: disable=broad-except
			logger.error(exc)
			continue

async def website_loader(url: str, namespace: str) -> AsyncGenerator[float, None]:
	"""Reads a website and returns a list of strings"""
	async with ClientSession(connector=connector, headers=HEADERS) as session:
		exts = ["sitemap.xml", "index.html", ""]
		for e in exts:
			response = await session.get(url + "/" + e)
			if response.status == 200:
				if e == "sitemap.xml":
					async for progress in sitemap_pipeline(url, namespace, session):
						yield progress
				else:
					async for progress in scrape_pipeline(url, namespace, session):
						yield progress
				break
		else:
			logger.error("Could not find a sitemap.xml or index.html file")
			raise Exception("Could not find a sitemap.xml or index.html file")
