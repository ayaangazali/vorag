# VoRAG Frontend

Modern glassmorphic chat interface for Voice RAG built with Next.js, React, TypeScript, and Framer Motion.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📁 Structure

```
frontend/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Main page with chat
│   └── globals.css      # Global styles
├── components/
│   ├── BackgroundFX.tsx    # Animated background
│   ├── ChatPanel.tsx       # Chat history
│   ├── Composer.tsx        # Message input
│   ├── GlassCard.tsx       # Reusable glass card
│   ├── MessageBubble.tsx   # Message display
│   ├── StatusPill.tsx      # Status indicator
│   └── TopBar.tsx          # Header
└── public/                 # Static assets
```

## 🎨 Design

- **Light Mode**: White with faint light blue background
- **Glassmorphism**: Transparent glass effects with backdrop blur
- **Animations**: Framer Motion for smooth transitions
- **Responsive**: Mobile-first design

## 🔧 Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Lint code
```

## 📚 Documentation

See [COMPONENTS.md](./COMPONENTS.md) for detailed component documentation.

## 🔗 Backend Integration

The frontend expects the backend API at `http://localhost:8000`. Update the API URL in your environment:

```bash
# Create .env.local (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎯 Features

- ✅ Welcome typing animation
- ✅ Dynamic bubble textarea
- ✅ Message history with auto-scroll
- ✅ Glass morphism effects
- ✅ Animated background
- ⏳ Backend integration (coming soon)
- ⏳ Voice input (coming soon)

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🎨 Customization

### Colors

Edit `tailwind.config.js`:
```javascript
colors: {
  glass: {
    border: 'rgba(255, 255, 255, 0.6)',
    bg: 'rgba(255, 255, 255, 0.4)',
  }
}
```

### Animations

Modify in `components/BackgroundFX.tsx`:
```typescript
transition={{ duration: 20, repeat: Infinity }}
```

## 📄 License

MIT
