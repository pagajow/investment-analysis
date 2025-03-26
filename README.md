# Investment Analysis Web App

This is a Django-based web application designed to assist individual investors in the analysis and evaluation of publicly traded companies. The tool simplifies collecting, storing, visualizing, and interpreting financial data, offering both manual tools and AI-powered insights to streamline the research process.

---

## ✨ What Does It Do?

This app supports investors by:

- Storing key financial data from annual reports
- Adding personalized notes for each asset
- Automatically calculating useful financial ratios
- Creating interactive charts and tables
- Defining custom filters and criteria to evaluate a company's fundamentals
- Estimating a company's intrinsic value using a DCF calculator
- Generating AI-assisted summaries and research reports using GPT-4o Mini and external data from the web (with API keys provided by the user)

All data is linked to individual user accounts. Users can set favorites, filter assets, and organize their research in a structured way. The AI assistant can process text, PDFs, and respond to questions, storing generated reports alongside other insights.

---

## 🧱 Tech Stack

- **Backend:** Django, Python 3.12
- **Frontend:** Static HTML templates (via Django), JavaScript (bundled using Webpack via Node.js)
- **Database:** SQLite (for development)
- **AI Integration:** OpenAI API (GPT-4o Mini), Google Search API

Main Python libraries:

- `pandas`, `numpy`, `scikit-learn`, `statsmodels` (financial calculations)
- `beautifulsoup4`, `requests`, `newspaper3k` (data extraction)
- `langchain`, `langgraph`, `PyPDF2`, `openai`, `google-api-python-client`, `markdown`, `bleach`

Static frontend assets are compiled with Node.js and Webpack and served via Django's static file system.

---

## 🔧 Installation (Local Dev)

```bash
# Clone the repo
$ git clone https://github.com/pagajow/investment-analysis.git
$ cd investment-analysis

# Create virtual environment
$ python3 -m venv venv
$ source venv/bin/activate

# Install backend dependencies
$ pip install -r requirements.txt

# Install frontend dependencies
$ npm install
$ npm run build

# Collect static files for Django
$ python manage.py collectstatic

# Apply migrations and run server
$ python manage.py migrate
$ python manage.py runserver
```

> If running on a server with low RAM, consider building the frontend locally and copying the `static/dist` folder manually.

---

## 🔧 Main Features Overview

- Secure user registration, login, email verification
- CRUD operations for companies, financial data, notes, and AI reports
- Upload financial data via CSV and process it with Pandas
- Custom filters using user-defined rules to evaluate financial strength
- Visual presentation of metrics and summaries
- AI agent powered by GPT-4o Mini and LangChain/LangGraph framework

---

## 🌎 Deployment Notes

Deployment relies on:
- A Gunicorn service running the Django app
- Nginx as a reverse proxy
- GitHub webhook integration via custom Python service
- Auto-deployment script (`deploy.sh`) which pulls changes, installs dependencies, builds frontend (optional), collects static files, and restarts services


---

## ⚠️ Disclaimer

> This tool is meant to support personal research and analysis. It is **not** financial advice. The software may contain bugs or omissions. Users are fully responsible for verifying information and making investment decisions.

---

## 🌟 Author & Contact

Made with passion for finance and code by **Patryk Gajowniczek**.

- YouTube: [@deepandbetter](https://www.youtube.com/@deepandbetter)
- Email: [deepandbetter@gmail.com](mailto:deepandbetter@gmail.com)

Suggestions, feedback, or contributions are always welcome!

---

## 🔐 License

MIT License (To be added)

---

