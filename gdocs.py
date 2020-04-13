import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('JSON file here', scope) # Get your signed credentials JSON file by following these instructions: https://gspread.readthedocs.io/en/latest/oauth2.html
client = gspread.authorize(creds)

# Tweets
sheet_tweets = client.open('Evergreen tweets').worksheet('Tweets') # If you change the name of the Google Sheet, then make sure you update it here.

# Log
sheet_log = client.open('Evergreen tweets').worksheet('Log') # If you change the name of the Google Sheet, then make sure you update it here.

