'use client'

import React from 'react'
import { motion } from 'framer-motion'

export default function BackgroundFX() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base gradient - light blue tones */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-indigo-50" />
      
      {/* Animated blob 1 - light blue */}
      <motion.div
        className="absolute top-1/4 -left-20 w-96 h-96 bg-blue-200/30 rounded-full blur-3xl"
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      {/* Animated blob 2 - light indigo */}
      <motion.div
        className="absolute bottom-1/4 -right-20 w-96 h-96 bg-indigo-200/30 rounded-full blur-3xl"
        animate={{
          x: [0, -80, 0],
          y: [0, 60, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      {/* Animated blob 3 - light cyan */}
      <motion.div
        className="absolute top-1/2 left-1/2 w-80 h-80 bg-cyan-200/25 rounded-full blur-3xl"
        animate={{
          x: [0, 50, -50, 0],
          y: [0, -40, 40, 0],
          scale: [1, 0.95, 1.05, 1],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  )
}
