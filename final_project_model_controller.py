import sqlite3
from requests_oauthlib import OAuth1
import json
from datetime import date
import requests
import sys
from bs4 import BeautifulSoup
import secret_data
import csv
import re
import plotly.plotly as py
import plotly.graph_objs as go


today = date.today()
db_name = 'final_proj_db.sqlite'


consumer_key = secret_data.CONSUMER_KEY
consumer_secret = secret_data.CONSUMER_SECRET
access_token = secret_data.ACCESS_KEY
access_secret = secret_data.ACCESS_SECRET



url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
requests.get(url, auth=auth).text



CACHE_FNAME = "best_seller.json"
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

READING_CACHE = "reading_list.json"
try:
    cache_file = open(READING_CACHE, 'r')
    reading_list_contents = cache_file.read()
    READING_LIST = json.loads(reading_list_contents)
    cache_file.close()
except:
    READING_LIST = []


class Book():
    def __init__(self, isbn = "none", author = "no author", publication_year = "none", title = "no title", avg_rating = "none", num_ratings = "none", num_reviews = "none", ratings_list = [], description = "none", sql = None, json = None, bs = None):
        if sql == None and json == None and bs == None:
            self.isbn = isbn
            self.author = author
            self.publication_year = publication_year
            self.title = title
            self.avg_rating = avg_rating
            self.num_ratings = num_ratings
            self.num_reviews = num_reviews
            self.ratings = ratings_list
            self.description = description
            self.bs = None
        elif sql != None:
            self.init_from_sql(sql)
        elif json != None:
            self.init_from_json(json)
        elif bs != None:
            self.init_from_bs(bs)

    def init_from_sql(self, sql):
        self.isbn = sql[5]
        self.author = sql[24]
        self.publication_year = sql[8]
        self.title = sql[10]
        self.avg_rating = sql[12]
        self.num_ratings = sql[13]
        self.num_reviews = sql[15]
        self.ratings = [sql[16],sql[17],sql[18],sql[19],sql[20]]
        self.description = 'No desc yet.'
        self.bs = None


    def __str__(self):
        if self.bs == None:
            return "Title: {}\nAuthor: {}\nPublication Year: {}\nReviewed {} times with an average rating of {}.\n".format(self.title, self.author, self.publication_year, str(self.num_reviews), self.avg_rating)
        else:
            return "Title: {}\nAuthor: {}\nPublication Year: {}\nNumber {} on the best seller list and has been on the list for {} full weeks.\n".format(self.title, self.author, self.publication_year, str(self.rank), self.rank_time)


    def plot_ratings(self):
        '''
        Method on a book to plot the distribution of ratings for that book
        params: self
        return: bar chart
        '''
        ratings_array = self.ratings
        trace0 = go.Bar(
                    x=['1', '2', '3', '4', '5'],
                    y=ratings_array
            )
        data = [trace0]
        layout = go.Layout(
            title = "Distribution of ratings for "+self.title,
        )
        fig = go.Figure(data=data, layout=layout)
        return py.plot(fig, filename='basic-bar')

    def add_to_list(self):
        '''
        method that adds the modified book to your reading list. Because it is a modifier on a book object, you must do this AFTER initializing the book object from the DB search or BS search
        params: self
        return: Updates the new cache and saves it.
        '''
        READING_LIST.append(self.__dict__)
        print(self.title + ' added to your reading list.')
        dumped_json_cache = json.dumps(READING_LIST)
        fw = open(READING_CACHE,"w")
        fw.write(dumped_json_cache)
        fw.close()

    # def remove_from_list(self):
    #     list_spot = READING_LIST.index(self)
    #     READING_LIST.pop(list_spot)
    #     print(self.title + ' removed from your reading list.')
    #     dumped_json_cache = json.dumps(READING_LIST)
    #     fw = open(READING_CACHE,"w")
    #     fw.write(dumped_json_cache)
    #     fw.close()


    def init_from_json(self, json):
        self.isbn = json['isbn']
        self.author = json['author']
        self.publication_year = json['publication_year']
        self.title = json['title']
        self.avg_rating = json['avg_rating']
        self.num_ratings = json['num_ratings']
        self.num_reviews = json['num_reviews']
        self.ratings = json['ratings']
        self.description = json['description']
        self.bs = None

    def init_from_bs(self, bs):
        self.bs = 'Best Seller'
        self.isbn = 'No ISBN on record.'
        self.author = bs[3]
        self.publication_year = str(today)[:4]
        self.title = bs[0]
        self.avg_rating = 0
        self.num_ratings = 'No ratings on record.'
        self.num_reviews = 0
        self.rank = bs[1]
        self.rank_time = bs[2]
        self.ratings = 'No ratings on record.'
        self.description = bs[4]

    # def init_from_xml(self, xml):
    #     self.title = xml.find('title').text
    #     self.author = xml.find('name').text
    #     self.description = ''
    #     self.review_count = int(xml.find('text_reviews_count').text)
    #     self.rating = xml.find('average_rating').text
    #     self.ratings_count = xml.find('ratings_count').text
    #     self.publication = xml.find('original_publication_year').text





