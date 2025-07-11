import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
import os
import json

class GoogleSheetsService:
    def __init__(self):
        self.client = None
        self.worksheet = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client with authentication"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try to get credentials from environment variables (Replit secrets)
            credentials_json = os.getenv('gcp_service_account')
            if credentials_json:
                try:
                    credentials_info = json.loads(credentials_json)
                    credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                except json.JSONDecodeError:
                    raise Exception("Invalid JSON format in gcp_service_account secret")
            else:
                # Try Streamlit secrets as fallback
                try:
                    if 'gcp_service_account' in st.secrets:
                        credentials_info = dict(st.secrets['gcp_service_account'])
                        credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                    else:
                        # Try credentials file as last resort
                        credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
                        if os.path.exists(credentials_file):
                            credentials = Credentials.from_service_account_file(credentials_file, scopes=scope)
                        else:
                            raise Exception("No Google credentials found. Please provide credentials via the gcp_service_account secret.")
                except Exception as e:
                    raise Exception(f"No Google credentials found. Please provide credentials via the gcp_service_account secret. Error: {str(e)}")
            
            # Authorize and create client
            self.client = gspread.authorize(credentials)
            
        except Exception as e:
            raise Exception(f"Failed to initialize Google Sheets client: {str(e)}")
    
    def connect_to_sheet(self, sheet_url_or_key=None, sheet_name=None):
        """Connect to a specific Google Sheet"""
        try:
            # Get sheet URL/key from environment variables (Replit secrets)
            if not sheet_url_or_key:
                sheet_url_or_key = os.getenv('GOOGLE_SHEET_URL')
                if not sheet_url_or_key:
                    # Try Streamlit secrets as fallback
                    try:
                        sheet_url_or_key = st.secrets.get('GOOGLE_SHEET_URL')
                    except:
                        pass
            
            if not sheet_url_or_key:
                raise Exception("No Google Sheet URL provided. Please set GOOGLE_SHEET_URL in your secrets.")
            
            # Open the spreadsheet
            if sheet_url_or_key.startswith('https://'):
                # It's a URL
                spreadsheet = self.client.open_by_url(sheet_url_or_key)
            else:
                # It's a key
                spreadsheet = self.client.open_by_key(sheet_url_or_key)
            
            # Get the worksheet
            if sheet_name:
                self.worksheet = spreadsheet.worksheet(sheet_name)
            else:
                # Use first worksheet
                self.worksheet = spreadsheet.get_worksheet(0)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to connect to Google Sheet: {str(e)}")
    
    def get_deals(self):
        """Fetch deals data from Google Sheets"""
        try:
            # Connect to the sheet if not already connected
            if not self.worksheet:
                self.connect_to_sheet()
            
            # Get all records
            records = self.worksheet.get_all_records()
            
            if not records:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Expected columns mapping
            column_mapping = {
                'Title': 'title',
                'title': 'title',
                'Description': 'description',
                'description': 'description',
                'Industry': 'industry',
                'industry': 'industry',
                'Target Amount': 'target_amount',
                'target_amount': 'target_amount',
                'TargetAmount': 'target_amount',
                'Raised Amount': 'raised_amount',
                'raised_amount': 'raised_amount',
                'RaisedAmount': 'raised_amount',
                'Status': 'status',
                'status': 'status',
                'Min Investment': 'min_investment',
                'min_investment': 'min_investment',
                'MinInvestment': 'min_investment',
                'Due Date': 'due_date',
                'due_date': 'due_date',
                'DueDate': 'due_date',
                'Documents Link': 'documents_link',
                'documents_link': 'documents_link',
                'DocumentsLink': 'documents_link',
                'Image URL': 'image_url',
                'image_url': 'image_url',
                'ImageURL': 'image_url'
            }
            
            # Rename columns to standardized names
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_columns = ['title', 'description', 'industry', 'target_amount', 'raised_amount', 'status']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = '' if col in ['title', 'description', 'industry', 'status'] else 0
            
            # Convert numeric columns
            numeric_columns = ['target_amount', 'raised_amount', 'min_investment']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Clean up data
            df = df.dropna(subset=['title'])  # Remove rows without titles
            df = df[df['title'].str.strip() != '']  # Remove empty titles
            
            return df
            
        except Exception as e:
            raise Exception(f"Failed to fetch deals from Google Sheets: {str(e)}")
    
    def add_deal(self, deal_data):
        """Add a new deal to the Google Sheet"""
        try:
            if not self.worksheet:
                self.connect_to_sheet()
            
            # Prepare the row data
            row_data = [
                deal_data.get('title', ''),
                deal_data.get('description', ''),
                deal_data.get('industry', ''),
                deal_data.get('target_amount', 0),
                deal_data.get('raised_amount', 0),
                deal_data.get('status', 'Open'),
                deal_data.get('min_investment', 0),
                deal_data.get('due_date', ''),
                deal_data.get('documents_link', ''),
                deal_data.get('image_url', '')
            ]
            
            # Append the row
            self.worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            raise Exception(f"Failed to add deal to Google Sheets: {str(e)}")
    
    def update_deal(self, row_number, deal_data):
        """Update an existing deal in the Google Sheet"""
        try:
            if not self.worksheet:
                self.connect_to_sheet()
            
            # Update specific cells
            for col, value in deal_data.items():
                # Find the column index
                headers = self.worksheet.row_values(1)
                if col in headers:
                    col_index = headers.index(col) + 1
                    self.worksheet.update_cell(row_number, col_index, value)
            
            return True
            
        except Exception as e:
            raise Exception(f"Failed to update deal in Google Sheets: {str(e)}")
    
    def get_sheet_info(self):
        """Get information about the connected sheet"""
        try:
            if not self.worksheet:
                return None
            
            return {
                'title': self.worksheet.title,
                'row_count': self.worksheet.row_count,
                'col_count': self.worksheet.col_count,
                'url': self.worksheet.spreadsheet.url
            }
            
        except Exception as e:
            return None
