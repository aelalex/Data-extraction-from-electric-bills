import sys,os
import fnmatch
import fitz #pip install PyMuPDF
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def find_all_files(path):
    """ Find all PDF files"""
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files,'*.pdf'):
            full_path=os.path.abspath(file)
            all_files.append(os.path.join(root, file))
    return all_files

def pdf_extraction(files):
    """ Extract data from pdfs and put all pages on a list. Each index of the list corresponds to a single pdf's text."""
    all_text = []
    for file in files:
        doc = fitz.open(file)
        text = ""
        for page in doc:
            text+=page.get_text()
        all_text.append(text)

    return all_text

def find_amount(text,amount):
    """ Extract the amount to pay. It always has the symbol * before the amount (in Euros), e.g., *195,00 """
    match=re.search(r'\*\d{1,},\d{1,}',text)
    #add exception when there is a refund and no amount is written
    try:
        value=match.group(0)[1:]
        value=value[:-1]
        value=value.replace(',', '.')
        amount.append(float(value))
    except:
        print('Add zero if the bill is negative')
        amount.append(0)
    else:
         pass
    return amount

def find_consumption(text,amount):
    """ Extract the consumption of kWh  """
    match=re.search(r"\d{1,} kWh|\d.\d{1,} kWh",text)
    #add exception when there is a refund and no amount is written
    try:
        value=match.group(0).split()
        amount.append(float(value[0]))
    except:
        print('Add zero if there is no consumption')
        amount.append(0)

    return amount

def find_date(text,begin,end,bill,amount):
    """ Extract the dates of the bills, date of bill and period of consumption. There are several formats of the data over the years. 
    In the newer ones the regex expressions work well, however in the older ones the extraction is done manually """
    #First find all dates in the text
    match=re.findall(r"\d{2}/\d{2}/\d{4}",text)
    dts=[]
    for dt in match:
        date_time_obj = datetime.strptime(dt,'%d/%m/%Y')
        dts.append(date_time_obj.date())

    #Older bills dont have these patterns while the new ones do
    regex_date_publish = re.compile(r'(Έκδοσης)\n(\d{2}/\d{2}/\d{4})')
    regex_date_publish_2 = re.compile(r'(\d{10})\s*-\s*(\d{2}/\d{2}/\d{4})')
    
    match = regex_date_publish.search(text)
    match_2 = regex_date_publish_2.search(text)
    dt=''
    dt_d = datetime.strptime('01/01/2000','%d/%m/%Y')
    if match: #New bill
        #word = match.group(1)
        dt=match.group(2)
        dt_d = datetime.strptime(dt,'%d/%m/%Y')
        bill.append(dt_d.date())

    elif match_2: #Older bills
        dt=match_2.group(2)
        dt_d = datetime.strptime(dt,'%d/%m/%Y')
        bill.append(dt_d.date())       

    #Consumption period
    regex_date_period = re.compile(r'(Κατανάλωσης)\n(\d{2}/\d{2}/\d{4})\s+-\s+(\d{2}/\d{2}/\d{4})')
    regex_date_period_2 = re.compile(r'\n(\d{2}/\d{2}/\d{4})\s+-\s+(\d{2}/\d{2}/\d{4})\n')
    match = regex_date_period.search(text)
    match_2 = regex_date_period_2.search(text)

    if match: #New format seen in bills
        title = match.group(1)
        start_date = match.group(2)
        end_date= match.group(3)
        
        start_date=datetime.strptime(start_date,'%d/%m/%Y')
        end_date=datetime.strptime(end_date,'%d/%m/%Y')
        
        begin.append( start_date.date())
        end.append(end_date.date())
        
        #print(f"Title: {title}\nStart Date: {start_date}\nEnd Date: {end_date}")
    elif match_2: #Second format seen in bills
        start_date = match_2.group(1)
        end_date= match_2.group(2)
        start_date=datetime.strptime(start_date,'%d/%m/%Y')
        end_date=datetime.strptime(end_date,'%d/%m/%Y')
        
        begin.append( start_date.date())
        end.append(end_date.date())     

    else: #Find start and end date based on the date of the bill
        check_date=datetime.strptime('01/12/2020','%d/%m/%Y')
        #The format of the bill changes at the end of the 2020.
        if dt_d<check_date:
            print(dts)
            begin.append(dts[1])
            end.append(dts[2])
        else:
            begin.append(dts[2])
            #If there is a refund, then the number of the period end moves up since there is no due date.
            if amount[-1]==0:
                end.append(dts[4])
            else:
                end.append(dts[5])           

    return begin,end,bill

