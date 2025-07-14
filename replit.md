# Sistema de Consulta de Stock - Distribuciones Lucero

## Overview

This is a Streamlit-based stock consultation system for Distribuciones Lucero that provides a web interface for managing and querying product inventory. The application features dual-access authentication, automatic SFTP updates, and corporate branding with persistent configuration management.

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
- FTP and SFTP integration for remote file downloads and automatic updates
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
- **Paramiko**: SFTP/SSH client for secure file transfers
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
- **JSON Configuration Files**: Implemented for persistent storage of application settings
- **Corporate Branding**: Distribuciones Lucero colors and logo integrated throughout

### Architecture Benefits
- **Dual Authentication**: Admin ("stock2025") and viewer ("lucero") access levels
- **Persistent Configuration**: Settings survive application restarts via JSON storage
- **Automatic Updates**: SFTP integration for scheduled data synchronization
- **Corporate Identity**: Professional appearance with company branding
- **Real-time Search**: Instant filtering across all product fields

## Recent Changes (December 2024)

### Authentication System
- Implemented dual-password system with role-based access control
- Admin users: Full configuration and data management capabilities
- Viewer users: Read-only access to stock consultation

### SFTP Integration
- Complete SFTP configuration interface for administrators
- Automatic nightly updates at 2:00 AM
- Manual update functionality with connection testing
- Persistent SFTP credentials and settings

### Data Persistence
- Configuration persistence using JSON files in data/ directory
- Stock thresholds, SFTP settings, and last update timestamps preserved
- Settings survive application restarts and code updates

### Corporate Branding
- Distribuciones Lucero logo integration
- Corporate color scheme (blue, green, red) applied throughout
- Professional header with company branding
- Styled metrics and interface elements with corporate identity

### Current State
- Fully functional stock consultation system with 4,524 products
- SFTP auto-updates confirmed working (tested December 14, 2024)
- Scheduler logging and monitoring operational
- All configurations persist between sessions
- Corporate branding complete with Distribuciones Lucero identity
- Production ready and tested

### Final Deployment Status
- Application successfully tested with live SFTP data
- Automatic updates verified working at configured schedule
- Authentication system operational for both admin and viewer roles
- Configuration persistence confirmed working
- Ready for production deployment on Replit