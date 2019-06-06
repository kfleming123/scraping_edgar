# Parsing a 10-Q
# import our libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
import re

# define our base URL
base_url = r"https://www.sec.gov"

# define a CIK number to do a company search
cik_number = '0275880'

# base URL for the SEC Edgar browser
endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

## define our paramters dictionary
param_dict = {'action':'getcompany',
              'CIK':cik_number,
              'type':'424B4',
              'dateb':'',
              'owner':'exclude',
              'start':'',
              'output':'atom',
              'count':'100'}

## request the url and parse the results
response = requests.get(endpoint, params=param_dict)
soup = BeautifulSoup(response.content, 'lxml')

## let the user know it was successful
#print('Request successful')
#print(response.url)
# loop through each found entry, however this is only the first two
# request the url and parse the results
# find all the entry tags

entries = soup.find_all('entry')

# initialize our list for storage
master_list_xml = []

response = requests.get(endpoint, params=param_dict)
soup = BeautifulSoup(response.content, 'lxml')

# grab the first accession number so we can create a url
accession_num = entries[0].find('accession-nunber').text.replace('-', '')

url = base_url + '/Archives/edgar/data/' + cik_number + '/' + accession_num + '/index.json'

# request the url and decode it
content = requests.get(url).json()
for file in content['directory']['item']:
    # grab the filing summary and create a new url leading to the file so we can download it.
    if '424b4.htm' in file['name']:
        tag = 'fin' + file['name'][1:7] + '_2'
        s1_url = base_url + '/Archives/edgar/data/' + cik_number + '/' + accession_num + '/' + file['name']
# Get the S1 content
content = requests.get(s1_url).content
report_soup = BeautifulSoup(content, 'lxml')
# Process the capitalization table
# find all the rows, figure out what type of row it is, parse the elements, and store in the statment file list
data = []
#table = report_soup.find('table', attrs={'class':'report'})
spacesPat = re.compile(r'\s+')
def getCombString(tag) :
    "Get the combined text from a BeautifulSoup tag."
    return spacesPat.sub(" "," ".join(tag.stripped_strings))
def parseCapTab(soup) :
    # find the possible cap tables:
    capTabs = []
    for tableTag in soup.find_all("table") :
        for row in tableTag.find_all("tr") :
            for entry in row.find_all("td") :
                if re.match(r"total\s*capitalization\s*$",getCombString(entry),re.IGNORECASE) :
                    capTabs.append(tableTag)
    if len(capTabs) == 0 :
        print("capitalization table not found!")
        return []
    if len(capTabs) > 1 :
        print("more than one capitalization table found - getting the first")
    else :
        print("one capitalization table found")
    # extract and clean up the text:
    tabContents = [[getCombString(entry) for entry in row.find_all("td")]
                    for row in capTabs[0].find_all("tr")]
    tabContents = [[entry.replace(u'\xa0',' ').replace(u'\x97','-')
                        .replace(u'\x92',"'").replace(u'\u2014',"-")
                    for entry in row if entry not in ['','$']] for row in tabContents]
    tabContents = [row for row in tabContents if row!=[]]
    for row in tabContents :
        for i in range(len(row)-1,0,-1) :
            if row[i]==')' and row[i-1] :
                del row[i]
                row[i-1] += ')'
    return tabContents
# Find the number of shares offered
find_string1 = report_soup.body.find(text=re.compile('Shares'))
shares = int(find_string1.split(' ')[0].replace(',', ''))
# Find offer price
find_string2 = report_soup.body.find('tr', text=re.compile('initial public offering price'))
print(find_string2)
#test = report_soup.find('Table')
#print(test)
#for i in test:
#    print(i)
#    test2 = i.find_parents('table')
#    data.append(test2)
#print(data)
#rows = table.find_all('tr')
#for row in rows:
#    cols = row.find_all('td')
#    cols = [ele.text.strip() for ele in cols]
#    data.append([ele for ele in cols if ele])
#new_data = []
#for d in data:
#    if len(d) > 1:
#        new_data.append(d)
#balance_sheet_data = []
#key_data_terms = ['CASH AND CASH EQUIVALENTS', 'ACCOUNTS RECEIVABLE', 'INVENTORY', 'LONG-TERM DEBT']
#for n in new_data:
#    for k in key_data_terms:
#        if k in n[0].upper():
#            balance_sheet_data.append(n)
#print(balance_sheet_data)


# define a new base url that represents the filing folder.  This will come in handy when we want to download the reports.
#base_url2 = xml_summary.replace('FilingSummary.xml', '')
#
## request and parse the content
#content = requests.get(xml_summary).content
#soup = BeautifulSoup(content, 'lxml')
#
## find the myreports tag because this contains all of the individual reports submitted
#reports = soup.find('myreports')
#
## I want a list to store all of the individual components of the report, so create the master list.
#master_reports = []

