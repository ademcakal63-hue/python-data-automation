from fpdf import FPDF
pdf = FPDF(); pdf.add_page(); pdf.set_font("Helvetica", size=12)
lines = [
 "ACME Auto Parts Ltd.",
 "Invoice Number: INV-2026-00842",
 "Date: 2026-06-15",
 "Due Date: 2026-07-15",
 "Bill To: Adem Cakal",
 "",
 "Description        Qty   Unit Price   Amount",
 "Brake pads          2      45.00        90.00",
 "Oil filter          1      20.00        20.00",
 "",
 "Subtotal: 110.00",
 "Tax (VAT 20%): 22.00",
 "Total: 132.00 USD",
]
for l in lines:
    pdf.cell(0, 8, l, new_x="LMARGIN", new_y="NEXT")
pdf.output("sample_invoice.pdf")
print("created sample_invoice.pdf")