class Author():
    def __init__(self, name = "no name", fan_count = 0, followers = 0, about = "n/a", influences = 'n/a', works_count = 0, gender = 'none', hometown = 'none', born = 'n/a', died = 'n/a', sql = None):

        if sql != None:
            self.init_from_sql(sql)

        else:
            self.name = name
            self.fan_count = fan_count
            self.followers = followers
            self.about = about
            self.influences = influences
            self.works_count = works_count
            self.gender = gender
            self.hometown = hometown
            self.born = born
            self.died = died
            self.xml = xml

    def init_from_sql(self,sql):
        self.name = sql[1]
        self.gender = sql[2]
        self.age = sql[3]
        self.hometown = sql[4]
        self.works_count = sql[5]
        self.followers = sql[6]
        about_search = sql[7]
        open_carot = 0
        while open_carot != -1:
            open_carot = about_search.find("<")
            close_carot = about_search.find(">")
            about_search = about_search[:open_carot]+about_search[close_carot+1:]
        self.about = about_search

    # def init_from_xml(self, xml):
    #     self.name = xml.find('name').text
    #     self.fan_count = xml.find('fans_count').text
    #     self.followers = xml.find('author_followers_count').text
    #     self.about = xml.find('about').string
    #     author_influences = []
    #     influences = xml.find('influences')
    #     self.influences =influences
    #     self.born = xml.find('born_at').text
    #     born = self.born.split('/')
    #     born_year = int(born[0])
    #     born_month = int(born[2])
    #     born_day = int(born[1])
    #     self.age = today.year - born_year - ((today.month, today.day) < (born_month, born_day))
    #     self.works_count = xml.find('works_count').text
    #     self.gender = xml.find('gender').text
    #     self.hometown = xml.find('hometown').text
    #     self.died = xml.find('died_at').text
    #     self.xml = xml

    def __str__(self):
        return "Author: {}\nGender: {}\nAge: {}\nHometown: {}\nNumber of Publications: {}\nNumber of Followers: {}\n".format(self.name, self.gender, self.age, self.hometown, self.works_count, self.followers)

# def amazon_request(baseurl):
#     unique_ident = params_unique_combination(baseurl)
#     if unique_ident in CACHE_DICTION:
#         print("Getting cached data...")
#         return CACHE_DICTION[unique_ident]
#     else:
#         print("Making a request for new data...")
#         header = {'User-Agent': 'University_class'}
#         page_text = requests.get(baseurl, headers=header).text
#         CACHE_DICTION[unique_ident] = page_text
#         dumped_json_cache = json.dumps(CACHE_DICTION)
#         fw = open(CACHE_FNAME,"w")
#         fw.write(dumped_json_cache)
#         fw.close()
#         return CACHE_DICTION[unique_ident]




def params_unique_combination(baseurl, params_diction = {}, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_diction.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_diction[k]))
    return baseurl + "_".join(res)


def load_help_text():
    with open('help.txt') as f:
        return f.read()


