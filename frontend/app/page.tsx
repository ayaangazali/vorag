'use client'

import React, { useState } from 'react'
import BackgroundFX from '@/components/BackgroundFX'
import TopBar from '@/components/TopBar'
import GlassCard from '@/components/GlassCard'
import ChatPanel from '@/components/ChatPanel'
import Composer from '@/components/Composer'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [typingMessageId, setTypingMessageId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSend = async () => {
    if (!inputValue.trim() || isProcessing) return

    setIsProcessing(true)

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      createdAt: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const userQuery = inputValue.trim()
    setInputValue('')

    // Add typing indicator
    const typingId = `assistant-${Date.now()}`
    const typingMessage: Message = {
      id: typingId,
      role: 'assistant',
      content: '', // Will show typing animation
      createdAt: new Date(),
    }

    setMessages((prev) => [...prev, typingMessage])
    setTypingMessageId(typingId)

    try {
      // Call backend API
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userQuery,
          top_k: 5,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Update message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === typingId
            ? { ...msg, content: data.answer }
            : msg
        )
      )
    } catch (error) {
      console.error('Failed to get response:', error)
      
      // Fallback to mock response on error
      const fallbackResponse = "Sorry, I couldn't connect to the backend. Please make sure the backend server is running on http://localhost:8000"
      
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === typingId
            ? { ...msg, content: fallbackResponse }
            : msg
        )
      )
    } finally {
      setTypingMessageId(null)
      setIsProcessing(false)
    }
  }

  return (
    <main className="min-h-screen relative">
      <BackgroundFX />

      <div className="relative z-10 container mx-auto px-4 py-6 max-w-4xl">
        <TopBar />

        {/* Centered chat card */}
        <GlassCard className="flex flex-col" style={{ minHeight: '600px' }}>
          <ChatPanel messages={messages} typingMessageId={typingMessageId} />

          <div className="border-t border-white/30 pt-4 mt-4">
            <Composer
              value={inputValue}
              onChange={setInputValue}
              onSend={handleSend}
              disabled={isProcessing}
            />
          </div>
        </GlassCard>
      </div>
    </main>
  )
}
