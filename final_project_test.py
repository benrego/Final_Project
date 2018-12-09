'''
You must write unit tests to show that the data access, storage, and processing components of your project are working correctly. You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’. Your tests should show that you are able to access data from all of your sources, that your database is correctly constructed and can satisfy queries that are necessary for your program, and that your data processing produces the results and data structures you need for presentation.

'''

import unittest
import json
from final_project_model_controller import *


class TestDataAccessAndStorage(unittest.TestCase):
    def test_best_seller_table(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        sql = 'SELECT Title FROM Best_Seller'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('KILLING THE SS',), result_list)
        self.assertEqual(len(result_list), 40)

        sql = '''
            SELECT Title, Author, Rank
            FROM Best_Seller
            WHERE List_name="Science"
            ORDER BY Rank DESC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        # print(result_list)
        self.assertEqual(len(result_list), 10)
        self.assertEqual(result_list[2][2], 8)

        sql = '''
            SELECT COUNT(*)
            FROM Best_Seller
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 40)

        conn.close()

    def test_books_table(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        sql = '''
            SELECT average_rating
            FROM Books
            WHERE original_publication_year="1994"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((3.57,), result_list)
        self.assertEqual(len(result_list), 121)

        sql = '''
            SELECT COUNT(*)
            FROM Books
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 10000)

        conn.close()

    def test_authors_table(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        sql = 'SELECT Name, Gender FROM Authors'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('William Shakespeare', 'male'), result_list)
        self.assertEqual(result_list[1][1], 'female')

        sql = '''
            SELECT Name, Gender, Followers
            FROM Authors
            WHERE Age<80
            ORDER BY Age ASC
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 2942)
        self.assertEqual(result_list[104][1], 'male')

        sql = '''
            SELECT COUNT(*)
            FROM Authors
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 3766)

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        sql = '''
            SELECT Authors.Name
            FROM Books
            JOIN Authors ON Books.authors = Authors.Id
            WHERE Authors.Hometown="Belfast"
            AND Books.original_title="The Silver Chair"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('C.S. Lewis',), result_list)

        sql = '''
            SELECT Authors.name, Best_Seller.title, Best_Seller.Weeks_on_list, Authors.Works_count
            FROM Best_Seller
            JOIN Authors ON Best_Seller.Author = Authors.Id
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('John Grisham','THE RECKONING',5,220), result_list)

        conn.close()




class TestDataProcessing(unittest.TestCase):

    def test_book_obj(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        sql = '''
            SELECT *
            FROM Books
            JOIN Authors ON Books.authors = Authors.Id
            WHERE Title='The Hobbit'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        book_test = Book(sql = result_list[0])
        self.assertEqual(book_test.title, "The Hobbit")
        self.assertEqual(book_test.author, "J.R.R. Tolkien")
        self.assertEqual(book_test.publication_year, 1937)
        try:
            book_test.plot_ratings()
        except:
            self.fail()
        conn.close()

    def test_author_obj(self):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        sql = '''
            SELECT *
            FROM Authors
            WHERE Name='George R.R. Martin'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        author_test = Author(sql = result_list[0])
        self.assertEqual(author_test.name, "George R.R. Martin")
        self.assertEqual(author_test.gender, "male")
        self.assertEqual(author_test.followers, 83936)

        conn.close()


    def test_line_plot(self):
        try:
            plot_reading_line()
        except:
            self.fail()

    def test_pie_plot(self):
        try:
            plot_reading_list()
        except:
            self.fail()



unittest.main(verbosity=2)
