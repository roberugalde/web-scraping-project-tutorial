

import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Fetch HTML with requests
url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"
time.sleep(10)
html_data = requests.get(url).text

# Handle 403 error
if "403 Forbidden" in html_data:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    time.sleep(10)
    html_data = requests.get(url, headers=headers).text

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html_data, "html.parser")
tables = soup.find_all("table")

# Identify the correct table
table_index = None
for index, table in enumerate(tables):
    if "Tesla Quarterly Revenue" in str(table):
        table_index = index
        break

if table_index is None:
    raise ValueError("Table not found")

# Create DataFrame
data = []
for row in tables[table_index].tbody.find_all("tr"):
    col = row.find_all("td")
    if col:
        Date = col[0].text.strip()
        Revenue = col[1].text.replace("$", "").replace(",", "").strip()
        data.append({"Date": Date, "Revenue": Revenue})

tesla_revenue = pd.DataFrame(data)
tesla_revenue = tesla_revenue[tesla_revenue["Revenue"] != ""]
tesla_revenue["Date"] = pd.to_datetime(tesla_revenue["Date"])
tesla_revenue["Revenue"] = tesla_revenue["Revenue"].astype("int")

# Save to SQLite
connection = sqlite3.connect("Tesla.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS revenue (Date TEXT, Revenue INTEGER)")
tesla_tuples = list(tesla_revenue.to_records(index=False))
cursor.executemany("INSERT INTO revenue VALUES (?,?)", tesla_tuples)
connection.commit()

# Query and print data
for row in cursor.execute("SELECT * FROM revenue"):
    print(row)

# Plot data
plt.figure(figsize=(10, 5))
sns.lineplot(data=tesla_revenue, x="Date", y="Revenue")
plt.title("Tesla Quarterly Revenue")
plt.tight_layout()
plt.show()



