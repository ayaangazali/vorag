'use client'

import React, { useRef, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
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

const WELCOME_TEXT = "Hi! I'm VoiceRAG, your AI assistant. Ask me anything and I'll help you find the information you need."

export default function ChatPanel({ messages, typingMessageId }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [displayedText, setDisplayedText] = useState('')
  const [showWelcome, setShowWelcome] = useState(true)
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, typingMessageId])
  
  // Hide welcome message when user starts chatting
  useEffect(() => {
    if (messages.length > 0) {
      setShowWelcome(false)
    }
  }, [messages])
  
  // Typing animation for welcome text
  useEffect(() => {
    if (!showWelcome) return
    
    let currentIndex = 0
    const interval = setInterval(() => {
      if (currentIndex <= WELCOME_TEXT.length) {
        setDisplayedText(WELCOME_TEXT.slice(0, currentIndex))
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 30) // Speed of typing
    
    return () => clearInterval(interval)
  }, [showWelcome])
  
  return (
    <div 
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-2 py-4 scrollbar-thin"
      style={{ minHeight: '400px', maxHeight: 'calc(100vh - 320px)' }}
    >
      {messages.length === 0 && showWelcome ? (
        <div className="flex items-start justify-start h-full">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-[80%] md:max-w-[70%] px-5 py-3 bubble-assistant"
          >
            <p className="text-sm leading-relaxed text-gray-800">
              {displayedText}
              {displayedText.length < WELCOME_TEXT.length && (
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="inline-block w-0.5 h-4 bg-gray-800 ml-0.5"
                />
              )}
            </p>
          </motion.div>
        </div>
      ) : messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-center">
          <div>
            <div className="text-4xl mb-4">💬</div>
            <p className="text-gray-600 text-sm">
              Start a conversation with VoiceRAG
            </p>
            <p className="text-gray-400 text-xs mt-2">
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
