from flask import Flask, request, render_template, redirect, url_for, session
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2 import id_token
from flask_session import Session
from datetime import datetime
from newspaper import Article
from bs4 import BeautifulSoup
from unidecode import unidecode
import requests
import psycopg2
import google
import json
import nltk
import math
import re
import os
nltk.download('all')


app = Flask(__name__)

app.secret_key = 'hello'


# Establish connection to the PostgreSQL database
connection = psycopg2.connect(
    user="satyam",
    password="rXi4WDQKlyUiN2pTFNBdiCDtkeZYo4pD",
    host="dpg-cnmr0li1hbls739i3800-a",
    database="dhp2024_zevw"
)

# Create a cursor object to execute PostgreSQL commands
cursor = connection.cursor()

# Function to create the table in PostgreSQL
def create_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS news_analysis (
        id SERIAL PRIMARY KEY,
        url TEXT,
        cleaned_text TEXT,
        sentence_count INT,
        word_count INT,
        link_count INT,
        upos_frequency JSONB,
        headlines TEXT,
        keywords TEXT,
        tone_sentiment TEXT,
        genre TEXT,
        news_agency TEXT,
        publish_date TEXT,
        reading_time TEXT,
        date_time_read TIMESTAMP
    );
    '''
    cursor.execute(create_table_query)
    connection.commit()

# Path to the client secrets file
client_secrets_file = "authentication.json"

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
scopes = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']

# Redirect URI for the OAuth flow
redirect_uri = 'https://sat-news-analyser.onrender.com/callback'

# Create the OAuth flow object
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)

@app.route('/login')
def login():
    if 'google_token' in session:
        # User is already authenticated, redirect to a protected route
        return redirect(url_for('protected'))
    else:
        # User is not authenticated, redirect to Google OAuth flow
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)

#

@app.route('/callback')
def callback():
    # Get the parameters from the request URL
    state = request.args.get('state')
    prompt = request.args.get('prompt')
    client_id = request.args.get('client_id')
    scope = request.args.get('scope')

    # Handle the callback from the Google OAuth flow
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token

    # Redirect to the protected route or another page
    return redirect(url_for('protected'))

@app.route('/protected')
def protected():
    if 'google_token' in session:
        # User is authenticated, retrieve user information
        session_credentials = flow.credentials
        session['google_token'] = session_credentials.token
        session['google_refresh_token'] = session_credentials.refresh_token
        session['google_client_id'] = session_credentials.client_id
        session['google_client_secret'] = session_credentials.client_secret
        session['google_scopes'] = session_credentials.scopes

        # Extract user profile information
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {session["google_token"]}'}
        userinfo_response = requests.get(userinfo_endpoint, headers=headers)
        userinfo_data = userinfo_response.json()
        global email
        email = userinfo_data.get('email')

        
        # Print access token and its expiration time
        print('Access Token:', session['google_token'])
        print('Token Expiry:', session_credentials.expiry)
        if email in ["satyampandeysatyam1411@gmail.com", "kushal@sitare.org", "su-23038@sitare.org", "satyamjnvian@gmail.com","shivampandeyvg@gmail.com"]:
            return redirect(url_for("history"))
        else:
            return redirect(url_for('portal'))

    else:
        # User is not authenticated, redirect to the homepage
        return redirect(url_for('portal'))

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('portal'))

# Function to insert data into the PostgreSQL table only if cleaned_text is non-empty
def insert_data(url, cleaned_text, sentence_count, word_count, link_count, upos_frequency,
                headlines, keywords, tone_sentiment, genre, news_agency, publish_date,
                reading_time, date_time_read):
        insert_query = '''
        INSERT INTO news_analysis (url, cleaned_text, sentence_count, word_count, link_count,
                                    upos_frequency, headlines, keywords, tone_sentiment, genre,
                                    news_agency, publish_date, reading_time, date_time_read)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        record_to_insert = (url, cleaned_text, sentence_count, word_count, link_count, json.dumps(upos_frequency),
                            headlines, keywords, tone_sentiment, genre, news_agency, publish_date,
                            reading_time, date_time_read)
        cursor.execute(insert_query, record_to_insert)
        connection.commit()
