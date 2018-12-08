import sqlite3
import sys
import csv
from requests_oauthlib import OAuth1
import json
from datetime import date
import time
import requests
from bs4 import BeautifulSoup
import secret_data
import random
today = date.today()


AUTHOR_CACHE = "authors.csv"
try:
    author_file = open(AUTHOR_CACHE, 'r')
    author_contents = author_file.read()
    AUTHOR_DIRECTORY = json.loads(AUTHOR_contents)
    author_file.close()
except:
    author_DIRECTORY = {}



def params_unique_combination(baseurl, params_diction = {}, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_diction.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_diction[k]))
    return baseurl + "_".join(res)


def init_db_books():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()

    #Drop Tables
    statement = "DROP TABLE IF EXISTS 'Books';"
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Books' (
            'Id' INTEGER PRIMARY KEY,
            'book_id' INTEGER,
            'best_book_id' INTEGER,
            'work_id' INTEGER,
            'books_count' INTEGER,
            'isbn' INTEGER,
            'isbn13' INTEGER,
            'authors' TEXT,
            'original_publication_year' INTEGER,
            'original_title' TEXT,
            'title' TEXT,
            'language_code' TEXT,
            'average_rating' INTEGER,
            'ratings_count' INTEGER,
            'work_ratings_count' INTEGER,
            'work_text_reviews_count' INTEGER,
            'ratings_1' INTEGER,
            'ratings_2' INTEGER,
            'ratings_3' INTEGER,
            'ratings_4' INTEGER,
            'ratings_5' INTEGER,
            'image_url' TEXT,
            'small_image_url' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
    return None

def init_db_authors():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()


    # Drop Tables
    statement = "DROP TABLE IF EXISTS 'Authors';"
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Authors' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'Gender' TEXT,
            'Age' INTEGER,
            'Hometown' TEXT,
            'Works_count' INTEGER,
            'Followers' INTEGER,
            'About' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
    return None

def init_db_best_seller():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()


    # Drop Tables
    statement = "DROP TABLE IF EXISTS 'Best_Seller';"
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Best_Seller' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT,
            'Author' TEXT,
            'Description' TEXT,
            'List_name' TEXT,
            'Rank' INTEGER,
            'Weeks_on_list' INTEGER,
            'Url' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()
    return None


def open_json(file_name):
    json_file = open(file_name, 'r')
    file_contents = json_file.read()
    json_dict_list = json.loads(file_contents)
    json_file.close()
    return json_dict_list


def insert_best_seller(name):
    json_dict_list = open_json(name)
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()
    for search in json_dict_list.keys():
        for book in json_dict_list[search]['results']:
            # Id, Title, Author, Description, List_name, Rank, Weeks_on_list, Url
            insertion = (None,book['book_details'][0]['title'],book['book_details'][0]['author'],book['book_details'][0]['description'],book['list_name'],book['rank'],book['weeks_on_list'],book['amazon_product_url'])
            statement = 'INSERT INTO "Best_Seller"'
            statement += 'VALUES (?,?,?,?,?,?,?,?)'
            cur.execute(statement,insertion)
    conn.commit()
    conn.close()
    return None



def open_csv(name):
    ifile  = open(name, encoding='latin-1')
    read = csv.reader(ifile)
    list_of_lists = []
    for row in read:
        list_of_lists.append(row)
    return list_of_lists


def insert_stuff_book(name):
    list_of_lists = open_csv(name)
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()
    for obs in list_of_lists[1:]:
        # print(len(obs),obs)
        insertion = (obs[0],obs[1],obs[2],obs[3],obs[4],obs[5],obs[6],obs[7],obs[8],obs[9],obs[10],obs[11],obs[12],obs[13],obs[14],obs[15],obs[16],obs[17],obs[18],obs[19],obs[20],obs[21],obs[22])
        statement = 'INSERT INTO "Books"'
        statement += 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        cur.execute(statement,insertion)

    conn.commit()
    conn.close()
    return None


def gather_author_names():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()
    start = "SELECT * FROM Books"
    order_by = " ORDER BY 'ratings_count'"
    statement = start+order_by
    # print(statement)
    cur.execute(statement)
    tup_list = cur.fetchall()
    conn.commit()
    conn.close()
    author_short_list = []
    # duplicates = []

    for tup in tup_list:
        try:
            author_split = tup[7].split(',')

            if author_split[0] not in author_short_list:
                author_short_list.append(author_split[0])
            # else:
            #     duplicates.append(author_split[0])
        except:
            if tup[7] not in author_short_list:
                author_short_list.append(tup[7])
            # else:
            #     duplicates.append(tup[0])
    # dup_sort = sorted(duplicates)
    smaller_list = []
    for name in author_short_list:
        if 'ô' not in name and 'Ì' not in name and 'Ç' not in name and 'pleasefindthis' not in name:
            smaller_list.append(name)
    return smaller_list


