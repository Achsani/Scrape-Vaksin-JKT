from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as DT
from requests_html import HTMLSession
from google_drive_downloader import GoogleDriveDownloader as gdd
import pandas as pd
import os
from selenium import webdriver
import time

# List for all href scraped 
data = []

# Url that we want to scrape
url = "https://riwayat-file-vaksinasi-dki-jakarta-jakartagis.hub.arcgis.com/"

# Run HTMLSession to scrape dynamic page
session = HTMLSession()
r = session.get(url)
r.html.render(sleep=10, timeout = 25)
res = BeautifulSoup(r.html.raw_html, "html.parser")


# Get all href data and insert it to data list
for link in res.find_all('a', href=True):
    data.append(link)

# Getting google drive id for newest data
# Missing vaccination data on date 19 July, 28 August, 11 September
# 20 Juni 2021 = 167
# Newest data on number 7
link = data[7]['href']
id_file = link[32:65]
judul = data[7].get_text()


# Download excel data using google drive id
destination = './' + judul + ".xlsx"
gdd.download_file_from_google_drive(file_id=id_file, dest_path=destination)
judul_excel = judul + ".xlsx"

# Get yesterday's date to be included in covid vaccination data
# 20 Juni 2021 = 164
# Yg terbaru di nomor 1
today = DT.date.today()
date = today - DT.timedelta(days=1)
str_date = str(date)

# Column where we want the data  reside
# # (0 = A, Kode Kel) (1 = B, Wil Kota) (2 = C, Kecamatan) (3 = D, Kelurahan) (4 = E, Sasaran) (5 = F, Belum Vaksin) (6 = G, Jumlah Dosis 1) (7 = H, Jumlah Dosis 2) (8 = I, Total Vaksin)
cols_kelurahan = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# On 30 July excel data changed from 1 sheet to 2 sheets
# Read downloaded data and exctract column that's needed
kelurahan = pd.read_excel(judul_excel, header = 0, sheet_name="Data Kelurahan", usecols=cols_kelurahan)
# kelurahan = pd.read_excel(judul_excel, header = 0, usecols=cols_kelurahan)
kelurahan.rename(columns={'JUMLAH\nDOSIS 1' : 'DOSIS 1', 'JUMLAH\nDOSIS 2' : 'DOSIS 2', 'TOTAL VAKSIN\nDIBERIKAN' : 'TOTAL VAKSIN'}, inplace=True)
kelurahan = kelurahan.iloc[1:]
kelurahan['TANGGAL'] = date
kelurahan['KODE KELURAHAN'] = kelurahan['KODE KELURAHAN'].astype('int64')


print(judul)
print(str_date)

# Location of old data that we want to append
destination_kelurahan = './Vaksin-Covid19-JKT-Kelurahan.csv'

#Read past data
past_kelurahan = pd.read_csv(destination_kelurahan)

# Append past data with new data
past_kelurahan = past_kelurahan.append(kelurahan)

# Remove old and downloaded file
os.remove(destination)
os.remove(destination_kelurahan)

# Export newest data on dataframe to CSV
# For iteration other than the first time
past_kelurahan.to_csv(destination_kelurahan,index=False)

# # For first iteration to csv
# kelurahan.to_csv(destination_kelurahan,index=False)
