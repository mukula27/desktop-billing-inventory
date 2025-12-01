"""
PDF Generator - Generate invoices and reports as PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import os


class PDFGenerator:
    def __init__(self, company_settings: dict):
        self.company_settings = company_settings
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyDetails',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_RIGHT
        ))
    
    def generate_invoice_pdf(self, invoice_data: dict, items: list, output_path: str) -> bool:
        """Generate invoice PDF"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=0.5*inch, leftMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            story = []
            
            # Company Header
            if self.company_settings.get('logo_path') and os.path.exists(self.company_settings['logo_path']):
                logo = Image(self.company_settings['logo_path'], width=1*inch, height=1*inch)
                story.append(logo)
                story.append(Spacer(1, 0.1*inch))
            
            company_name = Paragraph(self.company_settings.get('company_name', 'My Business'), 
                                    self.styles['CompanyName'])
            story.append(company_name)
            
            company_details = f"{self.company_settings.get('address', '')}<br/>"
            company_details += f"Phone: {self.company_settings.get('phone', '')} | "
            company_details += f"Email: {self.company_settings.get('email', '')}<br/>"
            if self.company_settings.get('gstin'):
                company_details += f"GSTIN: {self.company_settings['gstin']}"
            
            story.append(Paragraph(company_details, self.styles['CompanyDetails']))
            story.append(Spacer(1, 0.3*inch))
            
            # Invoice Title
            invoice_title = Paragraph(f"<b>TAX INVOICE</b>", self.styles['InvoiceTitle'])
            story.append(invoice_title)
            story.append(Spacer(1, 0.2*inch))
            
            # Invoice Details Table
            invoice_info_data = [
                ['Invoice No:', invoice_data['invoice_number'], 'Date:', invoice_data['invoice_date']],
                ['Time:', invoice_data['invoice_time'], 'Status:', invoice_data['payment_status'].upper()]
            ]
            
            invoice_info_table = Table(invoice_info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
            invoice_info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(invoice_info_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Customer Details
            story.append(Paragraph('<b>Bill To:</b>', self.styles['SectionHeader']))
            customer_details = f"<b>{invoice_data['customer_name']}</b><br/>"
            if invoice_data.get('customer_phone'):
                customer_details += f"Phone: {invoice_data['customer_phone']}<br/>"
            if invoice_data.get('customer_address'):
                customer_details += f"{invoice_data['customer_address']}"
            
            story.append(Paragraph(customer_details, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Items Table
            items_data = [['#', 'Product', 'Qty', 'Unit', 'Price', 'Disc%', 'GST%', 'Amount']]
            
            for idx, item in enumerate(items, 1):
                items_data.append([
                    str(idx),
                    f"{item['product_name']}\n({item['product_code']})",
                    f"{item['quantity']:.2f}",
                    item['unit'],
                    f"₹{item['unit_price']:.2f}",
                    f"{item.get('discount_percent', 0):.1f}%",
                    f"{item.get('gst_rate', 0):.1f}%",
                    f"₹{item['total_amount']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[0.4*inch, 2.5*inch, 0.7*inch, 0.6*inch, 
                                                       1*inch, 0.7*inch, 0.7*inch, 1.2*inch])
            
            items_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Body
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Totals Table
            totals_data = [
                ['Subtotal:', f"₹{invoice_data['subtotal']:.2f}"],
            ]
            
            if invoice_data.get('discount_amount', 0) > 0:
                discount_text = f"Discount ({invoice_data.get('discount_percent', 0):.1f}%):"
                totals_data.append([discount_text, f"- ₹{invoice_data['discount_amount']:.2f}"])
            
            if invoice_data.get('tax_amount', 0) > 0:
                totals_data.append(['Tax (GST):', f"₹{invoice_data['tax_amount']:.2f}"])
            
            totals_data.append(['<b>Grand Total:</b>', f"<b>₹{invoice_data['grand_total']:.2f}</b>"])
            totals_data.append(['<b>Rounded Total:</b>', f"<b>₹{invoice_data['rounded_total']:.2f}</b>"])
            
            if invoice_data.get('amount_paid', 0) > 0:
                totals_data.append(['Amount Paid:', f"₹{invoice_data['amount_paid']:.2f}"])
                totals_data.append(['<b>Balance Due:</b>', f"<b>₹{invoice_data['balance_amount']:.2f}</b>"])
            
            totals_table = Table(totals_data, colWidths=[5*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
                ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#34495e')),
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#34495e')),
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Notes
            if invoice_data.get('notes'):
                story.append(Paragraph('<b>Notes:</b>', self.styles['SectionHeader']))
                story.append(Paragraph(invoice_data['notes'], self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Footer
            story.append(Spacer(1, 0.3*inch))
            footer_text = "Thank you for your business!"
            story.append(Paragraph(footer_text, self.styles['CompanyDetails']))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def generate_customer_ledger_pdf(self, customer: dict, ledger_data: dict, output_path: str) -> bool:
        """Generate customer ledger PDF"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=0.5*inch, leftMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            story = []
            
            # Header
            title = Paragraph(f"<b>Customer Ledger Report</b>", self.styles['InvoiceTitle'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Customer Details
            customer_info = f"<b>Customer:</b> {customer['customer_name']}<br/>"
            if customer.get('phone'):
                customer_info += f"<b>Phone:</b> {customer['phone']}<br/>"
            if customer.get('address'):
                customer_info += f"<b>Address:</b> {customer['address']}"
            
            story.append(Paragraph(customer_info, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Summary
            summary_data = [
                ['Total Purchases:', f"₹{ledger_data['total_purchases']:.2f}"],
                ['Total Paid:', f"₹{ledger_data['total_paid']:.2f}"],
                ['<b>Total Due:</b>', f"<b>₹{ledger_data['total_due']:.2f}</b>"]
            ]
            
            summary_table = Table(summary_data, colWidths=[5*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Invoices Table
            if ledger_data['invoices']:
                story.append(Paragraph('<b>Invoice History:</b>', self.styles['SectionHeader']))
                
                invoice_data = [['Date', 'Invoice No', 'Amount', 'Paid', 'Balance', 'Status']]
                
                for inv in ledger_data['invoices']:
                    invoice_data.append([
                        inv['invoice_date'],
                        inv['invoice_number'],
                        f"₹{inv['grand_total']:.2f}",
                        f"₹{inv['amount_paid']:.2f}",
                        f"₹{inv['balance_amount']:.2f}",
                        inv['payment_status'].upper()
                    ])
                
                invoice_table = Table(invoice_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 
                                                               1.2*inch, 1.2*inch, 1*inch])
                
                invoice_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                ]))
                
                story.append(invoice_table)
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating ledger PDF: {e}")
            return False
    
    def generate_stock_report_pdf(self, products: list, output_path: str, report_type: str = "all") -> bool:
        """Generate stock report PDF"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=0.5*inch, leftMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            story = []
            
            # Header
            title_text = "Low Stock Report" if report_type == "low" else "Stock Report"
            title = Paragraph(f"<b>{title_text}</b>", self.styles['InvoiceTitle'])
            story.append(title)
            
            date_text = f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
            story.append(Paragraph(date_text, self.styles['CompanyDetails']))
            story.append(Spacer(1, 0.3*inch))
            
            # Products Table
            product_data = [['Code', 'Product Name', 'Category', 'Current Stock', 'Min Level', 'Unit']]
            
            for product in products:
                product_data.append([
                    product['product_code'],
                    product['product_name'],
                    product.get('category_name', '-'),
                    f"{product['current_stock']:.2f}",
                    f"{product['min_stock_level']:.2f}",
                    product['unit']
                ])
            
            product_table = Table(product_data, colWidths=[1*inch, 2.5*inch, 1.2*inch, 
                                                          1*inch, 1*inch, 0.8*inch])
            
            product_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(product_table)
            
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error generating stock report PDF: {e}")
            return False
