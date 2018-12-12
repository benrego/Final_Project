Brief user Guide:

This program creates a database of books, authors, and best sellers and allows the user to query the database, construct a reading list, and get different visualizations of the books and lists they are looking at.

The 'reading_list.json' cache and the 'final_proj_db.sqlite' are NOT required to be in the working directory to run the file. However, the reading list is helpful to have in the working directory when running the test file, as it will open the visualizations in plotly related to the reading list. Otherwise, the graph in plotly will be blank.

To create a new version of the database, run the 'final_proj_db_prep.py' file.
To start the interactive prompt, run the 'final_project_view.py' file.


When running the code, you will see the following prompt. Below, you will see explanations for how to navigate through each of the command menus.

Input Command:
        'books' for books database
        'authors' to search for an author
        'best_seller' to look at best seller list
        'reading_list' to view your reading list
        'help <COMMAND>' or 'help book_obj' to get search instructions
        'exit' to exit the program:


books
	Description: Lists books that match the specified parameters. Will return a
	list showing book title, author, and the sorting parameter specified.

	Options:
		  search parameter
		Description: Input a string that you want to match in the database with
		books which contain that string in the book title.

		  avg_rating|ratings_count|review_count [default: avg_rating]
		Description: Specifies whether to sort by average rating, number of
		ratings, or number of reviews.

		  <limit> [default: 10]
		Description: Specifies the number of records you want to be visible from
		that search. Will always sort in descending order.



authors
	Description: Allows you to search for info about the author or info about
	books the author has written.

	Second prompt: "Would you like info about the author ('info') or about
	books ('books') they have written?"

		info
			Description: Lists information about the author.

		books
			Description: Lists books that match the specified parameters. Will return
			a list showing book title, author, and the sorting parameter specified.

			Options:
				  search parameter
				Description: Input a string that you want to match in the database with
				authors who have that string in their name.

				    avg_rating|ratings_count|review_count [default: avg_rating]
				Description: Specifies whether to sort by average rating, number of
				ratings, or number of reviews.

				    <limit> [default: 10]
				Description: Specifies the number of records you want to be visible
				from that search. Will always sort in descending order.



best_seller

	Description: Search different New York Times best seller lists for books.

	First Prompt: ('What list would you like to see? (fiction, non-fiction, science):')

		fiction: shows fiction best seller list

		non-fiction: shows non-fiction best seller list

		science: shows science best seller list



reading_list
	Description: Lists the books on your reading list. Will return a list showing
	book title, author, and average rating.

	Second Prompt: pick up a book(#), pie chart of ratings('pie'), or line chart of publication years ('line') ('back' to return to original menu):

	#
	Description: selecting a book number from the above list returns that book
	as an object with the options available under book_object above.

	pie
	Description: typing chart will create a pie chart showing the percentage of
	books on your reading list across different average ratings (rounded to the
	tens decimal place)

	line
  Description: typing chart will create a aggregated line chart showing the
	quantity of books on your reading list across over time based on their
	publication year




The code is structured in 4 files:

'final_proj_db_prep.py' - running this file will delete the old database and create a new one.

'final_project_test.py' - this file contains unit tests checking to see that the data is being stored, accessed, and processed correctly.

'final_project_view.py' - this file contains the interactive prompt and logic determining when different functions are called and visualizations are displayed.

'final_project_model_controller.py' - this file contains the object definitions and function calls that are called in the view file.

Important functions and classes:

Class Book():
One of the two classes in this program is the Book class, which represents an individual book with a title, author, published year, average rating, ratings distribution, etc. Each book object has a few noteworthy methods:

plot_ratings will plot a histogram of the distribution of ratings given to the book (1-5)

add_to_list will add the book object to a cached reading list that can then be accessed through the reading_list command in the interactive prompt.

the string method changes depending on if the book came from the Books table or from the Best Seller table.

Class Author():
The other class in the program is the Author class, which represents an author that was present in one of the books from the books.csv. These instances contain information about the author like their name, gender, age, howntown, the number of works attributed to them, their number of followers, and a description about them.

Function search_book_database():
'''
database search for books
Params: book search term, author search term, sort type, number or results
Return: list of tuples with title, author, and average rating
'''
The search book database function will search the book table for information about books. Detailed above, it can take three kinds of parameters, a search parameter, a sorting parameters, and a limit parameter. If a sorting parameter or limit parameter are not specified, the program will use defaults. The list of tuples returned from the database will given numbers and printed out in a numbered list for the viewer to see. The numbers given to each book will correspond to their index in the list minus one, so that when, in the interactive prompt, the user inputs a number, the program will be able to retrieve the correct entry. The function returns a list of tuples.


Function show_reading_list():
'''
displays your reading list (Num, Title, Author, Avg Rating)
params: none
return: list of dictionaries for the books that had been stored in json, would need to be reconstructed into objects if you want to use objects again
'''
This function takes no inputs, it just prints an organized list of the books on your reading list (stored in a cache). It returns a list of dictionaries (each dictionary corresponding to a book), which can be reconstructed into book objects when they are specified by the interactive prompt.


Function plot_reading_list():
'''
plots a pie chart of ratings on reading list
params: none
return: pie chart
'''
This function takes no inputs and creates a visualization in plotly that will organize the books on your reading list into segments of a pie chart corresponding to the rounded value of their average rating.


Data Sources:

The data sources used in constructing the database are the following:
  'books.csv' contains data on 10,000 books
  'author_full.csv' contains data on over 3,500 authors
  'best_seller.json' contains information on best seller list

The program uses a few functions that require a plotly account. To use these functions make sure your plotly account is set up and that your plotly username and plotly key are in the secrets_data.py file in your working directory. Then, uncomment the line that looks like this -		'plotly.tools.set_credentials_file(username=plotly_username, api_key=plotly_key)'		- in the 'final_project_view.py' file. When you run the view file, this will set your credentials to your plotly account allowing you to host your visualizations on your account.


The program also has one function that requires an API call to Goodreads, if you want to get descriptions for books, you will need to add that API key to your secrets_data.py file.
