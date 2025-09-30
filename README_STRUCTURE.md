# Security+ Training Tool - Project Structure

## 📁 **Organized Folder Structure**

The project has been reorganized into a clean, modular structure:

```
Security_Plus_Training_Tool_web_app/
├── 📁 app/                    # Main Flask application
│   ├── __init__.py
│   ├── auth/                  # Authentication modules
│   ├── errors/                # Error handling
│   ├── main/                  # Main routes
│   ├── training/              # Training-specific routes
│   ├── static/                # Static files (CSS, JS, images)
│   └── templates/             # HTML templates
├── 📁 database/               # Database layer
│   ├── __init__.py
│   ├── connection.py          # MongoDB connection management
│   └── question_manager.py    # Question CRUD operations
├── 📁 models/                 # Data models
│   ├── __init__.py
│   ├── enums.py              # Enumerations (QuestionType, Category, etc.)
│   └── question_models.py    # Question model classes
├── 📁 api/                    # API endpoints
│   ├── __init__.py
│   └── question_routes.py    # REST API for questions
├── 📁 scripts/                # Utility scripts
│   ├── __init__.py
│   ├── db_setup.py           # Database setup and management
│   ├── populate_database.py  # Populate with sample questions
│   └── test_atlas_connection.py # Test MongoDB Atlas connection
├── 📁 utils/                  # Utility functions
│   └── __init__.py
├── app.py                     # Main Flask application entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment variables template
├── DATABASE_SETUP.md         # Database setup guide
└── README_STRUCTURE.md       # This file
```

## 🚀 **Quick Start with MongoDB Atlas**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Test Atlas Connection**
```bash
python scripts/test_atlas_connection.py
```

### 3. **Setup Database**
```bash
python scripts/db_setup.py
```

### 4. **Run Application**
```bash
python app.py
```

## 🔧 **Key Components**

### **Database Layer** (`database/`)
- **`connection.py`**: Manages MongoDB Atlas connection
- **`question_manager.py`**: Handles all question CRUD operations

### **Models** (`models/`)
- **`enums.py`**: Question types, categories, difficulty levels
- **`question_models.py`**: Question model classes (MC, T/F, Fill-in-blank, Scenario)

### **API Layer** (`api/`)
- **`question_routes.py`**: REST API endpoints for questions
  - `GET /api/questions` - Get questions with filtering
  - `GET /api/questions/{id}` - Get specific question
  - `GET /api/categories` - Get all categories
  - `GET /api/tags` - Get all tags
  - `GET /api/stats` - Get database statistics

### **Scripts** (`scripts/`)
- **`test_atlas_connection.py`**: Test MongoDB Atlas connectivity
- **`db_setup.py`**: Interactive database management
- **`populate_database.py`**: Add sample Security+ questions

## 🌐 **MongoDB Atlas Configuration**

The application is configured to use your MongoDB Atlas cluster:
- **Connection String**: `mongodb+srv://crystar151129_db_user:vPwV693GAoQykVnr@securityplusdb.k3m7nuk.mongodb.net/`
- **Database**: `security_plus_training`
- **Collection**: `questions`

## 📊 **Question Types Supported**

1. **Multiple Choice** - Standard 4-option questions
2. **True/False** - Binary choice questions
3. **Fill-in-the-Blank** - Text input questions
4. **Scenario-Based** - Complex scenario questions

## 🏷️ **Security+ Categories**

- Threats, Attacks & Vulnerabilities
- Technologies & Tools
- Architecture & Design
- Identity & Access Management
- Risk Management
- Cryptography & PKI
- Governance & Compliance
- Incident Response
- Security Operations
- Security Assessment

## 🔍 **API Usage Examples**

### Get Questions by Category
```bash
curl "http://localhost:5000/api/questions?category=threats_attacks_vulnerabilities&limit=5"
```

### Get Database Statistics
```bash
curl "http://localhost:5000/api/stats"
```

### Get All Categories
```bash
curl "http://localhost:5000/api/categories"
```

## 🛠️ **Development Workflow**

1. **Add New Questions**: Use the models in `models/question_models.py`
2. **Extend API**: Add routes in `api/question_routes.py`
3. **Database Operations**: Use `database/question_manager.py`
4. **Test Changes**: Run `scripts/test_atlas_connection.py`

## 📝 **Environment Variables**

Copy `env_example.txt` to `.env` and configure:
```env
MONGODB_URI=mongodb+srv://crystar151129_db_user:vPwV693GAoQykVnr@securityplusdb.k3m7nuk.mongodb.net/
MONGODB_DATABASE=security_plus_training
SECRET_KEY=your-secret-key-here
```

## 🎯 **Next Steps**

1. **Test the Atlas connection** with the test script
2. **Populate the database** with sample questions
3. **Start the Flask application**
4. **Test the API endpoints**
5. **Add more Security+ questions** as needed

The code is now properly organized and ready for development! 🚀