# Call the create_table function to ensure the table exists before inserting data
create_table()

def clean_text(text):
    text = unidecode(text)  # Convert Unicode to ASCII
    text = re.sub(r'(?<=[^\s\'"\(\[<{])\s*([.,!?;:])\s*', r'\1 ', text)  # Insert space after punctuation
    text = re.sub(r'<!--\s*-->', ' ', text)  # Handle text separated by comment tags
    text = re.sub(r'&#[0-9]+;', '', text)  # Remove ASCII codes
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.strip()

def extract_and_clean_text(url):
    cleaned_text = ''
    sentence_count = 0
    word_count = 0
    link_count = 0
    upos_frequency = {}
    headlines = ""
    keywords = ""
    tone_sentiment = ""
    genre = ""
    news_agency = ""
    publish_date = ""
    reading_time = ""
    date_time_read = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetching HTML content of the URL
    response = requests.get(url)

    # Parsing HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class="_s30J clearfix"
    elements = soup.find_all(class_="_s30J clearfix")

    # Extracting text from elements
    for element in elements:
        # Extract text
        text = ''.join([e for e in element.recursiveChildGenerator() if isinstance(e, str)])
        
        # Clean the text
        text = clean_text(text)
        
        cleaned_text += text.strip() + '\n'

    # Counting sentences and words
    sentence_count = len(nltk.sent_tokenize(cleaned_text))

    # Define a regular expression pattern to match words (excluding punctuation)
    pattern = r'\b\w+\b'

    # Tokenize the text using the regular expression pattern
    word_list = re.findall(pattern, cleaned_text)

    # Count the number of words
    word_count = len(word_list)

    # Counting UPOS frequencies
    upos_tag_list = nltk.pos_tag(word_list, tagset='universal')
    for _, pos in upos_tag_list:
        if pos not in [",", ".", "?", "!"]:
            upos_frequency[pos] = upos_frequency.get(pos, 0) + 1

    # Extract metadata using newspaper library
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    keywords = article.keywords
    title = article.title
    
    # Extract genre of news
    description = article.meta_data.get('og', {}).get('description', '')
    match = re.search(r'^(.*?):', description)
    genre = match.group(1).strip() if match else ""

    # Extract news agency
    news_agency = article.meta_data.get('og', {}).get('site_name', "")

    # Extract publish date
    scripts = soup.find_all('script')
    for script in scripts:
        script_text = script.get_text()
        if '"datePublished"' in script_text:
            try:
                script_json = json.loads(script_text)
                if 'datePublished' in script_json:
                    publish_date = script_json['datePublished']
                    break
            except json.JSONDecodeError:
                pass

    # Counting the number of links (excluding redirected links)
    for link in soup.find_all('a', href=True):
        if not link['href'].startswith('#') and not link['href'].startswith('http://redirect.website.com'):
            link_count += 1

    # Find the element with class "HNMDR"
    heading_element = soup.find(class_="HNMDR")
    # Extract heading text if found
    if heading_element:
        headlines = clean_text(heading_element.text)
    else:
        headlines = "Headline not found"

    # Initialize VADER sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Analyze sentiment using VADER
    sentiment_scores = sid.polarity_scores(cleaned_text)
    compound_score = sentiment_scores["compound"]
    positive_score = sentiment_scores["pos"]
    negative_score = sentiment_scores["neg"]

    # Classify sentiment based on compound score and predefined thresholds
    if compound_score > 0.1:
        tone_sentiment = "Positive"
    elif compound_score < -0.1:
        tone_sentiment = "Negative"
    else:
        tone_sentiment = "Neutral"

    # Calculate reading time
    reading_time_seconds = (word_count / 200) * 60  # Assuming an average reading speed of 200 words per minute
    reading_time_minutes = math.floor(reading_time_seconds / 60)
    reading_time_seconds_remainder = math.floor((reading_time_seconds % 60) / 30) * 30
    reading_time = f"{reading_time_minutes} minute {reading_time_seconds_remainder} second"

    # Insert data into the PostgreSQL table
    insert_data(url, cleaned_text, sentence_count, word_count, link_count, upos_frequency,
                headlines, ", ".join(keywords), tone_sentiment,
                genre, news_agency, publish_date, reading_time, date_time_read)

    return cleaned_text, sentence_count, word_count, link_count, upos_frequency, \
           headlines, ", ".join(keywords), tone_sentiment, \
           genre, news_agency, publish_date, reading_time, date_time_read

