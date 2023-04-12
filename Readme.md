# Electric Bill Data Extraction and Analysis
This Python script is designed to help users calculate the sums of consumption [kWh] and amount [Euro] provided by electric bills in PDF form from the public power company® in Greece. It automates the process of extracting data from PDFs and processing it to analyze the data from the electric bills, the consumption and the amount to pay.

## Getting Started
To get started with this script, the user will need to have Python 3 installed on your system. Python is downloaded from the official website: https://www.python.org/downloads/.

The user will also need to install the required Python packages. This can be done by running the following command in the terminal:

`pip install -r requirements.txt`

Once the required packages are installed, the script is executed by using the following command:

`python electric_bill_data.py`

## Usage
To use this script, the user will need to have the electric bill PDFs saved on the system. It is best to copy them into the bills folder which is located in the same folder as the script. Otherwise, the user may specify the complete path in the variable "initial_folder" inside the script. 

Once the PDFs are copied or the path is specified, then the script can be executed. The script will extract the data from the PDFs and calculate the quarter and year sums from the electric bills.  Next, the quarter and year results for the consumption and the amount to pay are presented in a graphical form to visualize the data. In addition, the results, from the PDF extraction, are saved in xlsx format for manipulating the data with a spreadsheet program.

It is noted that when the consumption is not written in the bill, it is considered as zero in the program. Similarly, when there is a refund, the amount to pay is zero. 

## Contributing
If you would like to contribute to this project, please feel free to submit a pull request. All contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.
