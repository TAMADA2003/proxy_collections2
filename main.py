import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import base64
import json
import requests

encoded_string = "MjEyLjgzLjEzOC4xMzI="
decoded_bytes = base64.b64decode(encoded_string)
decoded_string = decoded_bytes.decode('utf-8')

print(decoded_string)


def proxy():
    # Connect to the SQLite database
    conn = sqlite3.connect('proxy.db')
    cursor = conn.cursor()

    # Create a 'proxy' table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS proxy (
                          id INTEGER PRIMARY KEY,
                          ip TEXT,
                          port TEXT,
                          anonymity TEXT,
                          country TEXT,
                          speed INTEGER,
                          check_time TEXT)''')

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()

    # Loop through 9 pages on 'https://advanced.name/ru/freeproxy'
    for page in range(1, 10):
        driver.get(f'https://advanced.name/ru/freeproxy?page={page}')

        # Get HTML code of the page
        html = driver.page_source

        # Use BeautifulSoup for HTML parsing
        soup = BeautifulSoup(html, 'html.parser')

        # Find all <tr> elements in HTML
        rows = soup.find_all('tr')

        # Iterate through each <tr> element
        for row in rows:
            # Get text from each <td> cell
            columns = row.find_all('td')

            # Check if there are at least 7 columns (adjust if needed)
            if len(columns) >= 7:
                id, port, protocol, anonymity, country, speed, check_time = [column.text.strip() for column in
                                                                             columns[:8]]
                cursor.execute("SELECT * FROM proxy WHERE ip=?", (port,))

                fetched_row = cursor.fetchone()
                if not fetched_row:
                    save_info(port, protocol, anonymity, country, speed, check_time)


# Function to save proxy information to the database
def save_info(port, protocol, anonymity, country, speed, check_time):
    conn = sqlite3.connect('proxy.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO proxy (ip, port, country,anonymity,speed, check_time) VALUES (?, ?, ?, ?, ?, ?)',
        (port, protocol, anonymity, country, speed, check_time))
    conn.commit()
    conn.close()


# Function to scrape proxy information from 'https://proxyhub.me/ru/all-free-proxy-list.html'
def proxy2():
    try:
        driver = webdriver.Chrome()
        conn = sqlite3.connect('proxy.db')
        cursor = conn.cursor()

        url = 'https://proxyhub.me/ru/all-free-proxy-list.html'
        driver.get(url)

        # Click on the second page link
        page_links = driver.find_elements(By.CSS_SELECTOR, 'span.page-link[page]')
        if len(page_links) >= 2:
            second_page_link = page_links[1]
            second_page_link.click()

        # Loop through 110 pages
        for i in range(1, 110):
            print(i)

            # Get HTML code of the page
            html_code = driver.page_source

            # Create BeautifulSoup object
            soup = BeautifulSoup(html_code, 'html.parser')

            # Find all table rows
            table_rows = soup.find_all('tr')

            # Iterate through each row and extract data
            for row in table_rows:
                columns = row.find_all('td')
                if columns:
                    ip_address = columns[0].text
                    port = columns[1].text
                    protocol = columns[2].text
                    anonymity = columns[3].text
                    country = columns[4].a.text
                    speed = 0
                    check_time = 0
                    cursor.execute("SELECT * FROM proxy WHERE ip=?", (ip_address,))

                    fetched_row = cursor.fetchone()
                    if not fetched_row:
                        save_info(ip_address, port, protocol, anonymity, country, speed)

            # Get page links for the next iteration
            page_links = driver.find_elements(By.CSS_SELECTOR, 'span.page-link[page]')

            if len(page_links) >= 2:
                try:
                    second_page_link = page_links[3]
                    second_page_link.click()
                except IndexError:
                    print("Error: list index out of range")

    except ZeroDivisionError:
        print("All pages processed")


# Function to scrape proxy information from 'https://fineproxy.org/wp-content/themes/fineproxyorg/proxy-list.php?0.728653483723184'
def proxy3():
    url = 'https://fineproxy.org/wp-content/themes/fineproxyorg/proxy-list.php?0.728653483723184'
    response = requests.get(url)

    if response.status_code == 200:
        html_code = response.text
        with open('page.html', 'w', encoding='utf-8') as file:
            file.write(html_code)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

    json_data = html_code
    data = json.loads(json_data)

    filtered_results = []

    for record in data:
        filtered_results.append(
            {
                "ip": record.get("ip"),
                "port": record.get("port"),
                "country_name": record.get("country_name"),
                "checks_up": record.get("checks_up"),
                "anon": record.get("anon"),
                "http ": record.get("http "),
                "ssl": record.get("ssl"),
                "socks4": record.get("socks4"),
                "socks5": record.get("socks5"),
            }
        )
        ip = record.get('ip')
        port = record.get('port')
        country_name = record.get("country_name")
        anon = record.get("anon")
        http1 = record.get("http")
        ssl = record.get("ssl")
        socks4 = record.get("socks4")
        socks5 = record.get("socks5")
        anon1 = ""
        http2 = ""
        ssl1 = ""
        socks41 = ""
        socks51 = ""
        if http1 == "1":
            http2 = "http"
        if anon == "1":
            anon1 = "anon"
        if ssl == "1":
            ssl1 = "ssl"
        if socks4 == "1":
            socks41 = "socks4"
        if socks5 == "1":
            socks51 = "socks5"
        speed = 0
        chack_time = 0
        annosr = anon1, http2, ssl1, socks41, socks51
        annosr_str = str(annosr)
        conn = sqlite3.connect('proxy.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proxy WHERE ip=?", (port,))

        fetched_row = cursor.fetchone()
        if not fetched_row:
            save_info(ip, port, annosr_str, country_name, speed, chack_time)


# Function to print proxy information in CSV format
def csv_format():
    conn = sqlite3.connect('proxy.db')
    cursor = conn.cursor()
    query = "SELECT id, port FROM proxy"
    cursor.execute(query)

    # Извлечение всех строк сразу
    rows = cursor.fetchall()
    for row in rows:
        id, ip, port = row
        print(f"{ip}:{port}")

if __name__ == "__main__":
    proxy2()
    proxy3()
