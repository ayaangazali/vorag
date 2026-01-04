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
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null)

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

  const handleVoiceQuery = async (audioBlob: Blob) => {
    if (isProcessing) return

    setIsProcessing(true)

    try {
      // Create FormData with the audio file
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')

      // Add user message with placeholder
      const userMessageId = `user-${Date.now()}`
      const userMessage: Message = {
        id: userMessageId,
        role: 'user',
        content: '🎙️ Voice message...',
        createdAt: new Date(),
      }
      setMessages((prev) => [...prev, userMessage])

      // Add typing indicator
      const typingId = `assistant-${Date.now()}`
      const typingMessage: Message = {
        id: typingId,
        role: 'assistant',
        content: '',
        createdAt: new Date(),
      }
      setMessages((prev) => [...prev, typingMessage])
      setTypingMessageId(typingId)

      // Call voice-query endpoint
      const response = await fetch('http://localhost:8000/voice-query', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Voice API error: ${response.status}`)
      }

      // Check if response is audio or JSON
      const contentType = response.headers.get('content-type')
      
      if (contentType?.includes('audio')) {
        // Get metadata from headers
        const transcribedQuestion = response.headers.get('X-Transcribed-Question') || ''
        const answerText = response.headers.get('X-Answer-Text') || ''
        const voiceUsed = response.headers.get('X-Voice') || 'Edge TTS'
        
        console.log('📝 Transcribed:', transcribedQuestion)
        console.log('💬 Answer text:', answerText)
        console.log('🎤 Voice:', voiceUsed)
        
        // Get audio blob
        const audioBlob = await response.blob()
        
        // Create audio URL and preload
        const audioUrl = URL.createObjectURL(audioBlob)
        const audio = new Audio(audioUrl)
        audio.preload = 'auto'  // Preload audio for faster playback
        
        // Store audio element for cleanup
        setAudioElement(audio)
        
        // BATCH UPDATE: Update both user and assistant messages at once (single re-render)
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id === userMessageId && transcribedQuestion) {
              return { ...msg, content: transcribedQuestion }
            }
            if (msg.id === typingId && answerText) {
              return { ...msg, content: answerText }
            }
            return msg
          })
        )
        
        // Play the audio
        await audio.play()
        
        // When audio finishes, clean up
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl)
          console.log('✅ Audio playback completed')
        }
        
        // Handle audio errors
        audio.onerror = (e) => {
          console.error('Audio playback error:', e)
          URL.revokeObjectURL(audioUrl)
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === typingId
                ? { ...msg, content: answerText || 'Audio playback failed. ' + (answerText ? `Answer: ${answerText}` : '') }
                : msg
            )
          )
        }
        
      } else {
        // JSON response (text mode)
        const data = await response.json()
        
        // Update user message with transcription
        if (data.question) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === userMessageId
                ? { ...msg, content: `🎤 "${data.question}"` }
                : msg
            )
          )
        }
        
        // Show the answer as text
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === typingId
              ? { ...msg, content: data.answer || data.detail || 'Voice response received' }
              : msg
          )
        )
        
        // Log if transcription was corrected
        if (data.original_transcription !== data.question) {
          console.log('🔧 Corrected:', data.original_transcription, '→', data.question)
        }
      }

      // Update user message with transcription if available
      // (for now just keep the voice icon)
      
    } catch (error) {
      console.error('Voice query failed:', error)
      
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === typingMessageId
            ? { ...msg, content: `Sorry, voice processing failed: ${error instanceof Error ? error.message : 'Unknown error'}. Make sure the backend is running.` }
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
              onVoiceQuery={handleVoiceQuery}
              disabled={isProcessing}
            />
          </div>
        </GlassCard>
      </div>
    </main>
  )
}
