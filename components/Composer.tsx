'use client'

import React, { useRef, useEffect, KeyboardEvent } from 'react'
import { motion } from 'framer-motion'

interface ComposerProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled?: boolean
}

export default function Composer({ value, onChange, onSend, disabled = false }: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      const newHeight = Math.min(textarea.scrollHeight, 160) // max 160px
      textarea.style.height = `${newHeight}px`
    }
  }, [value])
  
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
            className="w-full px-6 py-4 glass-input resize-none text-sm text-gray-100 
                       placeholder:text-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
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
          className={`btn-pill bg-gradient-to-r from-purple-600 to-blue-600 text-white 
                     focus:ring-purple-500 shadow-lg shrink-0
                     ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:from-purple-500 hover:to-blue-500'}`}
          aria-label="Send message"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </motion.button>
        
        {/* Mic button (placeholder) */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-pill bg-glass-light border border-glass-border text-gray-400 
                     hover:text-gray-300 hover:border-gray-600 focus:ring-gray-600 
                     shadow-lg shrink-0 relative group"
          aria-label="Voice input (coming soon)"
          title="Voice input coming soon"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          
          {/* Tooltip */}
          <span className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 px-3 py-1 
                         bg-gray-900 text-gray-300 text-xs rounded-lg opacity-0 
                         group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            Coming soon
          </span>
        </motion.button>
      </div>
      
      {/* Helper text */}
      <p className="text-xs text-gray-600 pl-2">
        Press <kbd className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Enter</kbd> to send,{' '}
        <kbd className="px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">Shift+Enter</kbd> for new line
      </p>
    </div>
  )
}
