import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path
import os


def generate(invoices_path, pdfs_path, image_path, product_id, product_name,
             amount_purchased, price_per_unit, total_price):
    """
    This function converts excel invoice file into PDF invoices.
    :param invoices_path:
    :param pdfs_path:
    :param image_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :return:
    """
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")
    print(filepaths)

    for filepath in filepaths:

        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()

        filename = Path(filepath).stem

        # Extract Invoice# and Invoice Date
        invoice_nr, invoice_date = filename.split("-")

        pdf.set_font(family="Times", size=16, style="B")

        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_nr}", ln=1)
        pdf.cell(w=50, h=8, txt=f"Date {invoice_date}", ln=1)

        df = pd.read_excel(filepath, sheet_name="Sheet 1")

        # List Comprehension. df.columns is iterable just like list.
        column_names = [item.replace("_", " ").title() for item in df.columns]
        print(column_names)

        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=30, h=8, txt=column_names[0], border=1)
        pdf.cell(w=70, h=8, txt=column_names[1], border=1)
        pdf.cell(w=40, h=8, txt=column_names[2], border=1)
        pdf.cell(w=25, h=8, txt=column_names[3], border=1)
        pdf.cell(w=25, h=8, txt=column_names[4], border=1, ln=1)

        total = df[total_price].sum()
        # Creates the PGF Table
        for index, row in df.iterrows():
            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(80, 80, 80)

            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=row[product_name], border=1)
            pdf.cell(w=40, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=25, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=25, h=8, txt=str(row[total_price]), border=1, ln=1)

        pdf.cell(w=30, h=8, txt="Total", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=40, h=8, txt="", border=1)
        pdf.cell(w=25, h=8, txt="", border=1)
        pdf.cell(w=25, h=8, txt=str(total), border=1, ln=1)

        # Add total sum sentence
        pdf.set_font(family="Times", size=10, style="B")
        pdf.cell(w=30, h=8, txt=f"The total price in {total}", ln=1)

        # Add company name and logo
        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=25, h=8, txt=f"PythonHow")
        pdf.image(image_path, w=10)

        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)

        pdf.output(f"{pdfs_path}/{filename}.pdf")

