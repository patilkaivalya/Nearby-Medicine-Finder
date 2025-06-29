# 🏥 Nearby Medicine Finder - Web Application

A comprehensive web-based solution to help users locate nearby medical stores with required medicines in stock, and enable store owners to manage their inventory.

## 🌟 Key Features

### 👨‍⚕️ For Patients/Users
- 🔍 **Medicine Search**: Find medicines by name with instant results
- 📍 **Automatic Location Detection**: Uses browser geolocation (with permission)
- 🗺️ **Proximity Filtering**: Shows only stores within 1 km radius
- 📞 **Direct Contact**: Call stores or get directions via Google Maps
- ⚠️ **Stock Availability**: Real-time quantity information
- 📱 **Mobile-Friendly**: Responsive design works on all devices

### 🏪 For Store Owners
- 🔐 **Secure Authentication**: Signup/login system with session management
- 🏬 **Store Management**: Add, edit, and delete store information
- 💊 **Inventory Control**: Manage medicine listings and quantities
- 📍 **Map Integration**: Add store location using OpenStreetMap
- 📊 **Dashboard**: Overview of all stores and medicines

### 👨‍💼 Admin Panel
- 👥 **User Management**: View and manage all registered owners
- 🏪 **Store Oversight**: Monitor and manage all stores
- 💊 **Medicine Tracking**: View all medicines across stores
- ✉️ **Message Center**: Review contact form submissions
- 🔒 **Secure Access**: Protected admin-only routes

## 🛠️ Technical Implementation

### Backend
- **Framework**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Session-based with password hashing
- **Location Services**: 
  - OpenStreetMap + Nominatim for geocoding
  - Haversine formula for distance calculations
- **Security Features**:
  - CSRF protection
  - Secure session management
  - No-cache headers for sensitive pages

### Frontend
- **UI Framework**: Bootstrap 5
- **Responsive Design**: Mobile-first approach
- **Interactive Elements**:
  - Modal dialogs
  - Form validation
  - Dynamic tables
- **Accessibility**: Semantic HTML and ARIA labels

## 📂 Project Structure
medicine_finder/
├── app.py # Main application file
├── config.py # Configuration settings
├── requirements.txt # Dependencies
├── static/ # Static files
│ ├── css/
│ ├── js/
│ └── images/
├── templates/ # HTML templates
│ ├── admin/
│ ├── auth/
│ ├── store/
│ ├── base.html
│ └── [other pages]
└── instance/
└── medicine_app.db # Database file


## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/nearby-medicine-finder.git
   cd nearby-medicine-finder
   
2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Configure the application**:
   Create a .env file with your configuration:
   ```bash
   FLASK_SECRET_KEY=your_secret_key_here
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password

5. **Initialize the database**:
   ```bash
   flask shell
   >>> db.create_all()
   >>> exit()

6. **Run the application**:
   ```bash
   flask run

## 📝 Database Schema

![database-schema](https://github.com/user-attachments/assets/e97e1e05-4d20-4dde-a298-42669f4f5457)

## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

## ✉️ Contact

For questions or support, please contact:
**Project Lead**: Kaivalya Patil
**GitHub**: @patilkaivalya
