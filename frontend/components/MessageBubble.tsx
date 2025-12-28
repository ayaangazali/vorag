'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
}

interface MessageBubbleProps {
  message: Message
  isTyping?: boolean
}

export default function MessageBubble({ message, isTyping = false }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`max-w-[80%] md:max-w-[70%] px-5 py-3 ${
        isUser ? 'bubble-user' : 'bubble-assistant'
      }`}>
        {isTyping ? (
          <div className="flex items-center gap-1">
            <motion.span
              className="text-gray-700"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.4, repeat: Infinity, delay: 0 }}
            >
              •
            </motion.span>
            <motion.span
              className="text-gray-700"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.4, repeat: Infinity, delay: 0.2 }}
            >
              •
            </motion.span>
            <motion.span
              className="text-gray-700"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.4, repeat: Infinity, delay: 0.4 }}
            >
              •
            </motion.span>
          </div>
        ) : (
          <p className="text-sm leading-relaxed whitespace-pre-wrap text-gray-800">
            {message.content}
          </p>
        )}
      </div>
    </motion.div>
  )
}
