from typing import List

import pandas as pd
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfparser import PDFParser
from tabula import convert_into, read_pdf


def convertListOfInchesToListOfPdfUnits(list_of_inches):
    return list(map(lambda element : round(element*72,2),list_of_inches))


def countNumberOfPagesOfPdf(path_to_pdf_file: str) -> int:
    with open(path_to_pdf_file, 'rb') as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)
        return resolve1(document.catalog['Pages'])['Count']


def inchesToPDFUnits(tupleOfInches):
    list_of_inches = []
    for inche in tupleOfInches:
        list_of_inches.append(round(inche*72, 2))
    return tuple(list_of_inches)


def PDFtoCSV(path_to_pdf: str, first_page_to_read, area, columns, guess):
    last_page = countNumberOfPagesOfPdf(path_to_pdf)
    
    # Convert the arrays to CSV files
    convert_into(
        path_to_pdf,
        output_path=path_to_pdf.replace('.pdf', '.csv'),
        pages=str(first_page_to_read) + '-' + str(last_page),
        # Array borders: top, left, bottom and right
        area = area,
        # Columns distances
        columns = columns,
        # Let the script guess the columns
        guess=guess
    )
    
    pathCSV = path_to_pdf.replace('.pdf', '.csv')
    return pathCSV


def PDFtoDf(path_to_pdf: str, first_page_to_read, last_page_to_read, area, columns, guess) -> List[pd.DataFrame]:
    if last_page_to_read is None:
        last_page_to_read = countNumberOfPagesOfPdf(path_to_pdf)
    
    columns = convertListOfInchesToListOfPdfUnits(columns)
    area = convertListOfInchesToListOfPdfUnits(area)
    if guess :
        pandas_options = {'dtype': str}
    else:
        pandas_options = {'dtype': str, 'header': None}
    
    # Read the array in the top right corner.
    df = read_pdf(
        path_to_pdf,
        pages= str(first_page_to_read)+'-'+str(last_page_to_read),
        # Array borders: top, left, bottom and right
        area = area,
        # Columns distances
        columns = columns,
        # Let the script guess the columns
        guess=guess,
        pandas_options=pandas_options
    )
    return df
