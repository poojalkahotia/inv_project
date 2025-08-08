from .base_pdf import BasePDF
from fpdf import FPDF

class PartyBalancePDF(BasePDF):
    def __init__(self):
        super().__init__()
        self.title = "All Party Balance Report"

class ItemBalancePDF(BasePDF):
    def __init__(self):
        super().__init__(title="All Item Balance Report")
        
class PartyStatementPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Party Statement", ln=1, align="C")
        self.ln(5)

    def render_statement(self, partyname, data, total_balance):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Party: {partyname}", ln=1)
        self.ln(3)

        headers = ["Date", "Type", "Ref", "Debit", "Credit", "Remarks"]
        col_widths = [25, 30, 30, 25, 25, 55]
        self.set_font("Arial", "B", 10)
        for i in range(len(headers)):
            self.cell(col_widths[i], 8, headers[i], border=1)
        self.ln()

        self.set_font("Arial", "", 10)
        for row in data:
            self.cell(col_widths[0], 8, row["date"].strftime("%Y-%m-%d") if row["date"] else "", border=1)
            self.cell(col_widths[1], 8, row["type"], border=1)
            self.cell(col_widths[2], 8, str(row["ref"]), border=1)
            self.cell(col_widths[3], 8, f"{row['debit']:.2f}" if row["debit"] else "", border=1)
            self.cell(col_widths[4], 8, f"{row['credit']:.2f}" if row["credit"] else "", border=1)
            self.cell(col_widths[5], 8, str(row["remarks"]), border=1)
            self.ln()

        # Total
        self.ln(2)
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, f"Total Balance: Rs.{total_balance:.2f}", ln=1) 
        
class PurchaseReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Purchase Report", border=0, ln=1, align="C")

    def render_purchase_report(self, purchases, total_amount, from_date, to_date, partyname):
        self.set_font("Helvetica", size=10)
        self.ln(5)

        # Filters summary
        self.cell(0, 8, f"From: {from_date}  To: {to_date}", ln=1)
        self.cell(0, 8, f"Party: {partyname or 'All Parties'}", ln=1)

        # Table
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(200,200,200)
        self.cell(30, 8, "Inv No", border=1, fill=True)
        self.cell(30, 8, "Date", border=1, fill=True)
        self.cell(50, 8, "Party", border=1, fill=True)
        self.cell(30, 8, "Amount", border=1, fill=True)
        self.cell(50, 8, "Remarks", border=1, fill=True)
        self.ln()

        self.set_font("Helvetica", size=10)
        for p in purchases:
            self.cell(30, 8, str(p.invno), border=1)
            self.cell(30, 8, p.invdate.strftime("%Y-%m-%d"), border=1)
            self.cell(50, 8, str(p.partyname), border=1)
            self.cell(30, 8, f"{p.amount:.2f}", border=1, align="R")
            self.cell(50, 8, str(p.remark or ""), border=1)
            self.ln()

        self.set_font("Helvetica", "B", 10)
        self.cell(140, 8, "Total", border=1, align="R")
        self.cell(30, 8, f"{total_amount:.2f}", border=1, align="R")
        self.cell(50, 8, "", border=1)
        
class SaleReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Sales Report", border=False, ln=True, align="C")
        self.ln(5)

        self.set_font("Helvetica", "B", 10)
        self.cell(30, 8, "Invoice No", border=1)
        self.cell(30, 8, "Sale Date", border=1)
        self.cell(50, 8, "Party Name", border=1)
        self.cell(30, 8, "Amount", border=1, align="R")
        self.cell(50, 8, "Remarks", border=1)
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def sales_table(self, sales):
        self.set_font("Helvetica", "", 10)
        for s in sales:
            self.cell(30, 8, str(s.invno), border=1)
            self.cell(30, 8, s.invdate.strftime("%Y-%m-%d"), border=1)
            self.cell(50, 8, str(s.partyname), border=1)
            self.cell(30, 8, f"Rs. {s.amount:.2f}", border=1, align="R")
            self.cell(50, 8, str(s.remark or ""), border=1)
            self.ln()

class ReceiptReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Receipt Report", border=False, ln=True, align="C")
        self.ln(5)

        self.set_font("Helvetica", "B", 10)
        self.cell(30, 8, "Receipt No", border=1)
        self.cell(30, 8, "Entry Date", border=1)
        self.cell(50, 8, "Party Name", border=1)
        self.cell(30, 8, "Amount", border=1, align="R")
        self.cell(50, 8, "Remarks", border=1)
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def receipts_table(self, receipts):
        self.set_font("Helvetica", "", 10)
        for r in receipts:
            self.cell(30, 8, str(r.entryno), border=1)
            self.cell(30, 8, r.entrydate.strftime("%Y-%m-%d"), border=1)
            self.cell(50, 8, str(r.partyname), border=1)
            self.cell(30, 8, f"{r.amount:.2f}", border=1, align="R")
            self.cell(50, 8, str(r.remark or ""), border=1)
            self.ln()

class PaymentReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Payment Report", border=False, ln=True, align="C")
        self.ln(5)

        self.set_font("Helvetica", "B", 10)
        self.cell(30, 8, "Payment No", border=1)
        self.cell(30, 8, "Entry Date", border=1)
        self.cell(50, 8, "Party Name", border=1)
        self.cell(30, 8, "Amount", border=1, align="R")
        self.cell(50, 8, "Remarks", border=1)
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def payments_table(self, payments):
        self.set_font("Helvetica", "", 10)
        for p in payments:
            self.cell(30, 8, str(p.entryno), border=1)
            self.cell(30, 8, p.entrydate.strftime("%Y-%m-%d"), border=1)
            self.cell(50, 8, str(p.partyname), border=1)
            self.cell(30, 8, f"{p.amount:.2f}", border=1, align="R")
            self.cell(50, 8, str(p.remark or ""), border=1)
            self.ln()
                      