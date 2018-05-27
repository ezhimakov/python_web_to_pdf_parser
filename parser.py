from html_to_pdf import HtmlToPdfParser

scraper = HtmlToPdfParser()
scraper.get_working_sources()
scraper.get_file_format()
scraper.download_to_pdf()