def get_from_nyt_best_seller(type):
    '''
    API request to NYT Best Seller list
    Params: takes param for which list to get results from
    - combined-print-and-e-book-fiction
    - combined-print-and-e-book-nonfiction
    - science
    Return: Returns a list of book objects
    '''
    baseurl = "https://api.nytimes.com/svc/books/v3/lists.json"
    params_diction = {}
    params_diction["api-key"] = secret_data.nyt_key
    params_diction["list"] = type
    unique_ident = params_unique_combination(baseurl,params_diction)
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        # print(CACHE_DICTION[unique_ident])
        search_results = CACHE_DICTION[unique_ident]
        return search_results
    else:
        print("Making a request for new data...")
        nyt_resp = requests.get(baseurl, params = params_diction
        # auth = auth
        )
        nyt_text = nyt_resp.text
        nyt_data_obj = json.loads(nyt_text)
        CACHE_DICTION[unique_ident] = nyt_data_obj
        # dumped_json_cache = json.dumps(CACHE_DICTION)
        dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys=True,indent=4,separators=(',',': '))
        # print(dumped_json_cache)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        search_results = CACHE_DICTION[unique_ident]
        return search_results
    # make list of book objects
    # book_list = []
    # for i in range(len(search_results['results'])):
    #     new_book = Book(json = search_results['results'][i])
    #     book_list.append(new_book)
    # return book_list

# def isbn_from_bslist():
#     bs_to_gr = []
#     for item in CACHE_DICTION.keys():
#         for i in CACHE_DICTION[item]['results']:
#             bs_to_gr.append(i['isbns'][0]['isbn10'])
#     return bs_to_gr
#
# def get_book_info_from_bs(isbn_list):
#     '''
#     API request to Goodreads for review of a book
#     Params: takes the book title and the author
#     Returns: tuple of the book title and the description
#     '''
#     for isbn in isbn_list:
#         baseurl = "https://www.goodreads.com/search/index.xml"
#         params_diction = {}
#         params_diction['q'] = isbn
#         # params_diction['search[field]'] = 'title'
#         params_diction["key"] = secret_data.goodreads_key
#         unique_ident = params_unique_combination(baseurl,params_diction)
#         # print("Making a request for new data...")
#         goodreads_resp = requests.get(baseurl, params = params_diction
#         )
#         goodreads_text = goodreads_resp.text
#         search_soup = BeautifulSoup(goodreads_text, "xml")
#         return search_soup
#         title_search = search_soup.find('title').text
#         # print(title_search)
#         review_search = search_soup.find('description').text
#         open_carot = 0
#         while open_carot != -1:
#             open_carot = review_search.find("<")
#             close_carot = review_search.find(">")
#             review_search = review_search[:open_carot]+review_search[close_carot+1:]
#         return (title_search,review_search)
#
# isbns = ['152479628X', '0316273945']
# print(get_book_info_from_bs(isbns))

def get_book_description(title,author):
    '''
    API request to Goodreads for review of a book
    Params: takes the book title and the author
    Returns: tuple of the book title and the description
    '''
    baseurl = "https://www.goodreads.com/book/title.xml"
    params_diction = {}
    params_diction['title'] = title
    params_diction['author'] = author
    params_diction["key"] = secret_data.goodreads_key
    unique_ident = params_unique_combination(baseurl,params_diction)
    # print("Making a request for new data...")
    goodreads_resp = requests.get(baseurl, params = params_diction
    )
    goodreads_text = goodreads_resp.text
    search_soup = BeautifulSoup(goodreads_text, "xml")
    title_search = search_soup.find('title').text
    # print(title_search)
    review_search = search_soup.find('description').text
    open_carot = 0
    while open_carot != -1:
        open_carot = review_search.find("<")
        close_carot = review_search.find(">")
        review_search = review_search[:open_carot]+review_search[close_carot+1:]
    return (title_search,review_search)

# print(get_book_description("Dune","Frank Herbert"))

