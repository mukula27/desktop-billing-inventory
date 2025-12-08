"""
Enhanced PDF Price Extractor - Extract product prices from supplier PDFs
Supports multiple formats including solar panels, electronics, and general products
"""
import pdfplumber
import PyPDF2
import re
from fuzzywuzzy import fuzz
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedPDFPriceExtractor:
    """Enhanced PDF price extractor with multiple extraction strategies"""
    
    def __init__(self):
        self.extracted_products = []
        self.extraction_method = None
        
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract products from PDF using multiple strategies
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of extracted products with code, name, and price
        """
        logger.info(f"Starting PDF extraction from: {pdf_path}")
        
        # Try multiple extraction methods
        methods = [
            self._extract_with_pdfplumber_tables,
            self._extract_with_pdfplumber_text,
            self._extract_with_pypdf2,
            self._extract_with_pattern_matching
        ]
        
        for method in methods:
            try:
                products = method(pdf_path)
                if products and len(products) > 0:
                    self.extracted_products = products
                    self.extraction_method = method.__name__
                    logger.info(f"Successfully extracted {len(products)} products using {method.__name__}")
                    return products
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed: {str(e)}")
                continue
        
        logger.error("All extraction methods failed")
        return []
    
    def _extract_with_pdfplumber_tables(self, pdf_path: str) -> List[Dict]:
        """Extract using pdfplumber table detection"""
        products = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logger.info(f"Processing page {page_num} with table extraction")
                
                # Extract tables
                tables = page.extract_tables()
                
                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    # Analyze header to find column positions
                    header = table[0]
                    col_mapping = self._analyze_header(header)
                    
                    # Extract data rows
                    for row_idx, row in enumerate(table[1:], 1):
                        if not row or len(row) < 2:
                            continue
                        
                        product = self._extract_product_from_row(row, col_mapping)
                        if product:
                            product['page'] = page_num
                            product['table'] = table_idx
                            product['row'] = row_idx
                            products.append(product)
        
        return products
    
    def _extract_with_pdfplumber_text(self, pdf_path: str) -> List[Dict]:
        """Extract using pdfplumber text extraction with pattern matching"""
        products = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                # Split into lines
                lines = text.split('\n')
                
                for line_idx, line in enumerate(lines):
                    product = self._parse_line_for_product(line, page_num, line_idx)
                    if product:
                        products.append(product)
        
        return products
    
    def _extract_with_pypdf2(self, pdf_path: str) -> List[Dict]:
        """Extract using PyPDF2 as fallback"""
        products = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                for line_idx, line in enumerate(lines):
                    product = self._parse_line_for_product(line, page_num, line_idx)
                    if product:
                        products.append(product)
        
        return products
    
    def _extract_with_pattern_matching(self, pdf_path: str) -> List[Dict]:
        """Extract using advanced pattern matching for various formats"""
        products = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                # Multiple patterns for different formats
                patterns = [
                    # Pattern 1: Code | Name | Price (with various separators)
                    r'([A-Z0-9\-/]+)\s*[\|\t]\s*([A-Za-z0-9\s\-\(\)\.]+?)\s*[\|\t]\s*(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                    
                    # Pattern 2: Code Name Price (space separated)
                    r'([A-Z0-9\-/]{3,})\s+([A-Za-z][A-Za-z0-9\s\-\(\)\.]{5,}?)\s+(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                    
                    # Pattern 3: Name followed by price on same line
                    r'([A-Za-z][A-Za-z0-9\s\-\(\)\.]{10,}?)\s+(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*$',
                    
                    # Pattern 4: Solar panel specific (Watt, Voltage, etc.)
                    r'(\d+W?)\s+([A-Za-z0-9\s\-\(\)\.]+?(?:Panel|Module|Cell)?)\s+(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                    
                    # Pattern 5: Model/SKU based
                    r'(?:Model|SKU|Code)[\s:]*([A-Z0-9\-/]+)\s+([A-Za-z0-9\s\-\(\)\.]+?)\s+(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
                    
                    for match in matches:
                        groups = match.groups()
                        
                        if len(groups) == 3:
                            code, name, price = groups
                        elif len(groups) == 2:
                            # No code, generate one
                            name, price = groups
                            code = self._generate_code_from_name(name)
                        else:
                            continue
                        
                        # Clean and validate
                        code = code.strip()
                        name = name.strip()
                        price_str = price.replace(',', '').strip()
                        
                        if not name or len(name) < 3:
                            continue
                        
                        try:
                            price_value = float(price_str)
                            if price_value <= 0 or price_value > 10000000:
                                continue
                        except ValueError:
                            continue
                        
                        products.append({
                            'product_code': code,
                            'product_name': name,
                            'price': price_value,
                            'page': page_num,
                            'source': 'pattern_matching'
                        })
        
        # Remove duplicates
        seen = set()
        unique_products = []
        for p in products:
            key = (p['product_code'], p['product_name'])
            if key not in seen:
                seen.add(key)
                unique_products.append(p)
        
        return unique_products
    
    def _analyze_header(self, header: List[str]) -> Dict[str, int]:
        """Analyze table header to find column positions"""
        col_mapping = {
            'code': -1,
            'name': -1,
            'price': -1,
            'description': -1,
            'category': -1,
            'unit': -1
        }
        
        if not header:
            return col_mapping
        
        for idx, cell in enumerate(header):
            if not cell:
                continue
            
            cell_lower = str(cell).lower().strip()
            
            # Code column
            if any(keyword in cell_lower for keyword in ['code', 'sku', 'model', 'item', 'product id', 'part']):
                col_mapping['code'] = idx
            
            # Name column
            elif any(keyword in cell_lower for keyword in ['name', 'description', 'product', 'item name', 'title', 'specification']):
                if col_mapping['name'] == -1:  # Prefer first match
                    col_mapping['name'] = idx
                else:
                    col_mapping['description'] = idx
            
            # Price column
            elif any(keyword in cell_lower for keyword in ['price', 'rate', 'cost', 'amount', 'mrp', 'dealer', 'selling']):
                col_mapping['price'] = idx
            
            # Category column
            elif any(keyword in cell_lower for keyword in ['category', 'type', 'group', 'class']):
                col_mapping['category'] = idx
            
            # Unit column
            elif any(keyword in cell_lower for keyword in ['unit', 'uom', 'qty', 'pack']):
                col_mapping['unit'] = idx
        
        return col_mapping
    
    def _extract_product_from_row(self, row: List[str], col_mapping: Dict[str, int]) -> Optional[Dict]:
        """Extract product information from table row"""
        if not row:
            return None
        
        # Get values from mapped columns
        code = self._get_cell_value(row, col_mapping.get('code', -1))
        name = self._get_cell_value(row, col_mapping.get('name', -1))
        price_str = self._get_cell_value(row, col_mapping.get('price', -1))
        
        # If no explicit mapping, try to infer from row structure
        if not name and len(row) >= 2:
            # Common patterns: [Code, Name, Price] or [Name, Price]
            if len(row) >= 3:
                code = str(row[0]).strip() if row[0] else ''
                name = str(row[1]).strip() if row[1] else ''
                price_str = str(row[2]).strip() if row[2] else ''
            else:
                name = str(row[0]).strip() if row[0] else ''
                price_str = str(row[1]).strip() if row[1] else ''
                code = self._generate_code_from_name(name)
        
        # Validate and clean
        if not name or len(name) < 3:
            return None
        
        # Extract price from string
        price = self._extract_price_from_string(price_str)
        if price is None or price <= 0:
            return None
        
        # Generate code if missing
        if not code or len(code) < 2:
            code = self._generate_code_from_name(name)
        
        return {
            'product_code': code,
            'product_name': name,
            'price': price
        }
    
    def _parse_line_for_product(self, line: str, page_num: int, line_idx: int) -> Optional[Dict]:
        """Parse a text line for product information"""
        if not line or len(line.strip()) < 10:
            return None
        
        # Skip header-like lines
        if any(keyword in line.lower() for keyword in ['sr.', 'no.', 'page', 'total', 'subtotal', 'grand']):
            return None
        
        # Try to extract price
        price_match = re.search(r'(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)', line)
        if not price_match:
            return None
        
        price_str = price_match.group(1).replace(',', '')
        try:
            price = float(price_str)
            if price <= 0 or price > 10000000:
                return None
        except ValueError:
            return None
        
        # Extract name (text before price)
        name_part = line[:price_match.start()].strip()
        
        # Try to extract code from name part
        code_match = re.match(r'^([A-Z0-9\-/]{3,})\s+(.+)$', name_part)
        if code_match:
            code = code_match.group(1)
            name = code_match.group(2).strip()
        else:
            code = self._generate_code_from_name(name_part)
            name = name_part
        
        if len(name) < 3:
            return None
        
        return {
            'product_code': code,
            'product_name': name,
            'price': price,
            'page': page_num,
            'line': line_idx
        }
    
    def _get_cell_value(self, row: List[str], col_idx: int) -> str:
        """Safely get cell value from row"""
        if col_idx < 0 or col_idx >= len(row):
            return ''
        return str(row[col_idx]).strip() if row[col_idx] else ''
    
    def _extract_price_from_string(self, price_str: str) -> Optional[float]:
        """Extract numeric price from string"""
        if not price_str:
            return None
        
        # Remove currency symbols and commas
        price_str = re.sub(r'[₹Rs\.,\s]', '', price_str)
        
        # Extract first number
        match = re.search(r'(\d+(?:\.\d{2})?)', price_str)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None
    
    def _generate_code_from_name(self, name: str) -> str:
        """Generate product code from name"""
        if not name:
            return 'PROD001'
        
        # Take first letters of words
        words = name.upper().split()[:3]
        code = ''.join(word[:3] for word in words if word)
        
        # Add numbers if exists in name
        numbers = re.findall(r'\d+', name)
        if numbers:
            code += numbers[0][:3]
        
        return code[:10] if code else 'PROD001'
    
    def match_with_existing_products(self, existing_products: List[Dict]) -> List[Dict]:
        """
        Match extracted products with existing products in database
        
        Args:
            existing_products: List of existing products from database
            
        Returns:
            List of matched products with confidence scores
        """
        matched_products = []
        
        for extracted in self.extracted_products:
            best_match = None
            best_score = 0
            
            for existing in existing_products:
                # Calculate similarity scores
                code_score = fuzz.ratio(
                    extracted['product_code'].lower(),
                    existing['product_code'].lower()
                )
                
                name_score = fuzz.token_set_ratio(
                    extracted['product_name'].lower(),
                    existing['product_name'].lower()
                )
                
                # Weighted average (name is more important)
                combined_score = (code_score * 0.3) + (name_score * 0.7)
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_match = existing
            
            # Determine match status
            if best_score >= 70:  # Threshold for match
                matched_products.append({
                    'extracted': extracted,
                    'matched': best_match,
                    'confidence': best_score,
                    'status': 'matched'
                })
            else:
                matched_products.append({
                    'extracted': extracted,
                    'matched': None,
                    'confidence': 0,
                    'status': 'no_match'
                })
        
        return matched_products
    
    def get_extraction_stats(self) -> Dict:
        """Get statistics about extraction"""
        return {
            'total_extracted': len(self.extracted_products),
            'extraction_method': self.extraction_method,
            'has_codes': sum(1 for p in self.extracted_products if p.get('product_code')),
            'has_prices': sum(1 for p in self.extracted_products if p.get('price', 0) > 0),
            'avg_price': sum(p.get('price', 0) for p in self.extracted_products) / len(self.extracted_products) if self.extracted_products else 0
        }


# Backward compatibility
class PDFPriceExtractor(EnhancedPDFPriceExtractor):
    """Alias for backward compatibility"""
    pass
