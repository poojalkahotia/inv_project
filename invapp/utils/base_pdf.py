# invapp/utils/base_pdf.py
from fpdf import FPDF

class BasePDF(FPDF):
    def __init__(self, title=""):
        super().__init__()
        self.title = title

    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_table(self, data, col_widths, headers):
        self.set_font("Arial", "B", 10)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()

        self.set_font("Arial", "", 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), 1, 0, 'R')
            self.ln()
