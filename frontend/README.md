# Time Capsule Cloud - Frontend

A beautiful, animated frontend for Time Capsule Cloud built with React, Tailwind CSS, and Framer Motion.

## Features

- 🎨 **Modern UI Design** - Beautiful glassmorphism effects
- ✨ **Smooth Animations** - Framer Motion animations throughout
- 📱 **Responsive Design** - Works on all devices
- 🔐 **Authentication** - Login and registration with validation
- 📦 **Capsule Management** - Create, view, and manage time capsules
- 🎭 **Unique Animations** - Floating particles, glows, and transitions

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

Create a `.env` file:

```env
VITE_API_URL=http://localhost:5000
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **React Router** - Navigation
- **Axios** - HTTP client
- **React Hot Toast** - Notifications
- **Lucide React** - Icons
- **date-fns** - Date formatting

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── contexts/       # React contexts (Auth)
│   ├── pages/          # Page components
│   ├── services/       # API services
│   └── App.jsx        # Main app component
├── public/            # Static assets
└── package.json       # Dependencies
```

## Features in Detail

### Animations
- Floating particles background
- Smooth page transitions
- Hover effects on cards
- Loading spinners
- Toast notifications

### UI Components
- Glassmorphism cards
- Gradient buttons
- Animated icons
- Responsive grid layouts
- Drag & drop file upload

## API Integration

The frontend connects to the backend API at `http://localhost:5000` by default. Make sure your backend server is running!

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT

