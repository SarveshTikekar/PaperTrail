# PaperTrail
PaperTrail: Saasuke Clan

A full-stack OCR (Optical Character Recognition) application built with Django REST Framework backend and React frontend.

## 🚀 Tech Stack

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework 3.17** - API framework
- **OpenCV 4.13** - Image processing
- **pytesseract** - OCR engine
- **Pillow** - Image handling
- **SQLite** - Database (development)

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Python 3.11+**
- **Node.js 18+**
- **Tesseract OCR** (for production OCR functionality)
  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Add to PATH or update `pytesseract.pytesseract.tesseract_cmd` in `backend/ocr/views.py`

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Colohacks26
```

### 2. Install Tesseract OCR (Required for OCR functionality)

#### Windows:
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- The application automatically detects and uses this path
- **Verified Path**: `C:\Program Files\Tesseract-OCR\tesseract.exe` ✅

#### Linux/Mac:
- Install via package manager:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr

  # macOS
  brew install tesseract
  ```

### 3. Backend Setup

#### Install Python Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

#### Run Migrations
```bash
python manage.py migrate
```

#### Start Development Server
```bash
python manage.py runserver
```
Backend will be available at: `http://127.0.0.1:8000/`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd ../frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```
Frontend will be available at: `http://localhost:5173/`

## 🧪 Testing

### Test OCR API
```bash
# From backend directory
python -c "
import requests
response = requests.post('http://127.0.0.1:8000/api/ocr/',
                        files={'image': open('sample.png', 'rb')})
print('Status:', response.status_code)
print('Response:', response.json())
"
```

### Frontend Commands
```bash
# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
Colohacks26/
├── backend/                 # Django backend
│   ├── config/             # Django settings
│   ├── ocr/                # OCR app
│   ├── manage.py
│   ├── requirements.txt
│   └── sample.png          # Test image
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
│   ├── package.json
│   └── tailwind.config.js
├── .gitignore
└── README.md
```

## 🔧 Configuration

### Environment Variables
Create `.env` files in both backend and frontend directories if needed:

**Backend (.env):**
```
DEBUG=True
SECRET_KEY=your-secret-key
```

**Frontend (.env):**
```
VITE_API_URL=http://127.0.0.1:8000/api
```

### CORS Settings
CORS is configured in `backend/config/settings.py` to allow requests from the frontend.

## 🚀 Deployment

### Backend Deployment
1. Set `DEBUG=False` in settings
2. Configure production database
3. Install Tesseract OCR on server
4. Use a WSGI server (gunicorn, uwsgi)

### Frontend Deployment
1. Run `npm run build`
2. Serve the `dist/` directory with any static server
3. Update API URLs for production

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

## 📝 Notes

- The application currently uses mock OCR responses for development
- Install Tesseract OCR for actual text extraction
- Sample image (`sample.png`) is included for testing
- Backend runs on port 8000, frontend on port 5173

## 🐛 Troubleshooting

### Common Issues

**Tesseract not found:**
- Install Tesseract OCR from the official website
- Update the path in `backend/ocr/views.py` if needed

**Port conflicts:**
- Backend: Change port with `python manage.py runserver 8001`
- Frontend: Update `vite.config.js` or use `--port` flag

**CORS errors:**
- Check that backend is running and CORS settings are correct
- Ensure frontend is making requests to the correct URL

## 📄 License

This project is part of Colohacks26 - PaperTrail by Saasuke Clan.
