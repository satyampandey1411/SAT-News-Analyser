# SAT News Analyser 🗞️📊

## Project Overview
SAT News Analyser is a sophisticated web application that provides in-depth analysis of news articles by extracting and processing content from various online sources.

## Features 🌟
- URL-based news article extraction
- Automatic text cleaning and formatting
- Comprehensive metadata analysis:
  - Sentence and word count
  - Link count
  - Part of Speech (POS) tag frequency
  - Sentiment analysis
  - News genre detection
  - Reading time estimation
- Support for multiple news websites
- User authentication via Google OAuth
- Article history tracking
- Text-to-speech functionality

## Technologies Used 💻
- Backend: Flask (Python)
- Database: PostgreSQL
- Authentication: Google OAuth
- Libraries: 
  - NLTK
  - TextBlob
  - Newspaper3k
  - BeautifulSoup
  - psycopg2

## Prerequisites 🔧
- Python 3.8+
- PostgreSQL
- Google Cloud Project (for OAuth)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/satyampandey1411/SAT-News-Analyser.git
cd SAT-News-Analyser
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv      # On Windows, use python -m venv venv 
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
- Create a PostgreSQL database
- Update database credentials in `app.py`

### 5. Google OAuth Configuration
- Create a project in Google Cloud Console
- Generate OAuth 2.0 credentials
- Download `authentication.json`

### 6. Run the Application
```bash
python3 app.py          # On Windows, use python -m venv venv 
```

## Usage 🚀
1. Navigate to the homepage
2. Paste a news article URL
3. Click search/analyze
4. View detailed article analysis

## Screenshots 📸
### Main Interface
![Main Interface](/screenshots/main_interface.png)

### Article Analysis
![Article Analysis](/screenshots/article_analysis.png)

### History Page
![History Page](/screenshots/history_page.png)

## Authentication 🔐
- Login with Google
- Restricted access for specific email domains

## Supported News Sources
- DD News
- Times Now
- India Times
- The Hindu
- BBC
- CNBC
- Times of India
- Indian Express
- And many more!

## Acknowledgements🙏 
-Newspaper3k for seamless news extraction and content parsing
-NLTK and TextBlob for robust natural language processing and sentiment analysis
-Google OAuth for secure and reliable user authentication
-BeautifulSoup for efficient web scraping
-PostgreSQL for scalable and powerful database management
-Open-source communities and developers for their contributions

## Contributing 🤝
1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License 📄
This project is open-source. Please check the LICENSE file for details.
## Contact 📧
- [LinkedIn](https://www.linkedin.com/in/satyam1411pandey/)
- [GitHub](https://github.com/satyampandey1411)
