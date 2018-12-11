import sqlite3
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
import final_project_model_controller as functions

############ UNCOMMENT THIS LIKE TO SET YOUR CREDENTIALS IN PLOTLY ############
#plotly.tools.set_credentials_file(username=plotly_username, api_key=plotly_key)


def start_game():
    user_input = ''
    while user_input != 'exit':
        user_input = input("\nInput Command:\n\t'books' for books database\n\t'authors' to search for an author\n\t'best_seller' to look at best seller list\n\t'reading_list' to view your reading list\n\t'help <COMMAND>' or 'help book_obj' to get search instructions\n\t'exit' to exit the program: ").lower()
        if user_input.split()[0] == 'help':
            if user_input.split()[1] == 'books':
                help_books = functions.load_help_text('help_books.txt')
                print(help_books)
                continue
            elif user_input.split()[1] == 'authors':
                help_authors = functions.load_help_text('help_authors.txt')
                print(help_authors)
                continue
            elif user_input.split()[1] == 'best_seller':
                help_bs = functions.load_help_text('help_bs.txt')
                print(help_bs)
                continue
            elif user_input.split()[1] == 'reading_list':
                help_rl = functions.load_help_text('help_rl.txt')
                print(help_rl)
                continue
            elif user_input.split()[1] == 'book_obj':
                help_book_obj = functions.load_help_text('help_book_obj.txt')
                print(help_book_obj)
                continue
            else:
                print("Help command not recognized.")
        elif user_input == 'books':
            book_search = input("Search for a book by name: ").split()
            #(book='', author='',sort='avg_rating',top='10')
            search_param = ''
            sort_param = 'avg_rating'
            num_param = '10'
            for item in book_search:
                if item == 'avg_rating':
                    sort_param = item
                elif item == 'ratings_count':
                    sort_param = item
                elif item == 'review_count':
                    sort_param = item
                elif len(item) <=2:
                    num_param = item
                else:
                    search_param = item
            book_tuple_response = functions.search_book_database(book = search_param, sort = sort_param, top = num_param)
            if len(book_tuple_response) == 0:
                print("\nNo books match that search.\n")
            book_flag = ''
            while book_flag != 'next':
                book_input = input("pick up a book: ")
                try:
                    book_sql = book_tuple_response[int(book_input)-1]
                    book_obj = functions.Book(sql = book_sql)
                    print(book_obj)
                    book_flag = 'next'
                except:
                    print('\nNot a valid command.\n')
            second_book_input = ''
            while second_book_input != 'back':
                second_book_input = input("plot, description, add ('back' to return to original menu): ")
                if second_book_input == 'plot':
                    book_obj.plot_ratings()
                elif second_book_input == 'description':
                    book_d = functions.get_book_description(book_obj.title,book_obj.author)
                    print("\nDescription for ",book_d[0])
                    print(book_d[1])
                    print('\n')
                elif second_book_input == 'add':
                    book_obj.add_to_list()
                # elif second_book_input == 'remove':
                #     functions.remove_from_list(int(book_obj))
                elif second_book_input == 'back':
                    continue
                else:
                    print('\nNot a valid command.\n')
            user_input = ''
        elif user_input == 'authors':
            books_or_info = ''
            while books_or_info != 'back':
                author_search = input("\nSearch for an author by name ('back' to return to original menu) : ")
                if author_search == 'back':
                    break
                author_tuples = functions.author_db_search(author_search)
                if len(author_tuples) == 0:
                    print('\nNo authors matched that search.\n')
                else:
                    author_select = input("Select an Author ('back' to return to original menu) : ")
                    if author_select == 'back':
                        break
                    books_or_info = input("Would you like info about the author ('info') or about books ('books') they have written? ('back' to return to original menu) : ")
                    #(book='', author='',sort='avg_rating',top='10')
                    if books_or_info == 'info':
                        author_sql = author_tuples[int(author_select)-1]
                        author_obj = functions.Author(sql = author_sql)
                        print(author_obj)
                        more_info = input("Would you like more info ('yes') about "+author_obj.name+"? ('no' or 'back' to return to original menu): ")
                        if more_info == 'back' or more_info == 'no':
                            break
                        if 'y' in more_info.lower():
                            print(author_obj.about)
                            books_or_info = 'back'
                            user_input = ''
                        else:
                            print('\nNot a valid command.\n')
                    elif books_or_info.split()[0] == 'books':
                        search_param = author_tuples[int(author_select)-1][1]
                        book_split = books_or_info.split()
                        sort_param = 'avg_rating'
                        num_param = '10'
                        acc = 0
                        for item in book_split:
                            if item == 'avg_rating':
                                sort_param = item
                            elif item == 'ratings_count':
                                sort_param = item
                            elif item == 'review_count':
                                sort_param = item
                            elif len(item) <=2:
                                num_param = item
                            # elif acc >0:
                            #     search_param += ' '
                            #     search_param += item
                            # else:
                            #     acc+=1
                            #     search_param += item
                        #print(search_param)
                        author_tuple_response = functions.search_book_database(author = search_param, sort = sort_param, top = num_param)
                        if len(author_tuple_response) == 0:
                            print('No search results for that author\'s name.')
                            user_input = ''
                        else:
                            book_input = input("pick up a book: ")
                            try:
                                book_sql = author_tuple_response[int(book_input)-1]
                                book_obj = functions.Book(sql = book_sql)
                                print(book_obj)
                                second_book_input = ''
                                while second_book_input != 'back':
                                    second_book_input = input("plot, description, add, remove ('back' to original menu): ")
                                    if second_book_input == 'plot':
                                        book_obj.plot_ratings()
                                    elif second_book_input == 'description':
                                        book_d = functions.get_book_description(book_obj.title,book_obj.author)
                                        print("Description for ",book_d[0])
                                        print(book_d[1])
                                    elif second_book_input == 'add':
                                        book_obj.add_to_list()
                                    elif second_book_input == 'remove':
                                        functions.remove_from_list(int(book_obj))
                                books_or_info = 'back'
                                user_input = ''
                            except:
                                print('\nNot a valid input.')
                                break
                    else:
                        print('\nNot a valid command. Search for author again.\n')
        elif user_input == 'best_seller':
            bs_flag = ''
            while bs_flag != 'start':
                bs_input = input("What list would you like to see? (fiction, non-fiction, science) ('back' to return to original menu):")
                bs_list = functions.best_seller_db_search(bs_input)
                if len(bs_list) == 35:
                    print("\nNo list of that name.")
                    break
                bs_book_input = input("pick up a book (#) ('back' to return to original menu): ")
                if bs_book_input == 'back':
                    user_input = ''
                else:
                    book_dict_form = bs_list[int(bs_book_input)-1]
                    book_obj = functions.Book(bs = book_dict_form)
                    print(book_obj)
                    second_book_input = ''
                    while second_book_input != 'back':
                        second_book_input = input("plot, description, add ('back' to return to search options): ")
                        if second_book_input == 'plot':
                            print("No plot available for this book.")
                        elif second_book_input == 'description':
                            print("Description for ",book_obj.title)
                            print(book_obj.description)
                        elif second_book_input == 'add':
                            book_obj.add_to_list()
                        # elif second_book_input == 'remove':
                        #     print(READING_LIST)
                        #     functions.remove_from_list(int(bs_book_input))
                user_input = ''
        elif user_input == 'reading_list':
            book_input = ''
            while book_input != 'back':
                reading_list = functions.show_reading_list()
                book_input = input("pick up a book(#), pie chart of ratings('pie'), or line chart of publication years ('line') ('back' to return to original menu): ")
                if book_input == 'back':
                    user_input = ''
                elif book_input == 'pie':
                    functions.plot_reading_list()
                elif book_input == 'line':
                    functions.plot_reading_line()
                elif int(book_input) in range(1,len(functions.READING_LIST)+1):
                    book_dict_form = reading_list[int(book_input)-1]
                    if book_dict_form['bs'] == None:
                        book_obj = functions.Book(json = book_dict_form, bs = None)
                    else:
                        book_obj = functions.Book(json = book_dict_form, bs = book_dict_form['bs'])
                    print('\n',book_obj)
                    second_book_input = ''
                    while second_book_input != 'list':
                        second_book_input = input("plot, description, add, remove, ('back' to previous menu): ")
                        if second_book_input == 'back':
                            break
                        elif second_book_input == 'plot':
                            if book_obj.bs == None:
                                book_obj.plot_ratings()
                            else:
                                print("No ratings to plot for this book.")
                        elif second_book_input == 'description':
                            book_d = functions.get_book_description(book_obj.title,book_obj.author)
                            print("Description for ",book_d[0])
                            print(book_d[1])
                            second_book_input = 'list'
                        elif second_book_input == 'add':
                            book_obj.add_to_list()
                        elif second_book_input == 'remove':
                            functions.remove_from_list(int(book_input))
                else:
                    print("\nThat is not a valid entry.\n")
            user_input = ''
        elif user_input == 'exit':
            print('exiting...')
        else:
            print("\nThat was not a recognized command.\n")


start_game()


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
