import config
import codecs
import csv
import logging
import shutil
import tempfile
import urllib.request
import xlrd
import pandas as pd

def putScopusJournalListOnDisk():
    saveFilePerHttpToDiskAsCsv(config.scopusJournalListUrl, config.scopusFileListFileNameOnDisk)

def putSCIJournalListOnDisk():
    for i in range(1, 20):
        try:
            saveFileFromUrlToDisk(config.sciJournalListUrl + str(i), config.sciFileListNameOnDiskPrefix + "_" + str(i) + ".csv")
            logging.info("Save to file: " + config.sciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.sciJournalListUrl + str(i))
            print("Save to file: " + config.sciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.sciJournalListUrl + str(i))
        except:
            print("Not saved to file: " + config.sciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.sciJournalListUrl + str(i))

def putSSCIJournalListOnDisk():
    for i in range(1, 20):
        try:
            saveFileFromUrlToDisk(config.ssciJournalListUrl + str(i), config.ssciFileListNameOnDiskPrefix + "_" + str(i) + ".csv")
            logging.info("Save to file: " + config.ssciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.ssciJournalListUrl + str(i))
            print("Save to file: " + config.ssciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.ssciJournalListUrl + str(i))
        except:
            print("Not saved to file: " + config.ssciFileListNameOnDiskPrefix + "_" + str(i) + ".csv"
                         + " from " + config.ssciJournalListUrl + str(i))

# def saveFilePerHttpToDiskAsCsv(url, filename):
#     logging.info("Save to file: " + filename + " from " + url)
#     print("Save to file: " + filename + " from " + url)
#     req = urllib.request.Request(url)
#     with urllib.request.urlopen(req) as response:
#         with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
#             shutil.copyfileobj(response, tmp_file)
#         # with open(tmp_file.name) as file:
#             wb = xlrd.open_workbook(tmp_file.name)
#             sh = wb.sheet_by_index(0)
#             scopusJournalList = sh.col_values(1, 1)
#             your_csv_file = open("./data/" + filename, 'w', encoding='utf8')
#             wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
#
#             for rownum in range(sh.nrows):
#                 wr.writerow(sh.row_values(rownum))
#
#             your_csv_file.close()
#             with codecs.open('./data/' + config.scopusFileListFileNameOnDisk, 'w', 'utf-8') as fw:
#                 for item in scopusJournalList:
#                     fw.write(item + "\n")

def saveFilePerHttpToDiskAsCsv(url, filename):
    print("Save to file: " + filename + " from " + url)
    # Download the file from `url` and save it locally under 'temp2.xlsx' first:
    with urllib.request.urlopen(url) as response, open('temp2.xlsx', 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

    # convert xlsx to csv
    df = pd.read_excel('temp2.xlsx', header=1, usecols=[1])  # , sheetname='<your sheet>'
    df.to_csv('./data/' + config.scopusFileListFileNameOnDisk, index=False, quotechar='"')

def saveFileFromUrlToDisk(url, filename):
    logging.info("Save to file: " + filename + " from " + url)
    print("Save to file: " + filename + " from " + url)
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    pagesString = mybytes.decode("utf-8")
    fp.close()
    with codecs.open('./data/' + filename, 'w', 'utf-8') as fw:
        fw.write(pagesString)
