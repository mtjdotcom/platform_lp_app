# Co-Investment Portal

## Overview

This is a Streamlit-based web application for managing and displaying co-investment opportunities. The application provides a portal for partners to explore investment deals with real-time data sourced from Google Sheets. It features interactive dashboards, deal cards, and progress tracking visualizations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development and built-in web interface capabilities
- **Layout**: Wide layout with expandable sidebar for controls and filters
- **State Management**: Streamlit session state for caching deal data and tracking refresh times
- **Styling**: Custom CSS styling through Streamlit's native styling capabilities

### Backend Architecture
- **Data Layer**: Google Sheets integration serving as the primary data source
- **Service Layer**: Modular service classes for external API interactions
- **Component Architecture**: Reusable UI components for deal display and visualization

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and main application logic
- **Features**: 
  - Page configuration and layout setup
  - Data caching with `@st.cache_resource` decorator
  - Currency formatting utilities
  - Status color coding system

### 2. Deal Components (`deal_components.py`)
- **Purpose**: Reusable UI components for deal presentation
- **Key Features**:
  - `DealCard` class for standardized deal display
  - Progress visualization using Plotly gauge charts
  - Currency formatting and status color utilities
  - Interactive funding progress indicators

### 3. Google Sheets Service (`google_sheets_service.py`)
- **Purpose**: External data integration and authentication
- **Authentication Strategy**: Multi-tier credential resolution:
  1. Streamlit secrets (primary for deployed environments)
  2. Environment variable JSON (for local development)
  3. Credentials file fallback (legacy support)
- **Scope**: Read/write access to Google Sheets and Drive APIs

## Data Flow

1. **Authentication**: Application initializes Google Sheets service with credential resolution
2. **Data Retrieval**: Service connects to designated Google Sheet containing deal data
3. **Data Processing**: Raw sheet data is processed and formatted for display
4. **Caching**: Processed data is cached in Streamlit session state
5. **Visualization**: Data is rendered through interactive components and charts
6. **Real-time Updates**: Data refresh mechanisms maintain current information

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization library (express and graph_objects)
- **gspread**: Google Sheets API client
- **google-auth**: Google authentication libraries

### Google Cloud Platform Integration
- **Google Sheets API**: Primary data source
- **Google Drive API**: Required for Sheets access
- **Service Account Authentication**: Secure API access without user intervention

## Deployment Strategy

### Authentication Configuration
- **Production**: Utilizes Streamlit secrets for secure credential management
- **Development**: Supports multiple credential sources for flexible local development
- **Security**: Service account-based authentication eliminates need for user OAuth flow

### Scalability Considerations
- **Caching**: Resource-level caching prevents unnecessary API calls
- **Session Management**: Efficient state management for multi-user scenarios
- **Error Handling**: Graceful degradation when external services are unavailable

### Environment Setup
- Requires Google Cloud Platform service account with appropriate permissions
- Streamlit Cloud deployment ready with secrets management
- Local development supported with environment variables or credential files

The application follows a clean separation of concerns with modular components, making it maintainable and extensible for future enhancements such as user authentication, deal filtering, or additional data sources.