@app.route("/", methods=('POST','GET'))
def portal():
    url = ""
    cleaned_text = ""
    sentence_count = 0
    word_count = 0
    link_count = 0
    upos_frequency = {}
    headlines = ""
    keywords = ""
    tone_sentiment = ""
    genre = ""
    news_agency = ""
    publish_date = ""
    reading_time = ""
    date_time_read = ""

    if request.method == "POST":
        url = request.form["url"]
        cleaned_text, sentence_count, word_count, link_count, upos_frequency, \
        headlines, keywords, tone_sentiment, genre, news_agency, publish_date, reading_time, date_time_read = extract_and_clean_text(url)

    return render_template('index.html')

@app.route("/extract_text", methods=['POST'])
def extract_text():
    url = request.form['url']
    cleaned_text, sentence_count, word_count, link_count, upos_frequency, \
    headlines, keywords, tone_sentiment, genre, news_agency, publish_date, reading_time, date_time_read = extract_and_clean_text(url)
    


    return render_template('content.html', url=url, cleaned_text=cleaned_text,
                        sentence_count=sentence_count, word_count=word_count,
                        link_count=link_count, upos_frequency=upos_frequency,
                        headlines=headlines, keywords=keywords, tone_sentiment=tone_sentiment,
                        genre=genre, news_agency=news_agency, publish_date=publish_date,
                        reading_time=reading_time, date_time_read=date_time_read)

@app.route("/table", methods=['GET'])
def table_view():
    # Fetch data from the PostgreSQL table
    cursor.execute("SELECT * FROM news_analysis ORDER BY id DESC LIMIT 1")
    data = cursor.fetchone()  # Assuming you have only one row for now

    # Extracting data from the fetched row
    url = data[1]
    cleaned_text =data[2]
    sentence_count = data[3]
    word_count = data[4]
    link_count = data[5]
    upos_frequency = data[6]
    headlines = data[7]
    keywords = data[8]
    tone_sentiment = data[9]
    genre = data[10]
    news_agency = data[11]
    publish_date = data[12]
    reading_time = data[13]
    date_time_read = data[14]

    return render_template("analysis.html", 
                           url=url,
                           cleaned_text = cleaned_text,
                           sentence_count=sentence_count, 
                           word_count=word_count,
                           link_count=link_count, 
                           upos_frequency=upos_frequency,
                           headlines=headlines, 
                           keywords=keywords, 
                           tone_sentiment=tone_sentiment,
                           genre=genre, 
                           news_agency=news_agency, 
                           publish_date=publish_date,
                           reading_time=reading_time, 
                           date_time_read=date_time_read)

@app.route("/history")
def history():
    # Fetch URL, sentence count, word count, and stop word count from the news_analysis table
    cursor.execute("SELECT url, date_time_read, news_agency, publish_date FROM news_analysis ORDER BY id DESC")
    records = cursor.fetchall()

    return render_template("history.html", records=records)

@app.route("/developer")
def developer():
    return render_template("developer.html")


@app.route("/details")
def view_details():
    url = request.args.get('url')
    date_time_read = request.args.get('date_time_read')
    
    # Fetch all details for the provided URL and date_time_read
    cursor.execute("SELECT * FROM news_analysis WHERE url = %s AND date_time_read = %s", (url, date_time_read,))
    details = cursor.fetchone()

    return render_template("details.html", details=details)




if __name__ == "__main__":
    app.run(debug=True)
