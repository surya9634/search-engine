# search-engine
Hi, are you ready for experiencing the first Indian search engine "Surya"? I know it's not that advanced, but it's my first module. Here are all the functions of my search engine: search different search engine results to give you results on one engine, read aloud function for those who want to hear it in English right now, which also looks good.

# Surya
This code is essentially a **web search engine application** that performs the following tasks:

### Main Purpose:
- The app allows users to search for information from multiple search engines like Google, Bing, DuckDuckGo, and others.
- It displays the results in a visually appealing interface and also reads the content aloud if the user wishes.

### Breakdown of Functions:

1. **Environment Setup:**
   - The `os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'` disables the sandbox feature of QtWebEngine. This step is needed to avoid issues in specific environments where the sandbox might block certain operations.

2. **Imported Libraries:**
   - **PyQt5**: This is used to create the application's graphical interface. It controls the layout, buttons, search bar, and how the content is displayed.
   - **BeautifulSoup and Requests**: These are used to scrape web search results from search engines by sending requests to the web and parsing the HTML content.
   - **QWebEngine**: This is used to display web pages inside the application, allowing users to view the search results.
   - **Text-to-Speech Engine (pyttsx3)**: Used to convert text into speech so users can listen to the search results.

3. **SearchThread Class:**
   - This class handles the actual search process by sending queries to different search engines like Google, Bing, DuckDuckGo, etc., fetching the results, and then returning them to the main application.

4. **AdBlocker Class:**
   - This class is an optional feature to block ads from appearing when users browse pages. It prevents certain ad-related URLs from loading.

5. **BrowserTab Class:**
   - It represents each tab in the browser part of the app. When you search, the results are shown in a new tab, and you can interact with them. It also allows the app to read aloud any text on the page.

6. **SearchEngineGUI Class:**
   - This class handles the main interface of the app. It defines the layout of the search engine, including the search bar, buttons, results, and navigation features.
   - It supports multiple tabs like a regular browser and includes buttons for navigating back, forward, and refreshing pages.
   - There's also a toolbar to enter URLs directly, and a button to create new tabs.
   - The search function lets users search multiple engines and display combined results in a new tab.
   - Additionally, it includes a text-to-speech option where the app reads out the content of the current tab.

7. **Search Functions:**
   - Functions like `search_google()`, `search_bing()`, `search_duckduckgo()`, etc., take a search query, send it to the respective search engine, and return a list of results. Each result includes a title, URL, and description.

### Simple Explanation for Non-Technical Users:

Imagine you have a search engine like Google, but instead of just using one search engine, this app gathers information from **multiple websites** (Google, Bing, DuckDuckGo, etc.) and shows you the best results in one place. You type in your question or search, click the search button, and the app will display results from various websites in a new tab, just like how you use a regular browser.

Additionally, if you don’t feel like reading the results, the app can **read them aloud** to you. You can also open different tabs and browse multiple topics at once.

Moreover, if you don't like ads (advertisements), this app can block those for you so that they won’t interrupt your browsing.
