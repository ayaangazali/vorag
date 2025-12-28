'use client'

import React, { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
}

interface ChatPanelProps {
  messages: Message[]
  typingMessageId?: string | null
}

export default function ChatPanel({ messages, typingMessageId }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, typingMessageId])
  
  return (
    <div 
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-2 py-4 scrollbar-thin"
      style={{ minHeight: '400px', maxHeight: 'calc(100vh - 320px)' }}
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-center">
          <div>
            <div className="text-4xl mb-4">💬</div>
            <p className="text-gray-400 text-sm">
              Start a conversation with VoiceRAG
            </p>
            <p className="text-gray-600 text-xs mt-2">
              Type a message below to begin
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <MessageBubble 
              key={message.id} 
              message={message}
              isTyping={message.id === typingMessageId}
            />
          ))}
        </>
      )}
    </div>
  )
}
