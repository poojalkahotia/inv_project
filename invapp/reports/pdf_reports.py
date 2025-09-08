from fpdf import FPDF
from invapp.models import HeadCompanyinfo

class SaleReportPDF(FPDF):
    def __init__(self, sale, details, company=None):
        super().__init__()
        self.sale = sale
        self.details = details
        self.company = company

    # ---------- HEADER ----------
    def header(self):
        company = HeadCompanyinfo.objects.first()

        # Company Info (Top Center)
        # Company Info (Top Center)
        if company:
            self.set_font("Arial", "B", 14)
            self.cell(0, 8, company.companyname, ln=1, align="C")

            self.set_font("Arial", "", 10)
            self.cell(0, 6, company.add1, ln=1, align="C")  # Sirf address line
            self.cell(0, 6, f"{company.city}, {company.state}", ln=1, align="C")  # City + State next line
            self.cell(0, 6, f"Mobile: {company.mobile}", ln=1, align="C")
            self.ln(5)

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
        self.set_xy(120, 40)  # ✅ Fixed position so it does not overlap
        self.set_font("Arial", "B", 10)
        self.cell(70, 6, f"Invoice No: {self.sale.invno}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Date: {self.sale.invdate.strftime('%d-%m-%Y')}", ln=1, align="R")

        self.ln(15)  # ✅ Extra spacing before table starts


    # ---------- TABLE ----------
    def sales_table(self):
         # Ensure table starts thoda neeche (after party info + invoice box)
        if self.get_y() < 80:   # check kar rahe ki abhi cursor upar hai
            self.set_y(80)
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
        self.set_y(-60)
        self.set_font("Arial", "I", 9)
        self.multi_cell(
            100, 6,
            f"Remark: {self.sale.remark or ''}\n"
            f"Amount in Words: {self.sale.amtinwords or ''}"
        )

        self.set_xy(120, -50)
        self.set_font("Arial", "B", 10)
        self.cell(70, 6, f"Total: {self.sale.amount:.2f}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Adjustment: {self.sale.adjustment:.2f}", ln=1, align="R")
        self.set_x(120)
        self.cell(70, 6, f"Net Amount: {self.sale.netamt:.2f}", ln=1, align="R")