# DQS_software
READ THIS BEFORE STARTING WORK
IMPORTANT:

- Basic FLASK layout has been made for you.
- A Branch has been created for each seperate main requirement.
- Commits should only ever be pushed to that Branch.
- Merges will only be made once they have been tested and found to pass ALL tests.
- Tests will be at the start of EVERY function.
- If help is needed, ask.

GIT COMMANDS:
- git help
- git status
- git add FILENAME
- git pull
- git push
- git commit -m "HELPFUL AND DESCRIPTIVE COMMENT"
- git switch BRANCH

Venv Setup (Windows)
- Pull from git, this will give the requirements.txt
- Make sure you have Python3
- Open CMD in the git directory
- Write the following command: python3 -m venv venv
- Write the following command: .\venv\Scripts\activate.bat
- Write the following command: python3 -m pip install -r requirements.txt
- Write the following command: set FLASK_APP=run

MySQL Access (Web Development - Week 3, Databases and mySQL)
- Username: c1945047
- Password: Team18MySQL
- Database Name: c1945047_Team18

- Login to MySQL using: "mysql -u c1945047 -h csmysql.cs.cf.ac.uk -p" and enter the password when prompted
- Access the database with "use c1945047_Team18;"
- If you need to access the content inside of the database:
	- "show tables;"
	- "select * from (name of table);"

To run the flask application to test
- Write the following command: flask run
