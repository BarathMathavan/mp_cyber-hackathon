# 🛡️ Project Argus: Hostile Narrative Detector

**A real-time intelligence dashboard for detecting, analyzing, and visualizing hostile digital campaigns on social media. Developed for the CIIS Summit Hackathon.**

---

### Live Demo & Screenshots

**[➡️ View the Live Demo Here](https://your-app-name.streamlit.app)**  

---

### The Problem

In the modern digital age, information warfare is a significant threat to national security and social cohesion. Hostile actors, both foreign and domestic, leverage social media platforms to launch coordinated campaigns aimed at spreading disinformation, inciting hatred, and destabilizing society. These campaigns are often fast-moving and difficult to detect before they cause significant harm.

### Our Solution: Project Argus

Project Argus is an early warning system designed to provide actionable intelligence to security agencies and researchers. Our platform automatically monitors public conversations, identifies potentially hostile narratives using AI, and visualizes the key actors and networks driving these campaigns.

This allows analysts to move from a reactive to a **proactive** stance, enabling them to understand and counter threats as they emerge.

---

### ✨ Key Features

*   **Real-Time Vitals:** A high-level dashboard with KPIs like hostility ratio, tweet velocity, and bot-like activity detection to provide an instant snapshot of the information environment.
*   **Intelligent Threat Feed:** Uses a weighted engagement score to automatically rank and display the most viral and impactful hostile tweets, allowing analysts to see the exact messaging being used.
*   **Advanced Analytics:** Interactive charts visualize sentiment distribution, top hostile narratives, and the most active accounts spreading negative content.
*   **Interactive Network Analysis:** A dynamic graph visualization (using Pyvis and NetworkX) maps the mention networks, allowing for the instant identification of key influencers and potential echo chambers.
*   **Campaign Forensics:** A deep dive tool that allows analysts to investigate specific authors and uncover the co-occurrence of hostile hashtags, revealing the underlying structure of a coordinated campaign.

---

### 🛠️ Tech Stack

*   **Backend & Data Analysis:** Python
*   **Web Framework / Dashboard:** Streamlit
*   **Data Manipulation:** Pandas
*   **API Interaction:** Tweepy (for the Twitter/X API v2)
*   **Natural Language Processing (NLP):** TextBlob
*   **Graph Analysis:** NetworkX, Pyvis, `python-louvain` for community detection
*   **Data Visualization:** Plotly Express
*   **Deployment:** Streamlit Community Cloud

---

### 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/mp_cyber-hackathon.git
    cd mp_cyber-hackathon
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\Activate.ps1
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your credentials:**
    *   Create a file named `.env` in the root directory.
    *   Add your Twitter API Bearer Token to it: `TWITTER_BEARER_TOKEN="YOUR_TOKEN_HERE"`

5.  **Run the data pipeline (optional, sample data is included):**
    To fetch fresh data, run the collector and analyzer:
    ```bash
    python -m modules.twitter_collector
    python -m modules.analysis
    ```

6.  **Launch the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

---

### 👥 Team Members

*   **BARATH MATHAVAN M** - Team Lead
*   **SIVARAMA KRISHNAN M** - Data Engineer
*   **BACKIA LAKSHMI B** - Data Scientist
*   **AFSEEN MANHA M** ML Engineer
*   **JENI PEARL R** - Frontend / UI Specialist

---
