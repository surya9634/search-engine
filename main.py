import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QWidget, QLineEdit, QPushButton, 
                             QHBoxLayout, QLabel, QMessageBox, QProgressBar, QToolBar,
                             QTabWidget, QShortcut)
from PyQt5.QtCore import QUrl, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeySequence
import datetime
import sys
import pyttsx3

class SearchThread(QThread):
    results_ready = pyqtSignal(list, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            google_results = search_google(self.query)
            bing_results = search_bing(self.query)
            ddg_results = search_duckduckgo(self.query)
            qmau_result = search_qmau(self.query)
            yep_result = search_yep(self.query)
            you_result = search_you(self.query)
            web_info = get_web_info(self.query)
            combined_results = google_results + bing_results + ddg_results + qmau_result + yep_result + you_result
            self.results_ready.emit(combined_results, web_info)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AdBlocker(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ad_blocker_enabled = True

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if self.ad_blocker_enabled:
            if url.toString().startswith("https://pagead2.googlesyndication.com/") or \
               url.toString().startswith("https://ads.google.com/") or \
               url.toString().startswith("https://www.googleadservices.com/"):
                return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

class BrowserTab(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.setPage(CustomWebEnginePage(self))
        self.page().loadFinished.connect(self.inject_js)

    def inject_js(self):
        self.page().runJavaScript("""
            (function() {
                if (window.webkitStorageInfo) {
                    navigator.webkitTemporaryStorage = window.webkitStorageInfo;
                    navigator.webkitPersistentStorage = window.webkitStorageInfo;
                }
            })();
        """)

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            self.view().setUrl(url)
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if "window.webkitStorageInfo" in message:
            print("Deprecated API usage detected.")
            self.runJavaScript("""
                (function() {
                    if (window.webkitStorageInfo) {
                        navigator.webkitTemporaryStorage = window.webkitStorageInfo;
                        navigator.webkitPersistentStorage = window.webkitStorageInfo;
                    }
                })();
            """)

class BrowserTab(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setPage(CustomWebEnginePage(self))

    def get_page_text(self):
        self.page().runJavaScript("document.body.innerText", self.handle_page_text)

    def handle_page_text(self, text):
        if text:
            self.main_window.read_aloud_text(text)

class SearchEngineGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Surya Search Engine")
        self.setWindowIcon(QIcon('search_icon.png'))
        self.setMinimumSize(QSize(800, 600))
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")

        self.tts_engine = pyttsx3.init()
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        pixmap = QPixmap('search_icon.png')
        if not pixmap.isNull():
            pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        header_layout.addWidget(self.logo_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the web")
        self.search_input.setFont(QFont("Arial", 18))
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #424242;
                padding: 10px;
                border: 1px solid #5c5c5c;
                border-radius: 5px;
                color: #fff;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)
        header_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont("Arial", 18))
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: #fff;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
        """)
        self.search_button.clicked.connect(self.perform_search)
        header_layout.addWidget(self.search_button)

        self.read_aloud_button = QPushButton("Read Aloud")
        self.read_aloud_button.setFont(QFont("Arial", 18))
        self.read_aloud_button.setStyleSheet("""
            QPushButton {
                background-color: #34A853;
                color: #fff;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2C8E40;
            }
        """)
        self.read_aloud_button.clicked.connect(self.read_aloud)
        header_layout.addWidget(self.read_aloud_button)

        layout.addLayout(header_layout)

        # Toolbar for navigation buttons and URL bar
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #424242;
                border: 1px solid #5c5c5c;
                padding: 5px;
            }
            QPushButton {
                background-color: #4285f4;
                color: #fff;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
        """)
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.toolbar.addWidget(self.back_button)
        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.go_forward)
        self.toolbar.addWidget(self.forward_button)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_page)
        self.toolbar.addWidget(self.refresh_button)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL")
        self.url_bar.setFont(QFont("Arial", 14))
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #424242;
                color: #fff;
                padding: 5px;
                border: 1px solid #5c5c5c;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        layout.addWidget(self.toolbar)

        # Tabs for browsing
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #5c5c5c;
            }
            QTabBar::tab {
                background: #424242;
                color: #fff;
                padding: 10px;
                border: 1px solid #5c5c5c;
                border-bottom: none;
                border-radius: 5px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #357ae8;
            }
        """)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setFixedSize(30, 30)
        self.new_tab_button.setStyleSheet("background-color: #357ae8; color: #fff; border-radius: 15px;")
        self.new_tab_button.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(self.new_tab_button, Qt.TopRightCorner)

        layout.addWidget(self.tabs)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #424242;
                border: 1px solid #5c5c5c;
                border-radius: 5px;
                text-align: center;
                color: #fff;
            }
            QProgressBar::chunk {
                background-color: #4285f4;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Display the welcome page initially
        self.add_new_tab(label="Welcome")

        # Keyboard shortcut for new tab
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_new_tab)

    def add_new_tab(self, qurl=None, label="New Tab"):
        browser = BrowserTab(self)  # Pass the current instance of SearchEngineGUI
        if qurl is None:
            html_content = """
            <html>
            <head>
                <style>
                    body { 
                        background-color: #000; 
                        color: #fff; 
                        text-align: center; 
                        font-family: Arial, sans-serif; 
                        margin-top: 50px; 
                    }
                    h1 { 
                        color: #4285f4; 
                    }
                </style>
            </head>
            <body>
                <h1>Welcome to Surya Search Engine</h1>
                <p>Start by entering a search query above.</p>
            </body>
            </html>
            """
            browser.setHtml(html_content)
        else:
            browser.setUrl(QUrl(qurl))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(self.update_url_bar)
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)


    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())

    def navigate_to_url(self):
        qurl = QUrl(self.url_bar.text())
        if qurl.scheme() == "":
            qurl.setScheme("http")
        self.tabs.currentWidget().setUrl(qurl)

    def go_back(self):
        self.tabs.currentWidget().back()

    def go_forward(self):
        self.tabs.currentWidget().forward()

    def refresh_page(self):
        self.tabs.currentWidget().reload()

    def on_load_started(self):
        self.progress_bar.setVisible(True)

    def on_load_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_load_finished(self):
        self.progress_bar.setVisible(False)

    def perform_search(self):
        query = self.search_input.text()
        self.search_thread = SearchThread(query)
        self.search_thread.results_ready.connect(self.display_results)
        self.search_thread.error_occurred.connect(self.display_error)
        self.search_thread.start()

    def display_results(self, results, web_info):
        new_tab = BrowserTab(self)  # Pass the current instance of SearchEngineGUI
        html = f"""
        <html>
        <head>
            <style>
                body {{ background-color: #000; color: #fff; font-family: Arial, sans-serif; }}
                .result {{ margin-bottom: 20px; }}
                a {{ color: #4285f4; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Search Results</h1>
            <p>{web_info}</p>
            {"".join(f'<div class="result"><a href="#" onclick="window.location.href=\'{result["url"]}\'; return false;">{result["title"]}</a><br>{result["description"]}<br><button onclick="window.location.href=\'{result["url"]}\'; return false;">Read Full Content</button></div>' for result in results)}
        </body>
        </html>
        """
        new_tab.setHtml(html)
        index = self.tabs.addTab(new_tab, f"Results: {self.search_input.text()}")
        self.tabs.setCurrentIndex(index)
        new_tab.urlChanged.connect(self.update_url_bar)

    def display_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)

    def read_aloud(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, BrowserTab):
            current_tab.get_page_text()

    def read_aloud_text(self, text):
        if text:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

def search_qmau(query):
    url = f"https://qmamu.com/search?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for g in soup.find_all(class_='tF2Cxc'):
        title_elem = g.find('h3')
        link_elem = g.find('a')
        desc_elem = g.find(class_='IsZvec')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def search_google(query):
    url = f"https://www.google.com/search?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for g in soup.find_all(class_='tF2Cxc'):
        title_elem = g.find('h3')
        link_elem = g.find('a')
        desc_elem = g.find(class_='IsZvec')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def search_you(query):
    url = f"https://you.com/search?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for g in soup.find_all(class_='tF2Cxc'):
        title_elem = g.find('h3')
        link_elem = g.find('a')
        desc_elem = g.find(class_='IsZvec')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def search_yep(query):
    url = f"https://yep.com/web?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for g in soup.find_all(class_='tF2Cxc'):
        title_elem = g.find('h3')
        link_elem = g.find('a')
        desc_elem = g.find(class_='IsZvec')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def search_bing(query):
    url = f"https://www.bing.com/search?q={query}&num=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for b in soup.find_all(class_='b_algo'):
        title_elem = b.find('h2')
        link_elem = b.find('a')
        desc_elem = b.find(class_='b_caption')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def search_duckduckgo(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for d in soup.find_all(class_='result'):
        title_elem = d.find('a', class_='result__a')
        link_elem = title_elem
        desc_elem = d.find(class_='result__snippet')
        if title_elem and link_elem and desc_elem:
            title = title_elem.text
            link = link_elem['href']
            description = desc_elem.text
            results.append({"title": title, "url": link, "description": description})
    return results

def get_web_info(query):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    web_info = f"Web results for '{query}' fetched on {current_datetime}."
    return web_info

def fetch_full_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Assuming main content is within <article> or <main> tags, otherwise fallback to <div> with class 'content'
    content = soup.find(['article', 'main']) or soup.find('div', class_='content')
    return content.get_text(strip=True) if content else "Full content could not be extracted."

def main_search_engine():
    app = QApplication(sys.argv)
    gui = SearchEngineGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main_search_engine()