def author_db_search(author_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    select = 'SELECT * FROM Authors '
    where = 'WHERE name LIKE \'%' + author_name + '%\''
    statement = select+where
    cur.execute(statement)
    tup_list = cur.fetchall()
    acc = 0
    book_place_dict = {}
    header = 'Author Search'
    print(header)
    for author in tup_list:
        acc = int(acc)
        acc+=1
        acc = str(acc)+' '
        print_list = []
        print_list.append(acc + author[1])
        print(*print_list, sep=' ')
    return tup_list

def best_seller_db_search(bs_list):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    if bs_list == 'fiction':
        search_param = 'Combined Print and E-Book Fiction'
    elif bs_list == 'non-fiction':
        search_param = 'Combined Print and E-Book Nonfiction'
    elif bs_list == 'science':
        search_param = 'Science'
    else:
        return "No Best Seller list with that name."
    select1 = 'SELECT Best_Seller.Title, Best_Seller.Rank, Best_Seller.Weeks_on_list, Authors.Name, Best_Seller.Description FROM Best_Seller'
    join1 = " JOIN Authors ON Best_Seller.Author = Authors.Id"
    where1 = ' WHERE List_name LIKE \'%' + search_param + '%\''
    statement1 = select1+join1+where1
    # print(statement)
    cur.execute(statement1)
    tup_list1 = cur.fetchall()

    select2 = 'SELECT Title, Rank, Weeks_on_list, Author, Description FROM Best_Seller'
    where2 = ' WHERE List_name LIKE \'%' + search_param + '%\''
    where3 = ' AND (Author LIKE \'%a%\' OR Author LIKE \'%e%\' OR Author LIKE \'%i%\' OR Author LIKE \'%o%\' OR Author LIKE \'%u%\')'

    statement2 = select2+where2+where3
    # print(statement2)
    cur.execute(statement2)
    tup_list2 = cur.fetchall()
    tup_list = tup_list1 + tup_list2
    tup_list = sorted(tup_list, key=lambda x: x[1])

    tup_for_print = []
    for item in tup_list:
        tup_for_print.append((item[0],item[3]))
    row_num = 0
    table_spacing = [0,0]
    param_strings = []
    for tup in tup_for_print:
        for i in range(0,len(tup)):
            max_len = table_spacing[i]
            if type(tup[i]) == type('string'):
                if len(tup[i]) > max_len:
                    table_spacing[i] = len(tup[i])
            else:
                table_spacing[i] = 5
    for i in table_spacing:
        param_strings.append('{0: <'+str(i)+'}')
    acc = 0
    book_place_dict = {}
    header = ['#  Title','   Author']
    header_list = []
    for i in range(0,len(header)):
        header_list.append(param_strings[i].format(header[i]))
    print(*header_list, sep=' ')
    for tup in tup_for_print:
        acc = int(acc)
        acc+=1
        if acc <10:
            acc = str(acc)+' '
        acc = str(acc)
        print_list = []
        print_list.append(acc)
        book_place_dict[acc.rstrip()] = tup_for_print.index(tup)
        for i in range(0,len(tup)):
            print_list.append(param_strings[i].format(tup[i]))
        print(*print_list, sep=' ')
    return tup_list


def search_book_database(book='', author='',sort='avg_rating',top='10'):
    '''
    database search for books
    Params: book search term, author search term, sort type, number or results
    Return: list of tuples with title, author, and average rating
    '''
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    if sort == 'avg_rating':
        third_param = 'average_rating'
    elif sort == "ratings_count":
        third_param = 'ratings_count'
    elif sort == 'review_count':
        third_param = 'work_text_reviews_count'
    select = "SELECT * "
    # select = "SELECT title, authors, " + third_param
    frm = " FROM Books"
    join = " JOIN Authors ON Books.authors = Authors.Id"
    where = ''
    if book != '' and author == '':
        where = " WHERE title LIKE \'%" + book + "%\'"
    elif author != '' and book == '':
        where = " WHERE Authors.name LIKE \'%" + author + "%\'"
    else:
        where = " WHERE title LIKE %" + title + "% AND author LIKE %" + author + "%"
    sort = " ORDER BY " + third_param
    t_b = " DESC limit " + top
    statement = select+frm+join+where+sort+t_b
    # print(statement)
    cur.execute(statement)
    tup_list = cur.fetchall()
    tuple_response = tup_list
    tup_for_print = []
    if third_param == 'average_rating':
        for tup in tuple_response:
            author = tup[24].split(',')[0]
            tup_for_print.append((tup[10],author,tup[12]))
    if third_param == 'ratings_count':
        for tup in tuple_response:
            author = tup[24].split(',')[0]
            tup_for_print.append((tup[10],author,tup[13]))
    if third_param == 'work_text_reviews_count':
        for tup in tuple_response:
            author = tup[24].split(',')[0]
            tup_for_print.append((tup[10],author,tup[14]))
    row_num = 0
    table_spacing = [0,0,0]
    param_strings = []
    for tup in tup_for_print:
        for i in range(0,len(tup)):
            max_len = table_spacing[i]
            if type(tup[i]) == type('string'):
                if len(tup[i]) > max_len:
                    table_spacing[i] = len(tup[i])
            else:
                table_spacing[i] = 5
    for i in table_spacing:
        param_strings.append('{0: <'+str(i)+'}')

    acc = 0
    book_place_dict = {}
    for tup in tup_for_print:
        acc = int(acc)
        acc+=1
        print_list = []
        if acc <10:
            acc = str(acc)+' '
        acc = str(acc)
        print_list.append(acc)
        book_place_dict[acc.rstrip()] = tup_for_print.index(tup)
        for i in range(0,len(tup)):
            print_list.append(param_strings[i].format(tup[i]))
        print(*print_list, sep=' ')
    return tuple_response


def show_reading_list():
    '''
    displays your reading list (Num, Title, Author, Avg Rating)
    params: none
    return: list of dictionaries for the books that had been stored in json, would need to be reconstructed into objects if you want to use objects again
    '''
    tup_for_print = []
    for item in READING_LIST:
        tup_for_print.append((item['title'],item['author'],item['avg_rating']))
    row_num = 0
    table_spacing = [0,0,0]
    param_strings = []
    for tup in tup_for_print:
        for i in range(0,len(tup)):
            max_len = table_spacing[i]
            if type(tup[i]) == type('string'):
                if len(tup[i]) > max_len:
                    table_spacing[i] = len(tup[i])
            else:
                table_spacing[i] = 5
    for i in table_spacing:
        param_strings.append('{0: <'+str(i)+'}')

    acc = 0
    book_place_dict = {}
    for tup in tup_for_print:
        acc = int(acc)
        acc+=1
        print_list = []
        if acc <10:
            acc = str(acc)+' '
        acc = str(acc)
        print_list.append(acc)
        book_place_dict[acc.rstrip()] = tup_for_print.index(tup)
        for i in range(0,len(tup)):
            print_list.append(param_strings[i].format(tup[i]))
        print(*print_list, sep=' ')
    # return book_place_dict
    return READING_LIST


def remove_from_list(number):
    '''
    removes a book from your reading list. Must be looking at the reading list
    params: requres the number on the list of the book you want to remove
    return: None
    '''
    book_popped = READING_LIST.pop(int(number)-1)
    print(book_popped['title'] + ' removed from your reading list.')
    dumped_json_cache = json.dumps(READING_LIST)
    fw = open(READING_CACHE,"w")
    fw.write(dumped_json_cache)
    fw.close()
    return None

def plot_reading_list():
    '''
    plots a pie chart of ratings on reading list
    params: none
    return: pie chart
    '''
    avg_rating_list = []
    for item in READING_LIST:
        avg_rating_list.append(round(item['avg_rating'],1))
    labels = []
    for item in avg_rating_list:
        if item not in labels:
            labels.append(item)
    values = []
    for item in labels:
        values.append(0)
    for item in avg_rating_list:
        index_spot = labels.index(item)
        values[index_spot]+=1
    trace = go.Pie(labels=labels, values=values)
    layout = go.Layout(
        title = "Distribution of Ratings on Reading List",
    )
    fig = go.Figure(data=[trace],layout=layout)
    return py.plot(fig, filename='basic_pie_chart')



# if __name__ == '__main__':
    # author_search = input('author: ')
    # tuple_response = search_book_database(author = author_search, sort = 'ratings_count')
    # user_input = input("enter a number: ")
    # num_three = tuple_response[int(user_input)-1]
    # print(num_three[0])
    # book_test = Book(sql = num_three) # this is where you create the objects
    #
    #
    # print(book_test)
    # book_options = ''
    # while book_options != 'exit':
    #     book_options = input("plot, description, add, remove, exit: ")
    #     if book_options=='plot':
    #         book_test.plot_ratings()
    #     elif book_options=='description':
    #         print(book_test.description)
    #     elif book_options=='add':
    #         book_test.add_to_list()
    #     elif book_options=='remove':
    #         book_test.remove_from_list()
    #
    # print('\n')
    # print(show_reading_list())
    # removal = input("which to remove: ")
    # remove_from_list(removal)
    # print(show_reading_list())

    # get_from_nyt_best_seller('combined-print-and-e-book-fiction')
    # get_from_nyt_best_seller('combined-print-and-e-book-nonfiction')
    # get_from_nyt_best_seller('science')




# print(plot_reading_list())

# def goodreads_title_search(search_request, type = "isbn"):
#     baseurl = "https://www.goodreads.com/search/index.xml"
#     params_diction = {}
#     params_diction["q"] = search_request
#     params_diction["key"] = secret_data.goodreads_key
#     params_diction["search[field]"] = type
#     unique_ident = params_unique_combination(baseurl,params_diction)
#     if unique_ident in CACHE_DICTION:
#         print("Getting cached data...")
#         print(unique_ident)
#         search_results =  CACHE_DICTION[unique_ident]
#         search_soup = BeautifulSoup(search_results, "xml")
#         book_search = search_soup.find_all('work')
#         book_list = []
#         for book in book_search:
#             new_book = Book(xml = book)
#             book_list.append(new_book)
#         sorted_list = sorted(book_list, key = lambda book:book.review_count , reverse = True)
#         print('\nSearch for {}:\n'.format(search_request))
#         for book in sorted_list:
#             print('{} - Rated {} times with an average rating of {}.'.format(book.title, str(book.ratings_count), book.rating))
#         return None
#     else:
#         print("Making a request for new data...")
#         goodreads_resp = requests.get(baseurl, params = params_diction
#         # auth = auth
#         )
#         goodreads_text = goodreads_resp.text
#         print(unique_ident)
#         CACHE_DICTION[unique_ident] = goodreads_text
#         dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys=True,indent=4,separators=(',',': '))
#         fw = open(CACHE_FNAME,"w")
#         fw.write(dumped_json_cache)
#         fw.close()
#         search_results =  CACHE_DICTION[unique_ident]
#         search_soup = BeautifulSoup(search_results, "xml")
#         book_search = search_soup.find_all('work')
#         book_list = []
#         for book in book_search:
#             new_book = Book(xml = book)
#             book_list.append(new_book)
#         sorted_list = sorted(book_list, key = lambda book:book.review_count , reverse = True)
#         print('\nSearch for {}:\n'.format(search_request))
#         for book in sorted_list:
#             print('{} - Rated {} times with an average rating of {}.'.format(book.title, str(book.ratings_count), book.rating))
#         return None
#
# def goodreads_author_search(search_request, type = "author"):
#     baseurl = "https://www.goodreads.com/search/index.xml"
#     params_diction = {}
#     params_diction["q"] = search_request
#     params_diction["key"] = secret_data.goodreads_key
#     params_diction["search[field]"] = type
#     unique_ident = params_unique_combination(baseurl,params_diction)
#     if unique_ident in CACHE_DICTION:
#         print("Getting cached data...")
#         # print(CACHE_DICTION[unique_ident])
#         search_results =  CACHE_DICTION[unique_ident]
#         search_soup = BeautifulSoup(search_results, "xml")
#         book_search = search_soup.find_all('work')
#         print(book_search[0])
#         book_list = []
#         for book in book_search:
#             new_book = Book(xml = book)
#             book_list.append(new_book)
#         sorted_list = sorted(book_list, key = lambda book:book.review_count, reverse = True)
#         print('\nSearch for {}:\n'.format(search_request))
#         for book in sorted_list:
#             print('{} - Rated {} times with an average rating of {}.'.format(book.title, str(book.ratings_count), book.rating))
#         return None
#     else:
#         print("Making a request for new data...")
#         goodreads_resp = requests.get(baseurl, params = params_diction
#         # auth = auth
#         )
#         goodreads_text = goodreads_resp.text
#         CACHE_DICTION[unique_ident] = goodreads_text
#         dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys=True,indent=4,separators=(',',': '))
#         fw = open(CACHE_FNAME,"w")
#         fw.write(dumped_json_cache)
#         fw.close()
#         search_results = CACHE_DICTION[unique_ident]
#         search_soup = BeautifulSoup(search_results, "xml")
#         book_search = search_soup.find_all('work')
#         book_list = []
#         for book in book_search:
#             new_book = Book(xml = book)
#             book_list.append(new_book)
#         sorted_list = sorted(book_list, key = lambda book:book.review_count, reverse = True)
#         print('\nSearch for {}:\n'.format(search_request))
#         for book in sorted_list:
#             print('{} - Rated {} times with an average rating of {}.'.format(book.title, str(book.ratings_count), book.rating))
#         return None
#
# def goodreads_review_search(id):
#     baseurl = "https://www.goodreads.com/book/show.json"
#     params_diction = {}
#     params_diction["id"] = id
#     params_diction["key"] = secret_data.goodreads_key
#     #params_diction["rating"] = rating
#     unique_ident = params_unique_combination(baseurl,params_diction)
#     if unique_ident in CACHE_DICTION:
#         print("Getting cached data...")
#         # print(CACHE_DICTION[unique_ident])
#         return CACHE_DICTION[unique_ident]
#     else:
#         print("Making a request for new data...")
#         nyt_resp = requests.get(baseurl, params = params_diction
#         # auth = auth
#         )
#         nyt_text = nyt_resp.text
#         nyt_data_obj = json.loads(nyt_text)
#         CACHE_DICTION[unique_ident] = nyt_data_obj
#         # dumped_json_cache = json.dumps(CACHE_DICTION)
#         dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys=True,indent=4,separators=(',',': '))
#         # print(dumped_json_cache)
#         fw = open(CACHE_FNAME,"w")
#         fw.write(dumped_json_cache)
#         fw.close()
#         return CACHE_DICTION[unique_ident]

    # if unique_ident in CACHE_DICTION:
    #     print("Getting cached data...")
    #     search_results = CACHE_DICTION[unique_ident]
    #     search_soup = BeautifulSoup(search_results, "xml")
    #     return search_soup
    # else:
    #     print("Making a request for new data...")
    #     goodreads_resp = requests.get(baseurl, params = params_diction
    #     # auth = auth
    #     )
    #     goodreads_text = goodreads_resp.text
    #     CACHE_DICTION[unique_ident] = goodreads_text
    #     dumped_json_cache = json.dumps(CACHE_DICTION, sort_keys=True,indent=4,separators=(',',': '))
    #     fw = open(CACHE_FNAME,"w")
    #     fw.write(dumped_json_cache)
    #     fw.close()
    #     search_results = CACHE_DICTION[unique_ident]
    #     search_soup = BeautifulSoup(search_results, "xml")
    #     return search_soup





# enders_search = goodreads_author_search("Terry Pratchett")
# book_search = enders_search.find_all('work')
# print(book_search[0])
#
# book_list = []
# for book in book_search:
#     new_book = Book(xml = book)
#     book_list.append(new_book)
# sorted_list = sorted(book_list, key = lambda book:book.review_count , reverse = True)
# for book in sorted_list:
#     print(book.__str__())




## Additional Functions

# Add book shelf
    # add the To-Read shelf
# Add a book to a shelf
    # can also remove
# Get the books on a members shelf


# Google Books
# https://developers.google.com/books/docs/v1/getting_started
    # REST in the Books API

    # https://www.programmableweb.com/api/google-books/sample-source-code
    # book information, ratings, reviews

# Barnes and Nobles API
    # price
    # https://www.programmableweb.com/api/abundant-barnes-noble-price

# use the books.csv
    # (Pie) graph the proportion of books from genres (with 4 or 5 stars)
        # would need to find genre from some API (Goodreads or Google Books)
    # (Bar) graph the quantities of books with each review type
    # (Scatter) graph correlation between number of reviews and average rating
    # get the NY Times best sellers, and chart title, reviews, ratings
