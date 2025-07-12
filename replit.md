# Sistema de Consulta de Stock

## Overview

This is a Streamlit-based stock consultation system that provides a web interface for managing and querying product inventory. The application is built using Python and Streamlit, focusing on simplicity and ease of use for stock management operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data-driven web applications
- **Layout**: Wide layout with expandable sidebar for better user experience
- **Authentication**: Simple password-based access control system
- **UI Components**: Native Streamlit components for forms, tables, and data display

### Backend Architecture
- **Language**: Python
- **Framework**: Streamlit (handles both frontend and backend logic)
- **Architecture Pattern**: Single-file application with functional programming approach
- **Session Management**: Streamlit's built-in session state for authentication persistence

### Data Storage
- **Primary Storage**: CSV files stored in local filesystem
- **File Structure**: Single CSV file (`data/productos.csv`) containing product information
- **Data Format**: Standard CSV format for easy manipulation and portability

## Key Components

### Authentication System
- Password-protected access using hardcoded credential (`stock2025`)
- Session-based authentication state management
- Environment variable support planned for production security

### Data Management
- CSV file-based data storage for simplicity
- Pandas integration for data manipulation and analysis
- File I/O operations using Python's built-in libraries
- FTP integration for remote file downloads and automatic updates
- Session-based configuration storage for FTP credentials
- Scheduled automatic FTP updates using background threads
- Customizable update timing and frequency

### User Interface
- Page configuration with custom title, icon, and layout
- Responsive design with wide layout
- Professional styling with emojis and markdown formatting

## Data Flow

1. **Authentication Flow**:
   - User enters password → Validation → Session state update → Access granted/denied
   
2. **Data Loading Flow**:
   - Application startup → CSV file reading → Pandas DataFrame creation → Data display

3. **User Interaction Flow**:
   - User queries → Data filtering → Results display → Actions (if any)

## External Dependencies

### Core Dependencies
- **Streamlit**: Web framework for the application interface
- **Pandas**: Data manipulation and analysis
- **Standard Library**: os, io, csv, ftplib, datetime, threading for file operations and FTP connectivity
- **Schedule**: Task scheduling for automatic updates

### File Dependencies
- `data/productos.csv`: Product inventory data file
- Environment variables (optional): For secure password management

## Deployment Strategy

### Local Development
- Direct Python execution with Streamlit run command
- Local file system for data storage
- Development server on localhost

### Production Considerations
- Environment variable configuration for sensitive data
- File system persistence requirements
- Potential migration to database system for scalability

### Security Measures
- Password protection for application access
- Session state management for authenticated users
- Planned environment variable integration for credentials

## Key Design Decisions

### Technology Choices
- **Streamlit over Flask/Django**: Chosen for rapid development and built-in UI components suitable for data applications
- **CSV over Database**: Selected for simplicity and ease of data management in small-scale deployments
- **Functional over OOP**: Streamlit's paradigm favors functional programming for web apps

### Architecture Benefits
- **Simplicity**: Minimal setup and configuration required
- **Maintainability**: Single-file application easy to understand and modify
- **Portability**: CSV-based data storage makes the system easily portable

### Current Limitations
- **Scalability**: CSV storage not suitable for large datasets or concurrent users
- **Security**: Hardcoded password not production-ready
- **Persistence**: No backup or versioning system for data files