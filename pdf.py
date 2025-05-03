from fpdf import FPDF

# Це — текст відповіді GPT
text = """
INSURANCE POLICY No. POL-983245

Issued on: May 3, 2025

Policyholder: Ivan Ivanov
Vehicle License Plate: AA1234BC

Insured Amount: 100 USD
Coverage Period: May 3, 2025 - May 3, 2026

This insurance policy provides basic coverage for the insured vehicle, including protection against theft, accidental damage, and third-party liability. The policy is valid for the period stated above and subject to the terms and conditions of the insurer.

Thank you for choosing our insurance services.
"""

# Генерація PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
for line in text.strip().split('\n'):
    pdf.multi_cell(0, 10, line)
pdf.output("insurance_policy.pdf")
