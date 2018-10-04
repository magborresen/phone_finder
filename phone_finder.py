from urllib.request import urlopen
import ssl
from bs4 import BeautifulSoup as bs
import sqlite3
import os
import json
from send_ios_notification import send_to_mag

database = "phone_database.sqlite"
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), database)


def page_switcher():

    page = 1
    url = "https://www.dba.dk/soeg/?soeg=defekt+iphone"
    context = ssl._create_unverified_context()
    html = urlopen(url, context=context)
    soup = bs(html, features="html.parser")

    div_page_list = soup.find("div", attrs={"class": "pagination"})
    list_len = int(div_page_list.find_all("li")[-2].get_text())
    find_phones(soup)

    while page <= list_len:
        url = "https://www.dba.dk/soeg/side-{}/?soeg=defekt+iphone".format(page)
        html = urlopen(url, context=context)
        soup = bs(html, features="html.parser")
        find_phones(soup)
        page += 1


def connect_db(db_path=DEFAULT_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Link is Primary Key in this db because it's the only unique element
    c.execute("""CREATE TABLE IF NOT EXISTS phones (
                model TEXT,
                storage TEXT,
                color TEXT,
                description TEXT,
                link TEXT PRIMARY KEY,
                price TEXT
                )""")

    conn.commit()
    conn.close()


def find_phones(soup):
    # Scrapes all useful table data from the row.
    table_data = soup.find_all("tr", attrs={"class": "dbaListing"})

    # Loop goes through the list of data to pick out what is neeeded.
    for link in table_data:
        div_link = link.find("div", attrs={"class": "expandable-box"})
        phone = div_link.find("a", attrs={"class": "listingLink"})

        # JSON is only used to fetch price data since it's not detailed.
        json_data = link.find("script", attrs={"type": "application/ld+json"})
        read_json = json.loads(json_data.get_text(), strict=False)
        split_data = read_json['name'].split(',')

        '''Logic checks if the phone is actually broken and not sold by a
            company or that someone wants to buy broken phones.'''

        sort_unwanted = ["gå til varen",
                         "defekter",
                         "købe",
                         "iphone 4",
                         "iphone 5",
                         "iphone 5s",
                         "iphone 5c",
                         "iphone 6",
                         "perfekt"
                        ]

        if any(word in phone.get_text().lower() for word in sort_unwanted):
            pass
        elif "iphone" not in split_data[0].lower():
            pass
        else:
            description = phone.get_text()
            try:
                update_db(read_json,
                          description)
                send_to_mag(read_json, description)
            except sqlite3.IntegrityError:
                pass


def update_db(json_data, description, db_path=DEFAULT_PATH):

    conn = sqlite3.connect(db_path)

    c = conn.cursor()

    split_data = json_data['name'].split(',')

    model = split_data[0]
    storage = split_data[1]
    color = split_data[2]
    phone_link = json_data['url']
    price = (json_data['offers']['price'] + " " +
             json_data['offers']['priceCurrency'])

    c.execute("INSERT INTO phones VALUES (:model, :storage, :color, :description, :link, :price)",
              {"model": model, "storage": storage, "color": color,
               "description": description, "link": phone_link, "price": price})

    conn.commit()
    conn.close()


if __name__ == "__main__":
    while True:
        connect_db()
        page_switcher()