# loop through each report in myreports, but avoid the last one as this will cause an error.
#for report in reports.find_all('report')[0:20]:
#    # let's create a dictionary to store all the parts we need
#    report_dict = {}
#    report_dict['name_short'] = report.shortname.text
#    report_dict['name_long'] = report.longname.text
#    report_dict['position'] = report.position.text
#    report_dict['category'] = report.menucategory.text
#    report_dict['url'] = base_url2 + report.htmlfilename.text
#    # append the report dictionary to the master list
#    master_reports.append(report_dict)
#    # print the info to the user
##    print('-'*100)
##    print(base_url2 + report.htmlfilename.text)
##    print(report.longname.text)
##    print(report.shortname.text)
##    print(report.menucategory.text)
##    print(report.position.text)
##print(master_reports)
## create the list to hold the statements urls
##statements_url = []
##statements_list = [1, 3, 5]
##for statement_no in statements_list:
##    statements_url.append(master_reports[statement_no]['url'])
##print(statements_url)
#    # define the statements we want to look for
#bs1 = r"CONSOLIDATED BALANCE SHEET"
#inc_state1 = r"STATEMENT OF OPERATIONS"
#inc_state2 = r"STATEMENTS OF OPERATIONS"
#inc_state3 = r"STATEMENTS OF INCOME"
#inc_state4 = r"STATEMENT OF INCOME"
#inc_state5 = r"STATEMENT OF COMPREHENSIVE INCOME"
#inc_state6 = r"STATEMENTS OF COMPREHENSIVE INCOME"
#cash_flow1 = r"STATEMENT OF CASH FLOWS"
#cash_flow2 = r"STATEMENTS OF CASH FLOWS"
## store them in a list
#inc_state_list = [inc_state1, inc_state2, inc_state3, inc_state4, inc_state5, inc_state6]
#cash_flow_list = [cash_flow1, cash_flow2]
#
#for report_dict in master_reports:
#    if bs1 in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
#        balance_sheet_url = report_dict['url']
#
#income_statements = []
#for report_dict in master_reports:
#    for item in inc_state_list:
#        if item in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
#            income_statements.append(report_dict['url'])
#income_statement_url = income_statements[0]
#
#for report_dict in master_reports:
#    for item in cash_flow_list:
#        if item in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
#            cash_flow_url = report_dict['url']
#
## Process the balance sheet
#content = requests.get(balance_sheet_url).content
#report_soup = BeautifulSoup(content, 'lxml')
## find all the rows, figure out what type of row it is, parse the elements, and store in the statment file list
#data = []
#table = report_soup.find('table', attrs={'class':'report'})
#headers = table.find_all('th', attrs={'class':'th'})
#rows = table.find_all('tr')
#for row in rows:
#    cols = row.find_all('td')
#    cols = [ele.text.strip() for ele in cols]
#    data.append([ele for ele in cols if ele])
#new_data = []
#for d in data:
#    if len(d) > 1:
#        new_data.append(d)
#balance_sheet_data = []
#key_data_terms = ['CASH AND CASH EQUIVALENTS', 'ACCOUNTS RECEIVABLE', 'INVENTORY', 'LONG-TERM DEBT']
#for n in new_data:
#    for k in key_data_terms:
#        if k in n[0].upper():
#            balance_sheet_data.append(n)
#print(balance_sheet_data)
#
## Process the income statement
#content = requests.get(income_statement_url).content
#report_soup = BeautifulSoup(content, 'lxml')
## find all the rows, figure out what type of row it is, parse the elements, and store in the statment file list
#data = []
#table = report_soup.find('table', attrs={'class':'report'})
#headers = table.find_all('th', attrs={'class':'th'})
#rows = table.find_all('tr')
#for row in rows:
#    cols = row.find_all('td')
#    cols = [ele.text.strip() for ele in cols]
#    data.append([ele for ele in cols if ele])
#new_data = []
#for d in data:
#    if len(d) > 1:
#        new_data.append(d)
#income_statement_data = []
#key_data_terms = ['REVENUE', 'OPERATING INCOME', 'INCOME FROM OPERATIONS']
#for n in new_data:
#    for k in key_data_terms:
#        if k in n[0].upper():
#            income_statement_data.append(n)
#print(income_statement_data)
#
## Process the cash flow statement
#content = requests.get(cash_flow_url).content
#report_soup = BeautifulSoup(content, 'lxml')
## find all the rows, figure out what type of row it is, parse the elements, and store in the statment file list
#data = []
#table = report_soup.find('table', attrs={'class':'report'})
#headers = table.find_all('th', attrs={'class':'th'})
#rows = table.find_all('tr')
#for row in rows:
#    cols = row.find_all('td')
#    cols = [ele.text.strip() for ele in cols]
#    data.append([ele for ele in cols if ele])
#new_data = []
#for d in data:
#    if len(d) > 1:
#        new_data.append(d)
#cash_flow_data = []
#key_data_terms = ['CASH FLOW FROM OPERATIONS', 'NET CASH PROVIDED BY OP', 'DEPRECIATION AND AMORTIZATION', 'STOCK COMPENSATION', 'EQUITY COMPENSATION']
#for n in new_data:
#    for k in key_data_terms:
#        if k in n[0].upper():
#            cash_flow_data.append(n)
#print(cash_flow_data)
#
