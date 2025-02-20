# SI Opportunity Manager

A modern, desktop-based ticket management system built with PyQt5 and SQLAlchemy, designed to streamline team collaboration and ticket management for the SI team.

## Features

### Core Functionality
- **Real-time Ticket Management**: Create, track, and manage opportunities/tickets with real-time updates
- **Dark Theme UI**: Modern, eye-friendly dark theme interface
- **Response Time Tracking**: Automatic tracking of response and resolution times
- **File Attachments**: Support for file attachments and documentation
- **Custom Vehicle Management**: Dedicated module for managing custom vehicle entries

### User Management
- **Role-based Access Control**: Different permission levels (User, Manager, Admin)
- **Team Management**: Comprehensive team member management with activity tracking
- **User Profiles**: Customizable user profiles with team assignments

### Dashboard & Analytics
- **Team Overview**: Real-time statistics on active tickets, team performance, and completion rates
- **Activity Logging**: Detailed logging of all user actions and system changes
- **Performance Metrics**: Track response times, completion rates, and team productivity

### Security
- **PIN-based Authentication**: Secure access control with PIN authentication
- **Role-based Permissions**: Granular control over user actions and access
- **Activity Auditing**: Complete audit trail of all system activities

## Technical Stack

- **Frontend**: PyQt5
- **Backend**: Python 3.8+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migration Tool**: Alembic
- **Additional Libraries**:
  - `passlib` for PIN hashing
  - `python-dotenv` for environment management
  - `psycopg2-binary` for PostgreSQL connectivity

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd si-opportunity-manager
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```ini
   DATABASE_URL=postgresql://username:password@localhost:5432/si_opportunity
   SECRET_KEY=your_secret_key_here
   ```

5. **Initialize Database**
   ```bash
   alembic upgrade head
   ```

6. **Run the Application**
   ```bash
   python main.py
   ```

## User Roles & Access Levels

### Admin
- Full system access
- User management
- Custom vehicle management
- System configuration
- Performance monitoring

### Manager
- Team management
- Ticket management
- Performance tracking
- Report generation

### User
- Ticket creation and management
- Profile customization
- Basic dashboard access

## Customization

The application supports various customization options:
- Dark/Light theme switching (Dark theme by default)
- Custom vehicle definitions
- Notification preferences
- Dashboard layout customization

## Troubleshooting

Common issues and their solutions:

1. **Database Connection Issues**
   - Verify PostgreSQL service is running
   - Check database credentials in `.env` file
   - Ensure proper network connectivity

2. **UI Display Problems**
   - Verify PyQt5 installation
   - Check system resolution settings
   - Ensure proper theme file loading

3. **Authentication Issues**
   - Verify user credentials
   - Check database user table integrity
   - Ensure proper PIN hashing configuration

## Support

For technical support or feature requests, please contact:
- Email: [support-email]
- Internal Ticket System: Create a new ticket with type "Technical Support"

## Future Enhancements

Planned future improvements:
- Integration with Monday.com
- Mobile application support
- Advanced reporting features
- Real-time chat integration
- Automated ticket routing
- AI-powered ticket categorization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[License Information]

---

Last Updated: [Current Date]
Version: 1.0.0