def search_author_by_name(author_short_sorted,full_author_list):
        authorid_listoftup = []
        for author_name in author_short_sorted:
            try:
                baseurl = "https://www.goodreads.com/api/author_url/<" + author_name + ">"
                params_diction = {}
                #params_diction["id"] = author_name
                params_diction["key"] = secret_data.goodreads_key
                unique_ident = params_unique_combination(baseurl,params_diction)
                print("Making a request for new data...")
                goodreads_resp = requests.get(baseurl, params = params_diction)
                goodreads_text = goodreads_resp.text
                search_soup = BeautifulSoup(goodreads_text, "xml")
                author_id = search_soup.find("author").attrs['id']
                authorid_listoftup.append((author_name,author_id))
                rand = random.randint(1,3)
                print('sleeping for '+str(rand)+' seconds.')
                time.sleep(rand)
            except:
                print("Error occured, skipping that name.")
                continue
        return authorid_listoftup


def goodreads_author_info(authorid_listoftup,full_author_list):
        author_list_infos = []
        for tup in authorid_listoftup:
            try:
                baseurl = "https://www.goodreads.com/author/show.xml"
                params_diction = {}
                params_diction["id"] = tup[1]
                params_diction["key"] = secret_data.goodreads_key
                unique_ident = params_unique_combination(baseurl,params_diction)
                print("Making a request for new data...")
                goodreads_resp = requests.get(baseurl, params = params_diction
                # auth = auth
                )
                goodreads_text = goodreads_resp.text
                search_soup = BeautifulSoup(goodreads_text, "xml")
                book_search = search_soup.find('author')
                name = book_search.find('name').text
                gender = book_search.find('gender').text
                about = book_search.find('about').text
                born = book_search.find('born_at').text.split('/')
                try:
                    born_year = int(born[0])
                    born_month = int(born[2])
                    born_day = int(born[1])
                    age = today.year - born_year - ((today.month, today.day) < (born_month, born_day))
                except:
                    age = 0

                hometown = book_search.find('hometown').text
                works_count = int(book_search.find('works_count').text)
                followers = int(book_search.find('author_followers_count').text)
                author_list_infos.append([int(tup[1]), name, gender, age, hometown, works_count, followers, about])
                rand = random.randint(1,3)
                print('sleeping for '+str(rand)+' seconds.')
                time.sleep(rand)
            except:
                print("Error occured, skipping that entry")
                continue
        return author_list_infos



def write_to_authors_csv(author_list_infos):
    outfile_name = ('authors_full.csv')
    column_zero = 'author_id'
    column_one = 'Author'
    column_two = 'Gender'
    column_three = 'Age'
    column_four = 'Hometown'
    column_five = 'Number of Works'
    column_six = 'Number of Followers'
    column_seven = 'About'
    with open(outfile_name, 'a') as f:
        writer = csv.writer(f)
        writer.writerow((column_zero, column_one, column_two, column_three, column_four, column_five, column_six,column_seven))
        for author in author_list_infos:
                author_id = author[0]
                name = author[1]
                gender = author[2]
                age = author[3]
                hometown = author[4]
                num_publications = author[5]
                num_followers = author[6]
                about = author[7]
                writer.writerow((author_id, name, gender, age, hometown, num_publications, num_followers, about))
    print("CSV made of Goodreads Authors. Contains " + str(len(author_list_infos)) + " entries.")
    return None


def insert_author_db(name):
    list_of_lists = open_csv(name)
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()
    for obs in list_of_lists[1:]:
        insertion = (None,obs[1],obs[2],obs[3],obs[4],obs[5],obs[6],obs[7])
        statement = 'INSERT INTO "Authors"'
        statement += ' VALUES (?,?,?,?,?,?,?,?)'
        cur.execute(statement,insertion)
    conn.commit()
    conn.close()
    return None


