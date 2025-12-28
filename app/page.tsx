'use client'

import React, { useState } from 'react'
import BackgroundFX from '@/components/BackgroundFX'
import TopBar from '@/components/TopBar'
import GlassCard from '@/components/GlassCard'
import ChatPanel from '@/components/ChatPanel'
import Composer from '@/components/Composer'
import ContextPanel from '@/components/ContextPanel'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt: Date
}

// Mock assistant responses
const MOCK_RESPONSES = [
  "Based on the retrieved context, RAG systems combine the power of language models with real-time knowledge retrieval, enabling more accurate and contextual responses.",
  "Voice interfaces require careful consideration of speech recognition accuracy and natural language understanding to provide a seamless user experience.",
  "Vector databases enable semantic search by storing document embeddings, allowing for more relevant context retrieval compared to traditional keyword matching.",
  "The key to effective RAG is balancing retrieval quality with response generation - ensuring the retrieved context is both relevant and properly integrated into the answer.",
]

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [typingMessageId, setTypingMessageId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSend = () => {
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

    // Simulate assistant response after delay
    setTimeout(() => {
      const randomResponse = MOCK_RESPONSES[Math.floor(Math.random() * MOCK_RESPONSES.length)]

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === typingId
            ? { ...msg, content: randomResponse }
            : msg
        )
      )
      setTypingMessageId(null)
      setIsProcessing(false)
    }, 600)
  }

  return (
    <main className="min-h-screen relative">
      <BackgroundFX />

      <div className="relative z-10 container mx-auto px-4 py-6 max-w-7xl">
        <TopBar />

        {/* Main content layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Center chat card */}
          <div className="lg:col-span-8">
            <GlassCard className="flex flex-col" style={{ minHeight: '600px' }}>
              <ChatPanel messages={messages} typingMessageId={typingMessageId} />

              <div className="border-t border-glass-border pt-4 mt-4">
                <Composer
                  value={inputValue}
                  onChange={setInputValue}
                  onSend={handleSend}
                  disabled={isProcessing}
                />
              </div>
            </GlassCard>
          </div>

          {/* Right sidebar - Context */}
          <div className="lg:col-span-4">
            <ContextPanel />
          </div>
        </div>
      </div>
    </main>
  )
}
