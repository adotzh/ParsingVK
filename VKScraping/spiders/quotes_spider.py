import scrapy
from scrapy import Spider, Request
import dateparser
def parse_id(link, pointer):
    link = str(link)
    split = link.find(pointer) 
    + len(pointer)
    if link.find(pointer) == 0:
        split = 0
    return link[split:] 

class QuotesSpider(Spider):

    name = "quotes"
    allowed_domains = ["vk.com"]
    
    likes = {}     

    def start_requests(self):
        user_id = "1"
        main_url = 'https://vk.com/id%s' % user_id
        yield Request(url = main_url, callback = self.parse)
    
 
    def parse(self, response):
        result = {}
        with open('test.html', 'wb') as output_file:
            output_file.write(response.body)
        self.log('Saved file test.html')
        #загаловок страницы
        interim = response.xpath('//*[@id="page_info_wrap"]/div[1]/h2/text()').extract_first()
        # id_personal = str(response)
        # print('!!!!!!!', id_personal.split('/'))        
        # result['id'] = id_personal.split('/')[len(id_personal.split('/')) - 1]
        if (interim != ''):
            interim = interim.split(' ')
            if len(interim) == 2:
                result['first_name'] = interim[0]
                result['last_name'] = interim[1]
                result['nikename'] = ''
            elif len(interim) == 3:
                result['first_name'] = interim[0]
                result['last_name'] = interim[2]
                result['nikename'] = interim[1]
            else:
                result['first_name'] = interim[0]
                result['last_name'] = ''
                result['nikename'] = ''
        else: 
            result['first_name'] = ''
            result['last_name'] = ''
            result['nikename'] = ''
        interim = response.xpath('//*[@id="page_info_wrap"]/div[1]/div[1]/div[2]/text()').extract_first()
        if interim != '':
            mass = interim.split(' ')
            date = ''
            if mass[0] == 'заходила':
                result['sex'] = 'women'
            elif mass[0] == 'заходил':
                result['sex'] = 'men'

            if len(mass) > 1:
                for i in range(1, len(mass)):
                    date += mass[i] + ' '
                result['last_seen'] = dateparser.parse(date)
            else: 
                result['last_seen'] = interim

        #основной блок
        interim = response.xpath('//*[@id="profile_short"]/div')
        for main in interim:
            full_date = ''
            str_name = main.xpath('div[@class="label fl_l"]/text()').extract_first()
            if str_name is not None:
                str_name = str(str_name).replace(':', '')
                if str_name == 'День рождения':
                    date = main.xpath('div[@class="labeled"]/a/text()').extract()
                    for i in range(len(date)):
                        full_date += date[i] + ' '
                    result['date_of_birth'] = dateparser.parse(full_date)     

                else:
                    result[main.xpath('div[@class="label fl_l"]/text()').extract_first()] = main.xpath('div[@class="labeled"]/a/text()').extract_first()
            else:
                break
        for main in response.xpath('//*[@id="profile_full"]/div'):
            i = 1
            big_head = main.xpath('div[@class="profile_info_header_wrap"]/span/text()').extract_first()
            result[big_head] = {}
            if (big_head == 'Карьера'):
                for path in main.xpath('div[@class="profile_info"]/div'):
                    full_information = {}
                    head = path.xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                    if head is not None:
                        full = path.xpath('div[@class="labeled"]/a/text()').extract()
                        if full != []:
                            if len(full) >= 3:
                                full_information['link'] = response.urljoin(path.xpath('div[@class="labeled"]/a[@class="fl_r profile_career_group"]/@href').extract_first())
                                full_information['team'] = full[2]
                                full_information['position'] = full[3]
                            elif len(full) == 2:
                                full_information['team'] = full[0]
                                full_information['position'] = full[1]
                            else:
                                full_information['team'] = full[0]
                        if path.xpath('div[@class="labeled"]/text()').extract() != []:
                            full_information['city'] = path.xpath('div[@class="labeled"]/text()').extract_first().split(', ')[0]
                            date = str(path.xpath('div[@class="labeled"]/text()').extract_first().split(', ')[1]).split('–')
                            if len(date) == 2:
                                full_information['start_date'] = date[0]
                                full_information['end_date'] = date[1]
                            elif len(date) == 1:
                                full_information['start_date'] = date[0][2:6]
                        if result[big_head].get(head) is not None :
                            stack = []
                            stack.append(result[big_head][head])
                            stack.append(full_information)
                            result[big_head][head] = stack
                        else:
                            result[big_head][head] = full_information
            elif (big_head == 'Образование'):
                path = main.xpath('div[@class="profile_info"]/div[@class="clear_fix profile_info_row "]')
                stack = []
                for i in range(len(path)):
                    full_information = {}
                    place = path[i].xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                    if place == 'Вуз':
                        head = place
                        text = path.xpath('div[@class="labeled"]/a/text()').extract()
                        if len(text) == 1:
                            full_information = text[0]
                        elif len(text) == 2:
                            full_information[text[0]] = {}
                            full_information[text[0]]['year'] = text[1]
                        for k in range(i + 1, len(path)):
                            if len(path) >= k:
                                next_page = path[k].xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                                print('!!!!!!!!!!!!!!', next_page)    
                                if next_page != []:
                                    if next_page[0] != 'Вуз':
                                        full_information[text[0]][next_page[0]] = main.xpath('div[@class="profile_info"]/div[%d]/div[@class="labeled"]' %k)
                                    else: 
                                        break

                        stack.append(full_information)
                    result[big_head][head] = stack
                path = main.xpath('div[@class="profile_info"]/div[@class="clear_fix profile_info_row block"]')
                stack = []
                for i in range(len(path)):
                    place = path[i].xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                    full_information = {}
                    if place != '':
                        head = place
                        text = path[i].xpath('div[@class="labeled"]/a/text()').extract()
                        print('!!!!!!!!!!!  text%d' %i, text)
                        if len(text) == 1:
                            full_information = text[0]
                        elif len(text) == 2:
                            full_information[text[0]] = {}
                            if len(text[1].split(',')) == 1:
                                full_information[text[0]]['where'] = text[1].split(',')[0]
                            elif len(text[1].split(',')) == 2:
                                full_information[text[0]]['where'] = text[1].split(',')[0]
                                if len(text[1].split(',')[1].split('-')) == 2:
                                    full_information[text[0]]['from'] = text[1].split(',')[1].split('-')[0]
                                    full_information[text[0]]['to'] = text[1].split(',')[1].split('-')[1]
                                else:
                                    full_information[text[0]]['year'] = text[1].split(',')[1]
                        else:
                            full_information[text[0]] = {}
                            if len(text[1].split(',')) == 1:
                                full_information[text[0]]['where'] = text[1].split(',')[0]
                            elif len(text[1].split(',')) == 2:
                                full_information[text[0]]['where'] = text[1].split(',')[0]
                                if len(text[1].split(',')[1].split('-')) == 2:
                                    full_information[text[0]]['from'] = text[1].split(',')[1].split('-')[0]
                                    full_information[text[0]]['to'] = text[1].split(',')[1].split('-')[1]
                                else:
                                    full_information[text[0]]['year'] = text[1].split(',')[1]
                    stack.append(full_information)
                result[big_head][head] = stack
            else:
                for littel_main in main.xpath('div[@class="profile_info"]/div'):
                    if (littel_main.xpath('div[@class="label fl_l"]/text()').extract() != []) and (littel_main.xpath('div[@class="labeled"]/a/text()').extract() != []):
                        head = littel_main.xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                        if len(littel_main.xpath('div[@class="labeled"]/a/text()').extract()) == 1:
                            result[big_head][head] = littel_main.xpath('div[@class="labeled"]/a/text()').extract_first()
                        else:
                            result[big_head][head] = littel_main.xpath('div[@class="labeled"]/a/text()').extract()
                    else:
                        head = littel_main.xpath('div[@class="label fl_l"]/text()').extract_first().replace(':', '')
                        result[big_head][head] = littel_main.xpath('div[@class="labeled"]/text()').extract()
        #численная информация
        # for main in response.xpath('//*[@id="wide_column"]/div[1]/div[2]/a'):
        #     result[main.xpath('div[@class="label"]/text()').extract_first()] = main.xpath('div[@class="count"]/text()').extract_first()

        # photo_page = response.xpath('//*[@id="wide_column"]/div[1]/div[2]/a[2]/@href').extract_first()
        # print("!!!!!!!!", photo_page)
        # yield response.follow(photo_page, self.like)
        yield result

    
    
#     def like(self, response):
# #        for album in response.xpath('//*[@id="photos_container_photos"]/div[@class="photos_row_wrap"]'):
# #            for photo in album.xpath('div[@class="photos_row "]'):
# #                link = photo.xpath('a/@href').extract_first()
# #                yield response.follow(link, self.counter)

#         link = response.xpath('//*[@id="photo_row_1_456317315"]/a/@href').extract_first()
#         yield response.follow(link, self.counter)

#     def counter(self, response):
#         print('!!!!!!!', response.css('pv_narrow > div.ui_scroll_overflow > div.ui_scroll_blocker > div > div > div.ui_scroll_content.clear_fix > div.like_wrap._like_photo1_456317315 > div > div.like_btns').extract())
#         print('!!!!!!!!!!', response.xpath('//*[@id="pv_narrow"]/div[1]/div[1]/div/div/div[1]/div[3]/div/div[1]/a[2]/div[3]/text()').extract())
# #        count_likes = response.xpath('//*div[@class="like_btns"]/a[@class="like_btn like _like"]/div[@class="like_button_count"]/text()').extract()
# #        print('!!!!!!!!!!!', count_likes)
# #main = response.xpath('//*[@id="profile_full"]/div')



