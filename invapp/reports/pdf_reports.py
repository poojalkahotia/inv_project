from fpdf import FPDF

class SaleReportPDF(FPDF):
    def __init__(self, sale, details):
        super().__init__()
        self.sale = sale
        self.details = details

    # ---------- HEADER ----------
    def header(self):
        # LEFT -> Party Info
        self.set_font("Arial", "", 10)
        self.multi_cell(
            90, 6,
            f"{self.sale.partyname}\n"
            f"{self.sale.add1 or ''}\n"
            f"{self.sale.city or ''}\n"
            f"Mobile: {self.sale.mobileno}\n"
            f"Email: {self.sale.email or ''}",
            border=0
        )

        # RIGHT -> Invoice Info
        self.set_xy(120, 20)  # Move cursor right side
        self.set_font("Arial", "B", 10)
        self.cell(70, 6, f"Invoice No: {self.sale.invno}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Date: {self.sale.invdate.strftime('%d-%m-%Y')}", ln=1, align="R")

        self.ln(10)  # spacing

    # ---------- TABLE ----------
    def sales_table(self):
        self.set_font("Arial", "B", 10)
        self.cell(70, 8, "Item", 1, 0, "C")
        self.cell(30, 8, "Qty", 1, 0, "C")
        self.cell(40, 8, "Rate", 1, 0, "C")
        self.cell(40, 8, "Amount", 1, 1, "C")

        self.set_font("Arial", "", 10)
        for d in self.details:
            self.cell(70, 8, d.itemname, 1, 0, "L")
            self.cell(30, 8, str(d.itemqty), 1, 0, "C")
            self.cell(40, 8, f"{d.itemrate:.2f}", 1, 0, "R")
            self.cell(40, 8, f"{d.itemamt:.2f}", 1, 1, "R")

    # ---------- FOOTER ----------
    def footer(self):
        self.set_y(-60)  # Move to near bottom

        # LEFT -> Remark & Amt in words
        self.set_font("Arial", "I", 9)
        self.multi_cell(
            100, 6,
            f"Remark: {self.sale.remark or ''}\n"
            f"Amount in Words: {self.sale.amtinwords or ''}"
        )

        # RIGHT -> Totals
        self.set_xy(120, -50)
        self.set_font("Arial", "B", 10)
        self.cell(70, 6, f"Total: {self.sale.amount:.2f}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Adjustment: {self.sale.adjustment:.2f}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Net Amount: {self.sale.netamt:.2f}", ln=1, align="R")
