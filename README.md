Brief user Guide:

This program creates a database of books, authors, and best sellers and allows the user to query the database, construct a reading list, and get different visualizations of the books and lists they are looking at.

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
  Description: typing chart will create a aggregated line chart showing the quantity of books on your reading list across over time based on their publication year



The code is structured in 4 files:

'final_proj_db_prep.py' - running this file will delete the old database and create a new one.

'final_project_test.py' - this file contains unit tests checking to see that the data is being stored, accessed, and processed correctly.

'final_project_view.py' - this file contains the interactive prompt and logic determining when different functions are called and visualizations are displayed.

'final_project_model_controller.py' - this file contains the object definitions and function calls that are called in the view file.

Important functions and classes:

Book


Author




Brief description of how your code is structured, including the names of significant data processing functions (just the 2-3 most important functions--not a complete list) and class definitions. If there are large data structures (e.g., lists, dictionaries) that you create to organize your data for presentation, briefly describe them.

Data Sources:

The data sources used in constructing the database are the following:
  'books.csv' contains data on 10,000 books
  'author_full.csv' contains data on over 3,500 authors
  'best_seller.json' contains information on best seller list

The program uses a few functions that require a plotly account. To use these functions make sure your plotly account is set up and that your plotly username and plotly key are in the secrets_data.py file in your working directory. Then, uncomment the line that looks like this -		'plotly.tools.set_credentials_file(username=plotly_username, api_key=plotly_key)'		- in the 'final_project_view.py' file. When you run the view file, this will set your credentials to your plotly account allowing you to host your visualizations on your account.


The program also has one function that requires an API call to Goodreads, if you want to get descriptions for books, you will need to add that API key to your secrets_data.py file.
