# VoiceRAG UI Components Reference

## Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  TopBar (GlassCard)                                     │
│  [V] VoiceRAG      Source: hardcoded-site.com    Ready  │
└─────────────────────────────────────────────────────────┘

┌────────────────────────────┬───────────────────────────┐
│                            │                           │
│  Chat Panel (GlassCard)    │  Context Panel           │
│                            │  (GlassCard)             │
│  ┌──────────────────────┐  │                          │
│  │                      │  │  Retrieved Context       │
│  │  Message Bubbles     │  │  • Chunk 1 (94%)        │
│  │  (auto-scroll)       │  │  • Chunk 2 (87%)        │
│  │                      │  │  • Chunk 3 (82%)        │
│  └──────────────────────┘  │                          │
│                            │                           │
│  ┌──────────────────────┐  │                          │
│  │ [Dynamic Textarea  ] │  │                          │
│  │ [with bubble shape ] │  │                          │
│  └──────────────────────┘  │                          │
│  [🎤] [Send]              │                           │
│  Enter to send            │                           │
└────────────────────────────┴───────────────────────────┘
```

## Component Breakdown

### BackgroundFX
- 3 animated gradient blobs
- Slow drift animation (20-30s loops)
- Purple, blue, and indigo colors
- Positioned behind all content (z-index: -10)

### GlassCard
- Base component for all panels
- Props: `children`, `className`, `style`
- Uses `.glass-card` utility class
- Backdrop blur + translucent bg

### TopBar
- Fixed structure: Logo | Source | Status
- VoiceRAG branding with gradient text
- Status pill shows "Ready" (static)
- Responsive: hides source on mobile

### ChatPanel
- Scrollable message container
- Auto-scrolls to bottom on new messages
- Empty state with centered emoji
- Props: `messages[]`, `typingMessageId`

### MessageBubble
- User: right-aligned, purple-blue gradient
- Assistant: left-aligned, glass effect
- Typing animation: 3 animated dots
- Border radius: rounded-3xl, trimmed corner

### Composer
- Auto-resizing textarea (56px - 160px)
- Glass bubble style with rounded-full
- Send button with arrow icon
- Mic button (disabled, "Coming soon")
- Helper text for keyboard shortcuts
- Props: `value`, `onChange`, `onSend`, `disabled`

### ContextPanel
- Static mock chunks (3 items)
- Each chunk: title, snippet, score badge
- Score colors: 90%+ green, 80%+ blue
- Hover effect on cards

### StatusPill
- Rounded pill shape
- Animated pulse dot
- Green color scheme for "Ready"
- Can be extended for other statuses

## CSS Utilities (globals.css)

### .glass-card
- Background: rgba(255, 255, 255, 0.03)
- Backdrop blur: 2xl
- Border: rgba(255, 255, 255, 0.08)
- Border radius: rounded-3xl
- Shadow: 2xl

### .glass-input
- Similar to glass-card
- Rounded-full shape
- Focus: purple ring effect
- Transition: all 200ms

### .bubble-user
- Gradient: purple-600/30 → blue-600/30
- Border: purple-500/30
- Rounded-3xl with rounded-tr-md trim

### .bubble-assistant
- Light glass background
- Standard glass border
- Rounded-3xl with rounded-tl-md trim

### .btn-pill
- Rounded-full
- Padding: px-6 py-2.5
- Focus ring with offset
- Active scale: 0.95

### .scrollbar-thin
- Custom scrollbar styling
- Width: 6px
- Transparent track
- Semi-transparent thumb

## State Management (page.tsx)

### State Variables
```typescript
messages: Message[]        // Chat history
inputValue: string         // Current textarea content
typingMessageId: string    // ID of message being typed
isProcessing: boolean      // Locks input during response
```

### Message Flow
1. User types in Composer
2. Press Enter → handleSend()
3. Add user message to array
4. Add empty assistant message with typingId
5. Show typing animation (600ms)
6. Replace with random mock response
7. Clear typingId and unlock input

### Message Interface
```typescript
interface Message {
  id: string              // Unique identifier
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
}
```

## Animations

### Background Blobs
- Duration: 20-30s per loop
- Easing: easeInOut
- Transform: translate + scale
- Infinite repeat

### Message Entry
- Initial: opacity 0, translateY(10px)
- Animate: opacity 1, translateY(0)
- Duration: 300ms

### Typing Dots
- 3 dots with staggered animation
- Opacity: 0.4 → 1 → 0.4
- Duration: 1.4s loop
- Delays: 0ms, 200ms, 400ms

### Button Hover/Press
- Hover: scale(1.05)
- Press: scale(0.95)
- Smooth spring animation

## Responsive Breakpoints

- **Mobile (< 768px)**
  - Single column layout
  - Context panel below chat
  - Full-width cards
  
- **Tablet (768px - 1024px)**
  - Optimized spacing
  - Adjusted font sizes
  
- **Desktop (> 1024px)**
  - 12-column grid
  - Chat: 8 columns
  - Context: 4 columns
  - Max width: 7xl (1280px)

## Color Palette

### Backgrounds
- Body: #0a0a0a
- Glass: rgba(255, 255, 255, 0.03)
- Glass light: rgba(255, 255, 255, 0.08)

### Borders
- Default: rgba(255, 255, 255, 0.08)
- Hover: rgba(255, 255, 255, 0.2)

### Text
- Primary: #ededed
- Secondary: #9ca3af (gray-400)
- Tertiary: #6b7280 (gray-500)

### Accents
- Purple: #9333ea (purple-600)
- Blue: #2563eb (blue-600)
- Green: #22c55e (green-500)

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line
- `Tab` - Navigate between elements
- Focus visible on all interactive elements