def fix_delimiter(consmp):
    """Fix point delimiter considered as thousand in new bills """
    for month in consmp:
        try:
            #Check if consumption has a point delimiter that denotes thousand instead of decimal
            check=str(month).split(".")
            if check[1]>check[0]: #It is going to have at least 3 values after the point that denotes thousands
                number = str(month).replace(".", "")  # Remove the point
                consmp[consmp.index(month)] = float(number)  # Convert the result back to float
        except:
            pass
    return consmp

def graphs_per_quarter(dataframe):
    """Graphs of price and consumption per quarter  """

    # group data by year and quarter
    grouped = dataframe.groupby(['year','quarter']).sum()

    # reshape data into a pivot table
    pivot = grouped.pivot_table(index='quarter', columns='year', values='Bill', aggfunc=np.sum)
    pivot_c = grouped.pivot_table(index='quarter', columns='year', values='Consumption', aggfunc=np.sum)
    
    # create the bar chart
    ax = pivot.plot(kind='bar', figsize=(15,6))
    ax_c = pivot_c.plot(kind='bar', figsize=(15,6))

    # set the x-axis label and tick labels
    ax.set_xlabel('Quarter')
    ax.set_xticklabels(pivot.index, rotation=0)
    ax_c.set_xlabel('Quarter')
    ax_c.set_xticklabels(pivot.index, rotation=0)

    # set the y-axis label
    ax.set_ylabel('Bill [Euro]')
    ax_c.set_ylabel('Consumption [kWh]')

    # set the legend
    ax.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax_c.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')

    #set title
    ax.set_title('Bill comparison by quarter ', fontsize=16)
    ax_c.set_title('Consumption Comparison by quarter', fontsize=16)

def graphs_per_year(dataframe):
    """Graphs of price and consumption per year"""

    #Results for each a year
    df_year=dataframe.groupby(pd.to_datetime(dataframe['Date_bill']).dt.year).sum()

    # Create a figure with two subplots side by side
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))

    # Plot the first bar figure in the left subplot
    axs[0].bar(df_year.index, df_year['Bill'])
    axs[0].set_title('Bill')
    axs[0].set_ylabel('[EURO]')
    axs[0].set_xlabel('Year')
    # Plot the second bar figure in the right subplot
    axs[1].bar(df_year.index, df_year['Consumption'])
    axs[1].set_title('Consumption')
    axs[1].set_ylabel('[kWh]')
    axs[1].set_xlabel('Year')
    # Add a title to the overall figure
    fig.suptitle('Comparison by year', fontsize=16)

def main():
    """ Main entry point for the script """
    #Memory allocations
    monthly_pay=[]
    consumption=[]
    begin_consumption=[]
    end_consumption=[]
    date_bill=[]
    
    #Specify the path of the folder to look the PDFs of the bills. '.' is where the script is stored.
    initial_folder='bills'
    pdf_files=find_all_files(initial_folder)

    #Check that there are pdf files inside the folder
    if pdf_files==True:
        print('There are no bills in the folder! Exiting script!')
        sys.exit()

    #Extract the info that we want from PDF files: consumption, euros and dates
    pdf_text=pdf_extraction(pdf_files)
    #Iterate over the extracted PDF text.
    for f in pdf_text:
        #First, find what do we pay each month.
        find_amount(f,monthly_pay)
        #Next, find the dates of consumption and the bill's date.
        find_date(f,begin_consumption,end_consumption,date_bill,monthly_pay)
        #Finally, find the consumption of kWh.
        find_consumption(f,consumption)

    fix_delimiter(consumption)

    # Calling DataFrame constructor after zipping both lists, with columns specified
    df = pd.DataFrame(list(zip(date_bill,begin_consumption, end_consumption,consumption,monthly_pay,pdf_files)),
                columns =['Date_bill','Start', 'End','Consumption','Bill','Pdf_file'])
    # forming dataframe
    data = pd.DataFrame(df)
    #Adding year and quarter periods
    df['quarter'] = pd.to_datetime(df['Date_bill']).dt.quarter
    df['year'] = pd.to_datetime(df['Date_bill']).dt.year
    # storing into the excel file
    data.to_excel("output.xlsx")
    #Plot data
    graphs_per_quarter(df)
    graphs_per_year(df)
    #Display the data
    plt.show()

if __name__=='__main__':
    sys.exit(main())