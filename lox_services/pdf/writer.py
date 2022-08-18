"""
All functions and configurations to write all sorts of pdfs.
"""
import re
import os
import pandas as pd
from weasyprint import HTML, CSS

from lox_services.config.paths import ASSETS_FOLDER
from lox_services.utils.general_python import print_success


def dataframe_to_html_without_pandas_style(dataframe: pd.DataFrame) -> str:
    """Applies the `.to_html()` pandas function and removes the additional style on the table element."""
    #Needed because pandas did not fix the open PR
    return re.sub( 
        r'<tr.*>', '<tr>', 
        dataframe.to_html(index=False)
            .replace('border="1" ', '')
    )

def generate_pdf_file_from_dataframe(dataframe: pd.DataFrame, path_to_pdf:str, indexes: bool=False):
    """Generates a pdf from a dataframe.
        ## Arguments:
        - `dataframe`: DataFrame to use for generating the pdf (can be a Series).
        - `path_to_pdf`: The absolute path where the pdf should be saved.
        - `indexes`: Boolean that controls wheter or not the pdf should contain row indexes.
        
        ## Example:
            >>> generate_pdf_file_from_dataframe(my_df) #/home/whatever.pdf
        
        ## Returns:
        - Nothing
        - Raises an exception if there was a problem.
    """
    
    if isinstance(dataframe, pd.Series):
        print("The given parameter is a Series, converting to DataFrame...")
        dataframe = dataframe.to_frame()
    
    html_string = dataframe_to_html_without_pandas_style(dataframe)
    html = HTML(string=html_string)
    css = CSS(os.path.join(ASSETS_FOLDER, "pdf_tables.css"))
    
    html.write_pdf(
        path_to_pdf,
        stylesheets=[css],
    )
    print_success("Pdf created successfuly.")

def generate_pdf_file_from_html_css(base_url:str, html_string: str, path_to_css: str, path_to_pdf):
    """Generates a pdf from a html file and a css file.
        ## Arguments:
        - `base_url`: The path to the folder containing the assets (images, css ...).
        - `html_string`: The string representation of the html to use for pdf generation.
        - `path_to_css`: The path of the css to use for pdf generation.
        - `path_to_pdf`: The absolute path where the pdf should be saved.
        
        ## Example:
            >>> generate_pdf_file_from_html_css(
                lox_invoices,
                html_template,
                lox_invoices+"/style.css",
                os.path.join(ROOT_PATH,"output_folder","Ztests","invoice_test.pdf")
            )
        
        ## Returns:
        Nothing
    """
    html = HTML(string=html_string, base_url=base_url)
    css = CSS(path_to_css)
    html.write_pdf(
        path_to_pdf,
        stylesheets=[css],
    )
    print_success("Pdf created successfuly.")

