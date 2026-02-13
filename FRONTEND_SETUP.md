# Frontend Setup Guide

## 🚀 Quick Start

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:
```
VITE_API_URL=http://localhost:5000
```

### 4. Start Development Server
```bash
npm run dev
```

Frontend will run at `http://localhost:3000`

## 📋 Features Implemented

✅ **Authentication Pages**
- Beautiful animated login page with floating particles
- Registration page with validation
- Smooth transitions

✅ **Dashboard**
- Animated statistics cards
- Filterable capsule grid
- Real-time capsule status
- Smooth card animations

✅ **Capsule Management**
- Drag & drop file upload
- Date picker for unlock dates
- Capsule detail view
- Download unlocked files
- Delete capsules

✅ **Animations**
- Framer Motion throughout
- Floating particle background
- Glassmorphism effects
- Hover animations
- Page transitions
- Loading states

## 🎨 Design Features

- **Glassmorphism UI** - Modern glass effects
- **Gradient Backgrounds** - Animated color gradients
- **Gold Accents** - Time capsule theme
- **Smooth Transitions** - Page and component transitions
- **Responsive** - Mobile-friendly design

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── AnimatedBackground.jsx
│   │   ├── Navbar.jsx
│   │   └── PrivateRoute.jsx
│   ├── contexts/
│   │   └── AuthContext.jsx
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── CreateCapsule.jsx
│   │   └── CapsuleDetail.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── public/
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🎯 Next Steps

1. Make sure backend is running on port 5000
2. Start frontend: `npm run dev`
3. Visit `http://localhost:3000`
4. Register/Login and start creating capsules!

## 🐛 Troubleshooting

### Backend Connection Issues
- Check that backend is running: `python run_dev.py`
- Verify API URL in `.env` file
- Check browser console for errors

### Build Errors
- Delete `node_modules` and run `npm install` again
- Check Node.js version (should be 18+)

### CORS Issues
- Backend should have CORS enabled (already configured)
- Check backend is allowing requests from `http://localhost:3000`

## 📝 Notes

- Frontend uses Vite for fast development
- Hot Module Replacement (HMR) enabled
- All API calls go through axios interceptors
- JWT tokens stored in localStorage
- Automatic token refresh can be added

