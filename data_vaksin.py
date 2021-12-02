from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as DT
from requests_html import HTMLSession
from google_drive_downloader import GoogleDriveDownloader as gdd
import pandas as pd
import os
from selenium import webdriver
import time


data = []
url = "https://riwayat-file-vaksinasi-dki-jakarta-jakartagis.hub.arcgis.com/"
# url = "https://riwayat-file-covid-19-dki-jakarta-jakartagis.hub.arcgis.com/"

session = HTMLSession()
r = session.get(url)
r.html.render(sleep=10, timeout = 25)
res = BeautifulSoup(r.html.raw_html, "html.parser")

# driver = webdriver.Chrome(executable_path=r'C:/Users/Farhan Achsani/Downloads/chromedriver_win32/chromedriver.exe')
# driver.maximize_window()
# driver.get(url)

# time.sleep(5)
# content = driver.page_source.encode('utf-8').strip()
# res = BeautifulSoup(content, "html.parser")

links = res.find_all("a")
# print(len(links))

for link in res.find_all('a', href=True):
    data.append(link)

# 164 - 150 -> 150 - 140 -> 127 - 105 -> 85 - 40 -> 41 - 10
# for x in range(41, 10, -1) :
#     y = x - 6


# Tanggal vaksin hilang 19 Juli, 28 Agustus, 11 September
# 20 Juni 2021 = 167
# Yg tanggal terbaru di nomor 7
link = data[10]['href']
id_file = link[32:65]
judul = data[10].get_text()


destination = './' + judul + ".xlsx"
gdd.download_file_from_google_drive(file_id=id_file, dest_path=destination)
judul_excel = judul + ".xlsx"

# temp = pd.read_excel(judul_excel)

# date tanggal = -3 data vaksin karena ada 3 tanggal yg hilang, pada saat tanggal bener semua jadi -6
# 20 Juni 2021 = 164
# Yg terbaru di nomor 1
today = DT.date.today()
date = today - DT.timedelta(days=4)
str_date = str(date)


# # (0 = A, Kode Kel) (1 = B, Wil Kota) (2 = C, Kecamatan) (3 = D, Kelurahan) (4 = E, Sasaran) (5 = F, Belum Vaksin) (6 = G, Jumlah Dosis 1) (7 = H, Jumlah Dosis 2) (8 = I, Total Vaksin)
cols_kelurahan = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# Tanggal 30 Juli berubah menjadi 2 sheet
kelurahan = pd.read_excel(judul_excel, header = 0, sheet_name="Data Kelurahan", usecols=cols_kelurahan)
# kelurahan = pd.read_excel(judul_excel, header = 0, usecols=cols_kelurahan)
kelurahan.rename(columns={'JUMLAH\nDOSIS 1' : 'DOSIS 1', 'JUMLAH\nDOSIS 2' : 'DOSIS 2', 'TOTAL VAKSIN\nDIBERIKAN' : 'TOTAL VAKSIN'}, inplace=True)
kelurahan = kelurahan.iloc[1:]
kelurahan['TANGGAL'] = date
kelurahan['KODE KELURAHAN'] = kelurahan['KODE KELURAHAN'].astype('int64')

# print(id_file)
print(judul)
print(str_date)
# print(kelurahan['KODE KELURAHAN'].dtype)

destination_kelurahan = './Vaksin-Covid19-JKT-Kelurahan.csv'

past_kelurahan = pd.read_csv(destination_kelurahan)

# print(past_kelurahan.head())

past_kelurahan = past_kelurahan.append(kelurahan)


os.remove(destination)
os.remove(destination_kelurahan)

# For iteration other than the first time
past_kelurahan.to_csv(destination_kelurahan,index=False)

# # For first iteration to csv
# kelurahan.to_csv(destination_kelurahan,index=False)
