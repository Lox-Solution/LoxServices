from typing import List, Tuple

import pandas as pd
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfparser import PDFParser
from tabula import convert_into, read_pdf


def convertListOfInchesToListOfPdfUnits(list_of_inches: List[float]) -> List[float]:
    """Get a list of inches and return a list of PDF units (72 units per inch)

    ## Arguments
        - `list_of_inches`: List of floats

    ## Example
        >>> inchesToPDFUnits([1,1.5,2])

    ## Returns
    - A list of floats in PDF units
    """
    return list(map(lambda element: round(element * 72, 2), list_of_inches))


def countNumberOfPagesOfPdf(path_to_pdf_file: str) -> int:
    """Returns the number of pages of a PDF file

    ## Arguments
        - `path_to_pdf_file`: The location of the PDF file

    ## Example
        >>> path_to_pdf_file("/Users/me/Downloads/XXXXX.pdf")

    ## Returns
    - The number of pages of the PDF file
    """
    with open(path_to_pdf_file, "rb") as file:
        parser = PDFParser(file)
        document = PDFDocument(parser)
        return resolve1(document.catalog["Pages"])["Count"]


def inchesToPDFUnits(tupleOfInches: Tuple[float]) -> Tuple[float]:
    """Get a tuple of inches and return a tuple of PDF units (72 units per inch)

    ## Arguments
        - `tupleOfInches`: Tuple of floats

    ## Example
        >>> inchesToPDFUnits((1,1.5,2))

    ## Returns
    - A tuple of floats in PDF units

    """
    list_of_inches = []
    for inche in tupleOfInches:
        list_of_inches.append(round(inche * 72, 2))
    return tuple(list_of_inches)


def PDFtoCSV(
    path_to_pdf: str,
    first_page_to_read: int,
    area: List[str],
    columns: List[str],
    guess: bool,
) -> str:
    """Converts a PDF file to a CSV file and save it in the same folder as the PDF file

    ## Arguments
        - `path_to_pdf`: The location of the PDF file
        - `first_page_to_read`: The first page to take into account
        - `area`: Array borders in a list:[top, left, bottom ,right] - can be left [] if the full PDF is needed
        - `columns`: Column distances in a list of floats - can be left [] if the full PDF is needed
        - `guess`: True if the script guesses the columns

    ## Returns
    - The CSV file created from the PDF
    """
    last_page = countNumberOfPagesOfPdf(path_to_pdf)

    # Convert the arrays to CSV files
    convert_into(
        path_to_pdf,
        output_path=path_to_pdf.replace(".pdf", ".csv"),
        pages=str(first_page_to_read) + "-" + str(last_page),
        area=area,
        columns=columns,
        guess=guess,
    )

    pathCSV = path_to_pdf.replace(".pdf", ".csv")
    return pathCSV


def PDFtoDf(
    path_to_pdf: str,
    first_page_to_read: int,
    last_page_to_read: int,
    area: List[str],
    columns: List[str],
    guess: bool,
) -> List[pd.DataFrame]:
    """Converts a PDF file to a dataframe and returns it

    ## Arguments
        - `path_to_pdf`: The location of the PDF file
        - `first_page_to_read`: The first page to take into account
        - `last_page_to_read`: The last page to take into account
        - `area`: Array borders in a list:[top, left, bottom ,right] - can be left [] if the full PDF is needed
        - `columns`: Column distances in a list of floats - can be left [] if the full PDF is needed
        - `guess`: True if the script guesses the columns

    ## Example
        >>> PDFtoDf("/Users/me/Downloads/XXXXX.pdf")

    ## Returns
    - A list of DataFrames or dict containing the PDF information
    """
    if last_page_to_read is None:
        last_page_to_read = countNumberOfPagesOfPdf(path_to_pdf)

    columns = convertListOfInchesToListOfPdfUnits(columns)
    area = convertListOfInchesToListOfPdfUnits(area)
    if guess:
        pandas_options = {"dtype": str}
    else:
        pandas_options = {"dtype": str, "header": None}

    # Read the array in the top right corner.
    df = read_pdf(
        path_to_pdf,
        pages=str(first_page_to_read) + "-" + str(last_page_to_read),
        area=area,
        columns=columns,
        guess=guess,
        pandas_options=pandas_options,
    )
    return df


def is_word_in_pdf(
    pdf_path: str, first_page_to_read: int, last_page_to_read: int, text_to_search: str
) -> bool:
    """Returns True if the text_to_search is found in the pdf file, False otherwise

    ##Arguments:
    - `pdf_path`: path to the pdf file
    - `first_page_to_read`: first page to read for the search
    - `last_page_to_read`: last page to read for the search
    - `text_to_search`: text to search in the pdf file

    """

    df = PDFtoDf(pdf_path, first_page_to_read, last_page_to_read, [], [], False)[0]

    for column in df.columns:
        if df[column].str.contains(text_to_search).any():
            return True
        return False
