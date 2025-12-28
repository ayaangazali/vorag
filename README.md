# VoiceRAG - Voice-Powered RAG Assistant

A modern, glassmorphic chat interface for Voice RAG (Retrieval-Augmented Generation) built with Next.js, React, TypeScript, and Framer Motion.

## ✨ Features

- � **Modern Glassmorphism UI**: Translucent cards, blur effects, bubble aesthetics
- � **Dynamic Chat Interface**: Auto-resizing bubble textarea, smooth animations
- 🤖 **Mocked RAG System**: Simulated assistant responses with typing indicators
- 📱 **Fully Responsive**: Adapts beautifully from mobile to desktop
- ♿ **Accessible**: Keyboard navigation, focus states, ARIA labels
- 🌊 **Animated Background**: Subtle gradient blobs that drift slowly

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/ayaangazali/vorag.git
cd vorag

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## 🎯 Project Structure

```
vorag/
├── app/
│   ├── layout.tsx       # Root layout with dark mode
│   ├── page.tsx         # Main page with chat state management
│   └── globals.css      # Global styles with glassmorphism utilities
├── components/
│   ├── BackgroundFX.tsx    # Animated gradient background blobs
│   ├── GlassCard.tsx       # Reusable glass container component
│   ├── TopBar.tsx          # App header with logo and status
│   ├── StatusPill.tsx      # Status indicator pill component
│   ├── ChatPanel.tsx       # Chat history with auto-scroll
│   ├── MessageBubble.tsx   # Individual message bubble styles
│   ├── Composer.tsx        # Dynamic textarea input with send button
│   └── ContextPanel.tsx    # Retrieved context sidebar (mocked)
└── public/                 # Static assets
```

## 🎨 Design Language

### Glassmorphism
- Translucent backgrounds with backdrop blur
- Soft borders with subtle glows
- Rounded corners (2xl/3xl) for bubble aesthetic
- Dark mode first design

### Color Palette
- Background: Deep black (#0a0a0a)
- Glass borders: `rgba(255, 255, 255, 0.08)`
- User bubbles: Purple-blue gradient
- Assistant bubbles: Subtle glass effect
- Accents: Purple & Blue gradients

### Animations
- **Background**: Slow-drifting gradient blobs (20-30s)
- **Messages**: Fade and slide up on entry
- **Typing**: Animated dots indicator
- **Buttons**: Gentle scale on hover/press

## 💬 Chat Features

### Dynamic Bubble Textarea
- Auto-resizes as you type (up to 160px)
- Press **Enter** to send
- Press **Shift+Enter** for new line
- Fully rounded bubble shape with glass effect

### Message Handling
- User messages appear instantly
- Assistant shows typing indicator (~600ms)
- Auto-scrolls to latest message
- Clean bubble layout with role-based styling

### Keyboard Shortcuts
- `Enter` - Send message
- `Shift+Enter` - New line in message
- Tab navigation throughout UI

## 🔮 Backend Integration (Coming Soon)

Currently uses mocked local state. To connect to a real backend:

1. **Replace mock responses** in `app/page.tsx`:
   ```typescript
   // Replace MOCK_RESPONSES with API call
   const response = await fetch('/api/chat', {
     method: 'POST',
     body: JSON.stringify({ message: userMessage })
   })
   ```

2. **Add voice input**: Implement Web Speech API or Whisper integration

3. **Connect RAG backend**: Wire up Apify scraper and vector database

4. **Update ContextPanel**: Display real retrieved chunks from backend

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **UI Pattern**: Glassmorphism with bubble aesthetic

## 📱 Responsive Design

- **Mobile**: Single column, stacked layout
- **Tablet**: Optimized spacing and sizing
- **Desktop**: Two-column layout (chat + context sidebar)

## ♿ Accessibility

- Semantic HTML throughout
- ARIA labels on interactive elements
- Visible keyboard focus states
- Screen reader friendly
- High contrast text

## 🎭 Mock Data

The app currently uses mocked data for:
- Assistant responses (4 predefined answers)
- Retrieved context chunks (3 sample chunks)
- Typing delay simulation (600ms)

## 📝 Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 🎨 Customization

### Update Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  glass: {
    border: 'rgba(255, 255, 255, 0.08)',
    bg: 'rgba(255, 255, 255, 0.03)',
  },
}
```

### Adjust Animations
Modify durations in `components/BackgroundFX.tsx`:
```typescript
transition={{ duration: 20, repeat: Infinity }}
```

### Change Status
Update `components/StatusPill.tsx` for dynamic status display

## 📄 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 🙏 Acknowledgments

- Built for voice-powered RAG applications
- Designed with glassmorphism and modern UI principles
- Optimized for production use with backend integration
