# Parsing a 10-Q
# import our libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup

# define our base URL
base_url = r"https://www.sec.gov"

# define a CIK number to do a company search
cik_number = '1223389'

# base URL for the SEC Edgar browser
endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

## define our paramters dictionary
param_dict = {'action':'getcompany',
              'CIK':cik_number,
              'type':'8-K',
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
print(url)
# request the url and decode it
content = requests.get(url).json()

for file in content['directory']['item']:
    # grab the filing summary and create a new url leading to the file so we can download it.
    if file['name'] == 'FilingSummary.xml':
        xml_summary = base_url + content['directory']['name'] + '/' + file['name']

# define a new base url that represents the filing folder.  This will come in handy when we want to download the reports.
base_url2 = xml_summary.replace('FilingSummary.xml', '')

# request and parse the content
content = requests.get(xml_summary).content
soup = BeautifulSoup(content, 'lxml')

# find the myreports tag because this contains all of the individual reports submitted
reports = soup.find('myreports')

# I want a list to store all of the individual components of the report, so create the master list.
master_reports = []

# loop through each report in myreports, but avoid the last one as this will cause an error.
for report in reports.find_all('report')[0:20]:
    # let's create a dictionary to store all the parts we need
    report_dict = {}
    report_dict['name_short'] = report.shortname.text
    report_dict['name_long'] = report.longname.text
    report_dict['position'] = report.position.text
    report_dict['category'] = report.menucategory.text
    report_dict['url'] = base_url2 + report.htmlfilename.text
    # append the report dictionary to the master list
    master_reports.append(report_dict)

    # print the info to the user
#    print('-'*100)
#    print(base_url2 + report.htmlfilename.text)
#    print(report.longname.text)
#    print(report.shortname.text)
#    print(report.menucategory.text)
#    print(report.position.text)

# create the list to hold the statements urls
#statements_url = []
#statements_list = [1, 3, 5]
#for statement_no in statements_list:
#    statements_url.append(master_reports[statement_no]['url'])
#print(statements_url)
    # define the statements we want to look for
bs1 = r"CONSOLIDATED BALANCE SHEET"
inc_state1 = r"STATEMENT OF OPERATIONS"
inc_state2 = r"STATEMENTS OF OPERATIONS"
inc_state3 = r"STATEMENTS OF INCOME"
inc_state4 = r"STATEMENT OF INCOME"
inc_state5 = r"STATEMENT OF COMPREHENSIVE INCOME"
inc_state6 = r"STATEMENTS OF COMPREHENSIVE INCOME"
cash_flow1 = r"STATEMENT OF CASH FLOWS"
cash_flow2 = r"STATEMENTS OF CASH FLOWS"
# store them in a list
inc_state_list = [inc_state1, inc_state2, inc_state3, inc_state4, inc_state5, inc_state6]
cash_flow_list = [cash_flow1, cash_flow2]

for report_dict in master_reports:
    if bs1 in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
        balance_sheet_url = report_dict['url']

income_statements = []
for report_dict in master_reports:
    for item in inc_state_list:
        if item in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
            income_statements.append(report_dict['url'])

for report_dict in master_reports:
    for item in cash_flow_list:
        if item in report_dict['name_short'].upper() and 'Parenthetical' not in report_dict['name_short']:
            cash_flow_url = report_dict['url']

print(balance_sheet_url)
print(income_statements[0])
print(cash_flow_url)

#        
#    # if the short name can be found in the report list.
#    if report_dict['name_short'] in report_list:
#        statements_url.append(report_dict['url'])

#print(statements_url)
# Let's assume we want all the statements in a single data set.
#statements_data = []
#
## loop through each statement url
#for statement in statements_url:
#    # define a dictionary that will store the different parts of a statement
#    statement_data = {}
#    statement_data['headers'] = []
#    statement_data['sections'] = []
#    statement_data['data'] = []
#    # request the statement content
#    content = requests.get(statement).content
#    report_soup = BeautifulSoup(content, 'lxml')
#    # find all the rows, figure out what type of row it is, parse the elements, and store in the statment file list
#    for index, row in enumerate(report_soup.table.find_all('tr')):
#        # first let's get all the elements
#        cols = row.find_all('td')
#        # if its a regular row and not a section or table header
#        if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0):
#            reg_row = [ele.text.strip() for ele in cols]
#            statement_data['data'].append(reg_row)
#        # if its a regular row and a section but not a table header
#        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
#            sec_row = cols[0].text.strip()
#            statement_data['sections'].append(sec_row)
#        # finally if its not any of those it must be a header
#        elif len(row.find_all('th')) != 0:
#            head_row = [ele.text.strip() for ele in row.find_all('th')]
#            statement_data['headers'].append(head_row)
#        else:
#            print('We encountered an error.')
#    
#    # append the data to the master list
#    statements_data.append(statement_data)
#print(statements_data)
#print(len(statements_data))
#
## Grab the proper components
#income_headers = statements_data[2]['headers'][1]
#income_data = statements_data[2]['data']
#
## put the data in a data frame
#income_df = pd.DataFrame(income_data)
#
## Display
##print('-'*100)
##print('Before Reindexing')
##print('-'*100)
##print(income_df.head())
#
## Define the index column, rename it, and make sure to drop the old column once we rename it
#income_df.index = income_df[0]
#income_df.index.name = 'Category'
#income_df = income_df.drop(0, axis=1)
#
## Display
##print('-'*100)
##print('Before Regex')
##print('-'*100)
##print(income_df.head())
#
## Get rid of '$', '(', ')' and convert '' to 'NaN'
#income_df = income_df.replace('[\$,)]', '', regex = True)\
#                    .replace('[(]', '-', regex = True)\
#                    .replace('', 'NaN', regex = True)
#
## Display
##print('-'*100)
##print('Before Type Conversion')
##print('-'*100)
##print(income_df.head())
##
## Everything is a string so let's convert all the data to floats
#income_df = income_df.astype(float)
#
## change the column headers
#income_df.columns = income_headers
#
## Display
#print('-'*100)
#print('Final Product')
#print('-'*100)
## show the df
#print(income_df)
#print(statements_data[0])
### drop the data in a csv file if need be
##income_df.to_csv('10Q.csv')
