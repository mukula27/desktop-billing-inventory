"""
PDF Price Extractor - Extract product prices from supplier PDF price lists
"""
import pdfplumber
import re
from typing import List, Dict, Optional
import PyPDF2


class PDFPriceExtractor:
    def __init__(self):
        self.extracted_data = []
    
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract product information from PDF
        Returns list of dictionaries with product_code, product_name, and price
        """
        try:
            # Try pdfplumber first (better for tables)
            data = self._extract_with_pdfplumber(pdf_path)
            
            if not data:
                # Fallback to PyPDF2 for text extraction
                data = self._extract_with_pypdf2(pdf_path)
            
            self.extracted_data = data
            return data
            
        except Exception as e:
            print(f"Error extracting from PDF: {e}")
            return []
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[Dict]:
        """Extract using pdfplumber (good for tables)"""
        extracted_items = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table:
                            continue
                        
                        # Try to identify header row
                        header_row = None
                        for idx, row in enumerate(table):
                            if self._is_header_row(row):
                                header_row = idx
                                break
                        
                        if header_row is not None:
                            # Process rows after header
                            for row in table[header_row + 1:]:
                                item = self._parse_table_row(row, table[header_row])
                                if item:
                                    extracted_items.append(item)
                        else:
                            # No clear header, try to parse each row
                            for row in table:
                                item = self._parse_row_without_header(row)
                                if item:
                                    extracted_items.append(item)
                    
                    # Also extract text for non-table data
                    text = page.extract_text()
                    if text:
                        text_items = self._extract_from_text(text)
                        extracted_items.extend(text_items)
            
            return self._deduplicate_items(extracted_items)
            
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            return []
    
    def _extract_with_pypdf2(self, pdf_path: str) -> List[Dict]:
        """Extract using PyPDF2 (fallback for text-based PDFs)"""
        extracted_items = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        items = self._extract_from_text(text)
                        extracted_items.extend(items)
            
            return self._deduplicate_items(extracted_items)
            
        except Exception as e:
            print(f"Error with PyPDF2: {e}")
            return []
    
    def _is_header_row(self, row: List[str]) -> bool:
        """Check if row is likely a header row"""
        if not row:
            return False
        
        header_keywords = ['product', 'item', 'code', 'name', 'price', 'rate', 'mrp', 'cost']
        row_text = ' '.join([str(cell).lower() for cell in row if cell])
        
        return any(keyword in row_text for keyword in header_keywords)
    
    def _parse_table_row(self, row: List[str], header: List[str]) -> Optional[Dict]:
        """Parse a table row based on header"""
        if not row or len(row) < 2:
            return None
        
        try:
            # Create mapping of header to values
            row_dict = {}
            for idx, cell in enumerate(row):
                if idx < len(header) and header[idx]:
                    row_dict[header[idx].lower().strip()] = str(cell).strip() if cell else ""
            
            # Extract product code
            product_code = None
            for key in ['code', 'item code', 'product code', 'sku']:
                if key in row_dict and row_dict[key]:
                    product_code = row_dict[key]
                    break
            
            # Extract product name
            product_name = None
            for key in ['name', 'product name', 'item name', 'description', 'product']:
                if key in row_dict and row_dict[key]:
                    product_name = row_dict[key]
                    break
            
            # Extract price
            price = None
            for key in ['price', 'rate', 'mrp', 'cost', 'selling price', 'unit price']:
                if key in row_dict and row_dict[key]:
                    price = self._extract_price(row_dict[key])
                    if price:
                        break
            
            # If we couldn't find with headers, try positional
            if not product_code or not product_name or not price:
                return self._parse_row_without_header(row)
            
            if product_code and product_name and price:
                return {
                    'product_code': product_code,
                    'product_name': product_name,
                    'price': price
                }
            
        except Exception as e:
            print(f"Error parsing table row: {e}")
        
        return None
    
    def _parse_row_without_header(self, row: List[str]) -> Optional[Dict]:
        """Parse row without header information (positional)"""
        if not row or len(row) < 2:
            return None
        
        try:
            # Clean row
            cleaned_row = [str(cell).strip() for cell in row if cell and str(cell).strip()]
            
            if len(cleaned_row) < 2:
                return None
            
            # Common patterns:
            # [Code, Name, Price]
            # [Name, Code, Price]
            # [Code, Name, ..., Price]
            
            product_code = None
            product_name = None
            price = None
            
            # Try to find price (usually numeric with currency symbols)
            for cell in cleaned_row:
                extracted_price = self._extract_price(cell)
                if extracted_price:
                    price = extracted_price
                    break
            
            if not price:
                return None
            
            # Remaining cells are likely code and name
            non_price_cells = [cell for cell in cleaned_row if not self._extract_price(cell)]
            
            if len(non_price_cells) >= 2:
                # First is usually code, second is name (or vice versa)
                # Check which looks more like a code
                if self._looks_like_code(non_price_cells[0]):
                    product_code = non_price_cells[0]
                    product_name = non_price_cells[1]
                else:
                    product_name = non_price_cells[0]
                    product_code = non_price_cells[1] if len(non_price_cells) > 1 else non_price_cells[0]
            elif len(non_price_cells) == 1:
                # Only one field, use it as name and generate code
                product_name = non_price_cells[0]
                product_code = self._generate_code_from_name(product_name)
            
            if product_code and product_name and price:
                return {
                    'product_code': product_code,
                    'product_name': product_name,
                    'price': price
                }
            
        except Exception as e:
            print(f"Error parsing row: {e}")
        
        return None
    
    def _extract_from_text(self, text: str) -> List[Dict]:
        """Extract product information from plain text"""
        extracted_items = []
        
        # Split into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Try to find price in line
            price = self._extract_price(line)
            if not price:
                continue
            
            # Remove price from line to get product info
            line_without_price = re.sub(r'[₹$€£]?\s*\d+[,.]?\d*\.?\d*', '', line).strip()
            
            # Try to split into code and name
            parts = re.split(r'\s{2,}|\t', line_without_price)
            parts = [p.strip() for p in parts if p.strip()]
            
            if len(parts) >= 2:
                if self._looks_like_code(parts[0]):
                    product_code = parts[0]
                    product_name = ' '.join(parts[1:])
                else:
                    product_name = parts[0]
                    product_code = parts[1] if len(parts) > 1 else self._generate_code_from_name(product_name)
                
                extracted_items.append({
                    'product_code': product_code,
                    'product_name': product_name,
                    'price': price
                })
        
        return extracted_items
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None
        
        # Remove currency symbols and extract number
        # Patterns: ₹1,234.56, $1234.56, 1234.56, 1,234
        pattern = r'[₹$€£]?\s*(\d+[,.]?\d*\.?\d*)'
        matches = re.findall(pattern, str(text))
        
        for match in matches:
            try:
                # Remove commas and convert to float
                price_str = match.replace(',', '')
                price = float(price_str)
                
                # Sanity check (price should be reasonable)
                if 0.01 <= price <= 1000000:
                    return price
            except:
                continue
        
        return None
    
    def _looks_like_code(self, text: str) -> bool:
        """Check if text looks like a product code"""
        if not text or len(text) > 20:
            return False
        
        # Product codes usually:
        # - Are short (< 20 chars)
        # - Contain numbers
        # - May contain hyphens, underscores
        # - Are uppercase or mixed case
        
        has_number = bool(re.search(r'\d', text))
        has_special = bool(re.search(r'[-_]', text))
        is_short = len(text) <= 15
        
        return has_number and is_short
    
    def _generate_code_from_name(self, name: str) -> str:
        """Generate a product code from name"""
        # Take first 3 letters of each word, uppercase
        words = name.split()[:3]
        code = ''.join([w[:3].upper() for w in words])
        return code[:10]  # Limit to 10 chars
    
    def _deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items"""
        seen = set()
        unique_items = []
        
        for item in items:
            key = (item['product_code'], item['product_name'])
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def match_with_existing_products(self, extracted_items: List[Dict], 
                                     existing_products: List[Dict]) -> List[Dict]:
        """
        Match extracted items with existing products
        Returns list with match information
        """
        matched_items = []
        
        for item in extracted_items:
            match_info = {
                'extracted_code': item['product_code'],
                'extracted_name': item['product_name'],
                'extracted_price': item['price'],
                'matched': False,
                'matched_product_id': None,
                'matched_product_name': None,
                'current_price': None,
                'confidence': 0
            }
            
            # Try exact code match
            for product in existing_products:
                if product['product_code'].lower() == item['product_code'].lower():
                    match_info['matched'] = True
                    match_info['matched_product_id'] = product['id']
                    match_info['matched_product_name'] = product['product_name']
                    match_info['current_price'] = product['selling_price']
                    match_info['confidence'] = 100
                    break
            
            # Try fuzzy name match if no code match
            if not match_info['matched']:
                best_match = None
                best_score = 0
                
                for product in existing_products:
                    score = self._similarity_score(item['product_name'], product['product_name'])
                    if score > best_score and score > 0.7:  # 70% similarity threshold
                        best_score = score
                        best_match = product
                
                if best_match:
                    match_info['matched'] = True
                    match_info['matched_product_id'] = best_match['id']
                    match_info['matched_product_name'] = best_match['product_name']
                    match_info['current_price'] = best_match['selling_price']
                    match_info['confidence'] = int(best_score * 100)
            
            matched_items.append(match_info)
        
        return matched_items
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity score between two strings (0-1)"""
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Simple word-based similarity
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
