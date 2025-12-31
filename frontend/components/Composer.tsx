'use client'

import React, { useRef, useEffect, KeyboardEvent } from 'react'
import { motion } from 'framer-motion'
import { useVoiceRecording } from '@/hooks/useVoiceRecording'

interface ComposerProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  onVoiceQuery?: (audioBlob: Blob) => Promise<void>
  disabled?: boolean
}

export default function Composer({ value, onChange, onSend, onVoiceQuery, disabled = false }: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { isRecording, startRecording, stopRecording, error: recordingError } = useVoiceRecording()
  
  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      const newHeight = Math.min(textarea.scrollHeight, 160) // max 160px
      textarea.style.height = `${newHeight}px`
    }
  }, [value])

  const handleVoiceClick = async () => {
    if (disabled) return

    if (isRecording) {
      // Stop recording and send audio
      const audioBlob = await stopRecording()
      if (audioBlob && onVoiceQuery) {
        await onVoiceQuery(audioBlob)
      }
    } else {
      // Start recording
      await startRecording()
    }
  }
  
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (value.trim() && !disabled) {
        onSend()
      }
    }
  }
  
  const isDisabled = disabled || !value.trim()
  
  return (
    <div className="space-y-3">
      <div className="flex items-end gap-3">
        {/* Dynamic bubble textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows={1}
            disabled={disabled}
            className="w-full px-6 py-4 glass-input resize-none text-sm text-gray-800 
                       placeholder:text-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ minHeight: '56px', maxHeight: '160px' }}
            aria-label="Message input"
          />
        </div>
        
        {/* Send button */}
        <motion.button
          onClick={onSend}
          disabled={isDisabled}
          whileHover={!isDisabled ? { scale: 1.05 } : {}}
          whileTap={!isDisabled ? { scale: 0.95 } : {}}
          className={`btn-pill bg-gradient-to-r from-blue-600 to-indigo-600 text-white 
                     focus:ring-blue-500 shadow-lg shrink-0
                     ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:from-blue-500 hover:to-indigo-500'}`}
          aria-label="Send message"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </motion.button>
        
        {/* Mic button - Voice Recording */}
        <motion.button
          onClick={handleVoiceClick}
          disabled={disabled}
          whileHover={{ scale: disabled ? 1 : 1.05 }}
          whileTap={{ scale: disabled ? 1 : 0.95 }}
          className={`btn-pill relative shrink-0 shadow-lg transition-all duration-300
                     ${isRecording 
                       ? 'bg-red-500 text-white animate-pulse' 
                       : 'bg-white/60 border border-white/80 text-gray-600 hover:text-gray-700 hover:border-gray-300'
                     }
                     ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                     focus:ring-blue-400`}
          aria-label={isRecording ? 'Stop recording' : 'Start voice recording'}
          title={isRecording ? 'Click to stop and send' : 'Click to start voice recording'}
        >
          {isRecording ? (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          )}

          {/* Recording pulse indicator */}
          {isRecording && (
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-red-400"
              animate={{
                scale: [1, 1.3],
                opacity: [0.8, 0],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: "easeOut"
              }}
            />
          )}
        </motion.button>
      </div>

      {/* Error message for recording */}
      {recordingError && (
        <p className="text-xs text-red-500 pl-2">
          ⚠️ {recordingError}
        </p>
      )}
      
      {/* Helper text */}
      <p className="text-xs text-gray-500 pl-2">
        {isRecording ? (
          <span className="text-red-500 font-medium animate-pulse">🎙️ Recording... Click the mic to stop and send</span>
        ) : (
          <>
            Press <kbd className="px-1.5 py-0.5 rounded bg-white/60 text-gray-600 font-mono border border-gray-300">Enter</kbd> to send,{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-white/60 text-gray-600 font-mono border border-gray-300">Shift+Enter</kbd> for new line
          </>
        )}
      </p>
    </div>
  )
}
