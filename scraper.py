import mechanicalsoup
import time
import json
from timeit import default_timer as timer
import re
from unidecode import unidecode

SITE = "https://wolnelektury.pl/"  # Default site to work on, tested.


class Scrapper:
    def __init__(self, site):
        """
        Webscrapper that extracts text data from wolne lektury site.
        parameters
        ----------
        site : string
        the site from which the data are taken
        attributes
        ----------
        linksOnPage : list
        links to the fanfics
        downloaded : list
        list of all downloaded fanfics
        """
        self.__original_site = site
        self.site = site
        self.__browser = mechanicalsoup.StatefulBrowser(raise_on_404=True)
        self.response = self.__browser.open(self.site)
        self.linksOnPage = list()
        self.linksToDownload = list()


    def open_site(self, site):
        """ Opens the site """
        self.__browser.open(site)
        self.site = self.__browser.get_url()
        return site
        

    def follow_link(self, follow_link):
        """ Follows the link passed as an input """
        self.__browser.follow_link(follow_link)
        return (self.__browser.get_url())

    def filter_catalog(self,Filters = ['gatunek'],FilterValues= ['wiersz'],
                       epoch = 'pozytywizm',genre = 'wiersz',author = 'adam-asnyk'):
        """ Filters the fanficts looking for only the desired settings """
        URL = str(self.__browser.get_url())
        print(URL)
        self.author = author
        try:
            FilterSet = 'katalog'
            for i in range(len(Filters)):
                FilterSet += f'/{Filters[i]}/{FilterValues[i]}'
                newURL = f'{str(URL)}{FilterSet}'
        except:
            FilterSet = ''
            Filters = ['epoka', 'gatunek','autor']  # list of desired filters
            FilterValues = [epoch,genre,author]  # list of values for filters
            FilterSet = ''
            for i in range(len(Filters)):
                FilterSet += f'{Filters[i]}/{FilterValues[i]}/'
            newURL = f'{str(URL)}katalog/{FilterSet}'
        return newURL
        
    def preparing_links(self):
        """This module is tasked with finding all links to stories on a search
         page of fanfiction.net. It takes a ResultSet of URLs, extracted from
         StatefulBrowser, and runs a regular expression.
        To reduce calcultions, the module searches only for links to the last
         chapters of stories. Then it reconstructs links to the firsts.
         Yeah, it's faster that way."""

        all_links = self.__browser.links()
        self.linksOnPage = re.findall(r'katalog/lektura/[a-z-]+/', str(all_links))
        return self.linksOnPage
    
    def detect_txt(self,link):
        self.open_site(SITE + link)
        #detect links
        all_links = self.__browser.links()
        #acquire text, for check purposes
        txt = self.__browser.get(self.__original_site + link).text
        #check whether text is in english
        check = re.findall(r'<a>English</a>',txt)
        if (len(check) < 1):
            self.linksOnPage = re.findall(r'media/book/txt/[a-z-]+.txt', str(all_links))
            try:
                # return link to txt version
                return self.linksOnPage[0]
            except:
                # audiobook or no txt version file
                print('Detecting text info: No txt version available')
        else:
            print('Detecting text info: English text, dismissed')
            
    @staticmethod
    def clean_txt(txt):
        text = re.sub('\r','',txt)
        text = re.sub(r'[\n]+','\n',text)
        try:
            text = text.split('-----')[:-1]
        except:
            pass
        return ''.join(text)
    
    def download_txt(self,link):
        text = self.__browser.get(self.__original_site + link).text
        text = self.clean_txt(text)
        return text
    