import time
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

import csv


InnerBlock = namedtuple('Block', 'title, price, date, url')     #create namedtuple

class Block(InnerBlock):
    
    def __str__(self):
        return f'{self.title}\t{self.price}\t{self.date}\t{self.url}'       #create str method for namedtuple


class AvitoParser:

    def __init__(self):
        self.session = requests
        self.session.headers = {'User-Agent' :'{Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                                'Accept-Language' : 'ru'
                               }                                      #use headers for login on avito.ru

    def get_page(self, page: int = None):
        params = {
            'radius': 100,
            'user': 1                                              #create getpage func with params of url
            }
        if page and page > 1:
            params['p'] = page

        url = 'https://www.avito.ru/sankt-peterburg/predlozheniya_uslug/nyani_sidelki-ASgBAgICAUSYC6ifAQ?cd=1'
        # url = 'https://www.avito.ru/sankt-peterburg?q=iphone/'
        r = self.session.get(url, params=params)
        return r.text       

    def pagination_limit(self):
        text = self.get_page()                                       #func for search a search maximum pages 
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select('span.pagination-item-1WyVp')
        last_button = container[-2]
        return int(last_button.text)

    def parse_block(self, item):
        url_block = item.select_one('a.snippet-link')             #func for getting all html code and creating a block with information
        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru' + href
        else:
            url = None

        title_block = item.select_one('a.snippet-link')
        title_block = title_block.string.strip()
        
        price_block = item.select_one('span.snippet-price')
        price_block = price_block.get_text('\n')
        price_block = list(filter(None, map(lambda i: i.strip(), price_block.split('\n'))))
        if len(price_block) == 1:
            price = price_block[0]
        else:
            price = None
            print('Что-то пошло не так при записи цены ')
         

        date_block = item.select_one('div.snippet-date-info')
        date_block = date_block.get('data-tooltip')
        
        return Block(
            url=url,
            title=title_block,
            price=price,
            date=date_block,
            
        )

    def get_blocks(self, page:int = 2):                         #func for getting inf.block and parsing him
        text = self.get_page(page=page)                         
        soup = BeautifulSoup(text, 'lxml')
        container = soup.select('div.item.item_table.clearfix.js-catalog-item-enum.item-with-contact.js-item-extended')
        i=1
        for item in container:
            block = self.parse_block(item=item)
            i += 1
            with open('avito.csv', 'a') as f:
                writter = csv.writer(f)
                writter.writerow(block)
            
    def parse_all(self):                                          #func for parse all pages from search query 
        limit = self.pagination_limit()
        print(f'Всего {limit} страниц')
        for i in range(1, limit + 1):
            if i % 2 == 0:
                time.sleep(9)
            self.get_blocks(page=i)
            

def main():
    p = AvitoParser()                                      #point of entry 
    p.parse_all()
    
    
if __name__ == "__main__":
    main()