def update_booksdb_authorid():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()


    statement = "SELECT Id, Name FROM Authors"
    cur.execute(statement)
    tup_list = cur.fetchall()

    author_dict = {}
    for tup in tup_list:
        author_dict[tup[1]] = tup[0]

    # linking authors to books tables
    for author in author_dict.keys():
        author_id = author_dict[author]
        statement = "UPDATE Books SET authors = "+str(author_id)+" WHERE authors LIKE \""+author+"%\""
        # print(statement)
        cur.execute(statement)

    # giving 'Unknown' to entries with no author
    statement = '''UPDATE Books SET authors = \"Unknown\"
    WHERE authors LIKE \"%ô%\"
    OR authors LIKE \"%Ì%\"
    OR authors LIKE \"%Ç%\"
    OR authors LIKE \"%a%\"
    OR authors LIKE \"%e%\"
    OR authors LIKE \"%i%\"
    OR authors LIKE \"%o%\"
    OR authors LIKE \"%u%\"
    '''
    # print(statement)
    cur.execute(statement)
    conn.commit()
    conn.close()
    return None

def update_bestseller_authorid():
    conn = sqlite3.connect("final_proj_db.sqlite")
    cur = conn.cursor()


    statement = "SELECT Id, Name FROM Authors"
    cur.execute(statement)
    tup_list = cur.fetchall()

    author_dict = {}
    for tup in tup_list:
        author_dict[tup[1]] = tup[0]

    # linking authors to books tables
    for author in author_dict.keys():
        author_id = author_dict[author]
        statement = "UPDATE Best_Seller SET Author = "+str(author_id)+" WHERE Author LIKE \""+author+"%\""
        # print(statement)
        cur.execute(statement)

    # giving 'Unknown' to entries with no author
    # statement = '''UPDATE Books SET authors = \"Unknown\"
    # WHERE authors LIKE \"%ô%\"
    # OR authors LIKE \"%Ì%\"
    # OR authors LIKE \"%Ç%\"
    # OR authors LIKE \"%a%\"
    # OR authors LIKE \"%e%\"
    # OR authors LIKE \"%i%\"
    # OR authors LIKE \"%o%\"
    # OR authors LIKE \"%u%\"
    # '''
    # # print(statement)
    # cur.execute(statement)
    conn.commit()
    conn.close()
    return None


###############################################################################
################### GETTING AUTHO DATA FROM GOODREADS TO CSV ##################
###############################################################################
# full_author_list = []
# author_name_list = gather_author_names() # 3888 authors
# author_ids = search_author_by_name(author_name_list,full_author_list)
# full_author_list = goodreads_author_info(author_ids,full_author_list)
# write_to_authors_csv(full_author_list)


###############################################################################
####################### INITIALIZING DATABASE AND TABLES ######################
###############################################################################
if __name__ == '__main__':
    init_db_books()
    insert_stuff_book("books.csv")
    init_db_authors()
    insert_author_db('authors_full.csv')
    init_db_best_seller()
    insert_best_seller('best_seller.json')
    update_booksdb_authorid()
    update_bestseller_authorid()








# def update_bean_ids():
#     conn = sqlite3.connect("Proj3_db.sqlite")
#     cur = conn.cursor()
#
#     statement = "SELECT Id, EnglishName FROM Countries"
#     cur.execute(statement)
#     tup_list = cur.fetchall()
#
#     country_dict = {}
#     for tup in tup_list:
#         country_dict[tup[1]] = tup[0]
#     country_dict['Unknown'] = 'Unknown'
#     for country in country_dict.keys():
#         company_id = country_dict[country]
#         cur.execute("UPDATE Bars SET CompanyLocationId = ? WHERE CompanyLocation= ?", (company_id, country))
#         cur.execute("UPDATE Bars SET BroadBeanOriginId = ? WHERE BroadBeanOrigin= ?", (company_id, country))
#     conn.commit()
#     conn.close()
#     return None


# if len(sys.argv) >1 and sys.argv[1] == '--init':
#     if sys.argv[2] == 'books':
#         print('Deleting books table and starting over from scratch.')
#         init_db_books()
#     elif sys.argv[2] == 'authors':
#         print('Deleting authors table and starting over from scratch.')
#         init_db_authors()
# elif len(sys.argv) >1 and sys.argv[1] == 'update' and sys.argv[2] == 'books':
#     print('Updating books table.')
#     insert_stuff_book('books.csv')
# elif len(sys.argv) >1 and sys.argv[1] == 'update' and sys.argv[2] == 'authors':
#     print('Updating authors table.')
#     insert_author_db('authors.csv')
# elif len(sys.argv) >1 and sys.argv[1] == 'update' and sys.argv[2] == 'ids':
#     print('Updating author ids in Books table.')
#     update_booksdb_authorid()
# else:
#     print('Leaving the database alone.')
