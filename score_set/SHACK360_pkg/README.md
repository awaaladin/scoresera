# Counter Django Web App - Ajo Savings Platform

Counter is a production-ready Django web application for farmers and traders in Nigeria. It enables users to form communities (Ajo groups), contribute to a shared vault, and receive disbursements based on assigned slots. The app features a comprehensive dashboard with real-time updates, transaction tracking, encrypted group chat, and bank payout integration.

## Features

### Core Functionality
- User registration and authentication
- Community (Ajo) creation and management
- Vault system for pooled contributions
- Slot-based disbursement cycles (weekly/monthly)
- Contribution tracking and validation
- Automated payout scheduling

### Dashboard Features
- Real-time vault balance and stats
- Contribution deadline countdown
- Recent transaction history
- Cycle progress timeline
- Bank account payout method management
- Notifications system (10 types)

### Advanced Features
- Encrypted group chat (Bitcoin-level encryption using Fernet)
- Transaction ledger with unique references
- Bank alert system for disbursements
- Member slot assignments
- Contribution validation (amount & cycle)
- Notification system for all events

## Tech Stack

### Backend
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL (database)
- Cryptography (Fernet encryption)
- Python-dateutil (cycle calculations)

### Frontend
- Vanilla JavaScript (Fetch API)
- HTML5 & CSS3
- Tailwind CSS 3.x (utility-first styling)
- Inter font family

## Project Structure

```
counter/
├── core/                    # Main app
│   ├── models.py           # 9 models (Community, Transaction, Notification, etc.)
│   ├── views.py            # REST API viewsets
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # API routes
│   └── management/         # Custom commands
│       └── commands/
│           ├── seed_data.py
│           └── clear_data.py
├── theme/                  # Frontend templates
│   ├── templates/
│   │   ├── index.html      # Main dashboard
│   │   ├── base.html
│   │   ├── login.html
│   │   └── signup.html
│   └── static/             # Static files
├── counter/                # Project settings
│   ├── settings.py
│   └── urls.py
├── requirements.txt        # Python dependencies
└── manage.py
```

## Database Models

### Core Models
- **Community**: Ajo group with vault, cycles, and contribution rules
- **CommunityMember**: User membership with slot assignments
- **Contribution**: Individual contributions with cycle tracking
- **Disbursement**: Payout records with slot-based distribution

### Supporting Models
- **PayoutMethod**: Bank account details (encrypted)
- **Transaction**: Complete financial ledger
- **Notification**: 10 types (member_joined, contribution_received, etc.)
- **GroupChat**: Encrypted messaging groups
- **GroupMembership**: User roles in group chats
- **Message**: Encrypted chat messages

## API Endpoints

### Communities
- `GET /api/communities/` - List all communities
- `POST /api/communities/{id}/join/` - Join community
- `GET /api/communities/{id}/dashboard_stats/` - Dashboard data
- `GET /api/communities/{id}/timeline/` - Cycle timeline
- `POST /api/communities/{id}/assign_slots/` - Assign member slots

### Contributions
- `POST /api/contributions/contribute/` - Make contribution
- `GET /api/contributions/` - List contributions

### Transactions
- `GET /api/transactions/` - List transactions (filterable)
- `GET /api/transactions/recent/` - Last 10 transactions

### Notifications
- `GET /api/notifications/` - List notifications
- `GET /api/notifications/unread_count/` - Unread count
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read

### Payout Methods
- `GET /api/payout-methods/` - List bank accounts
- `POST /api/payout-methods/` - Add bank account
- `POST /api/payout-methods/{id}/set_default/` - Set default

### Users
- `GET /api/users/me/` - Current user details

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool

### Installation

1. **Clone and navigate to project**
   ```bash
   cd c:\Users\awaje\Documents\counter
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```powershell
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```powershell
   python manage.py createsuperuser
   ```

6. **Seed sample data (optional)**
   ```powershell
   python manage.py seed_data
   ```

7. **Run development server**
   ```powershell
   python manage.py runserver
   ```

8. **Access the application**
   - Dashboard: http://127.0.0.1:8000/
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/

## Development

### Management Commands

- **Seed sample data**
  ```powershell
  python manage.py seed_data
  ```

- **Clear all data**
  ```powershell
  python manage.py clear_data
  ```

### Code Quality

The codebase follows PEP 8 standards with proper indentation (4 spaces). All Python files have been formatted using autopep8.

### Testing

Run Django checks:
```powershell
python manage.py check
```

## Dashboard Features

### Vault Stats Card
- Total vault balance
- Target amount progress
- Contribution amount per member
- Current cycle number
- Days until contribution deadline

### Transaction History
- Recent 5 transactions
- Transaction type (contribution/disbursement)
- Amount and status
- Timestamp

### Payout Method Card
- Bank name and account number (masked)
- Add/edit bank details modal

### Cycle Timeline
- All members with slot numbers
- Contribution status per cycle
- Received payout status
- Highlight current user

### Contribution Modal
- Amount validation
- Instant contribution submission
- Real-time vault balance update

## Real-Time Updates

The dashboard polls the API every 30 seconds to:
- Update vault balance
- Refresh transaction list
- Update cycle progress
- Refresh notification count

## Security Features

- CSRF protection on all POST requests
- Bank account number masking (shows first 3 and last 4 digits)
- Fernet encryption for group chat messages
- User authentication required for all API endpoints
- Transaction validation (amount & cycle)

## Future Enhancements

- Payment gateway integration (Paystack/Flutterwave)
- SMS notifications
- Email notifications
- Mobile app (React Native)
- Advanced analytics dashboard
- Multi-currency support
- KYC verification

## Contributing

This project is actively maintained. Follow PEP 8 standards and ensure all tests pass before submitting pull requests.

## License

Proprietary - All rights reserved

---

**Last Updated**: January 2026  
**Status**: Production-ready  
**Version**: 1.0.0
