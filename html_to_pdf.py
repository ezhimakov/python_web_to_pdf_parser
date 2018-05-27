import json, requests, bs4, os, sys
from xhtml2pdf import pisa
import time, re
from urllib.parse import urlparse



class HtmlToPdfParser():
	"""parse web pages and saving to pdf file"""
	def __init__(self):
		os.makedirs('pdf', exist_ok=True)
		os.makedirs('html', exist_ok=True)
		os.makedirs('doc', exist_ok=True)

		filename = 'sources.json'
		try:
			with open(filename, encoding='utf-8') as f_obj:
				self.sources = json.load(f_obj)
		except FileNotFoundError:
			print('JSON-файл с источниками не найден')
			sys.exit()

	def get_working_sources(self):
		print("Выберите источники(введите номер через запятую либо нажмите 'Ввод' для выбора всех):")
		for key, source in enumerate(self.sources):
			print(str(key) + ': ' + source['url'])

		source_choices = input()
		
		if(source_choices == ""):
			return self.sources
		else:
			choosed_nums = []
			choosed_sources = []
			sources_indexes = source_choices.split(",")
			for i in sources_indexes:
				if(int(i) not in choosed_nums):
					choosed_nums.append(int(i))

			print("Выбранные источники:\n")
			for num in choosed_nums:
				if num in range(0, len(self.sources)):
					choosed_sources.append(self.sources[num])
					print(str(num)+": "+str(self.sources[num]['url'])+"\n")	

			self.sources = choosed_sources
				
			return self.sources

	def get_file_format(self):
		fileformat = input("Выберите формат файла:\n0: PDF\n1: docx\n")

		format_list = ['PDF', 'doc']

		self.file_format = format_list[int(fileformat)]

		return self.file_format


	def download_to_pdf(self):
		timestr = time.strftime("%Y%m%d-%H%M%S")

		pdf_string = """<html><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"><style type="text/css">@page { size: A4; margin: 1cm; }@font-face {font-family: Dejavu;src: url(\""""+os.getcwd()+"""/dejavu.ttf\");}html, body, h2{font-family: Dejavu;font-size: 11pt;}
		a:link:after, a:visited:after { content:" [" attr(href) "] "; }
		a{
		color:#000;
		text-decoration:none;
		}
		img{
		max-height:300px;
		}
		</style></head><body>"""
		for source in self.sources:
			res = requests.get(source['url'])
			res.raise_for_status()

			sitepath = urlparse(source['url'])
			replacing_link = sitepath.scheme+'://'+sitepath.hostname
						
			working_page = bs4.BeautifulSoup(res.text, "html5lib")

			article_elements = working_page.select(str(source['selector']))
			
			heading = '<h2>Ресурс: '+str(source['url'])+'</h2><h2>'+str(source['heading'])+'</h2>'

			pdf_string += heading
			for article in article_elements:
				# foundLinks = links_on_resource.findall(str(article))
				# print(foundLinks)

				soup = bs4.BeautifulSoup(str(article), "html5lib")
				
				for a in soup.findAll('a'):
  					a['href'] = a['href'].replace(a['href'], replacing_link+a['href'])

				for img in soup.findAll('img'):
					if(img['src'].startswith('http')==False):
						img['src'] = img['src'].replace(img['src'], replacing_link+img['src'])
								
				pdf_string += str(soup)

			print("Генерирую файл\n")

		if(self.file_format=='PDF'):
			outputFilename = timestr+".pdf"				
			resultFile = open(os.getcwd()+"/pdf/"+outputFilename, "w+b")				
			pisaStatus = pisa.CreatePDF(pdf_string, dest=resultFile, encoding='UTF-8')
			
			resultFile.close()

			print('Готово. Сохранённый файл находится в папке /pdf')
			return
		else:
			outputFilename = timestr+".html"
			resultFile = open(os.getcwd()+"/html/"+outputFilename, "w", encoding="utf-8")
			resultFile.write(pdf_string)
			resultFile.close()
			#output = pypandoc.convert(source=os.getcwd()+'/html/'+outputFilename, format='html', to='docx', outputfile='/doc/'+timestr+'.docx', extra_args=['-RTS'])
			print('Готово. Сохранённый файл находится в папке /html')


