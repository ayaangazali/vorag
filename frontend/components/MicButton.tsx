'use client'

import React from 'react'
import { motion } from 'framer-motion'

interface MicButtonProps {
  isRecording: boolean
  onClick: () => void
}

export default function MicButton({ isRecording, onClick }: MicButtonProps) {
  return (
    <div className="relative flex items-center justify-center">
      {/* Pulse rings when recording */}
      {isRecording && (
        <>
          <motion.div
            className="absolute w-24 h-24 rounded-full border-2 border-red-500/50"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div
            className="absolute w-24 h-24 rounded-full border-2 border-red-500/30"
            animate={{
              scale: [1, 1.8, 1],
              opacity: [0.3, 0, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.5
            }}
          />
        </>
      )}

      {/* Main button */}
      <motion.button
        onClick={onClick}
        whileTap={{ scale: 0.9 }}
        whileHover={{ scale: 1.05 }}
        className={`relative w-20 h-20 rounded-full flex items-center justify-center 
                   font-bold text-white shadow-xl transition-all duration-300
                   focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-black
                   ${isRecording 
                     ? 'bg-red-500 focus:ring-red-400 animate-pulse' 
                     : 'bg-gradient-to-br from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 focus:ring-purple-400'
                   }`}
        aria-label={isRecording ? 'Stop recording' : 'Start recording'}
      >
        {isRecording ? (
          <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
            <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
          </svg>
        )}
      </motion.button>

      {/* Waveform visualization when recording */}
      {isRecording && (
        <div className="absolute -bottom-8 flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="w-1 bg-red-500 rounded-full"
              animate={{
                height: ['8px', '20px', '8px'],
              }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.1
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
