'use client'

import React from 'react'
import GlassCard from './GlassCard'

interface RetrievedChunk {
  title: string
  snippet: string
  score: number
}

const MOCK_CHUNKS: RetrievedChunk[] = [
  {
    title: 'Understanding RAG Architecture',
    snippet: 'Retrieval-Augmented Generation combines the power of large language models with external knowledge retrieval...',
    score: 0.94,
  },
  {
    title: 'Voice Interface Best Practices',
    snippet: 'When building voice-enabled applications, consider speech recognition accuracy, natural language understanding...',
    score: 0.87,
  },
  {
    title: 'Vector Database Integration',
    snippet: 'Embedding documents into vector space allows for semantic similarity search, enabling more relevant retrieval...',
    score: 0.82,
  },
]

export default function ContextPanel() {
  return (
    <GlassCard className="h-fit">
      <h3 className="text-lg font-semibold text-gray-100 mb-4">Retrieved Context</h3>
      
      <div className="space-y-3">
        {MOCK_CHUNKS.map((chunk, idx) => (
          <div 
            key={idx}
            className="p-3 rounded-2xl bg-glass-light border border-glass-border 
                       hover:border-purple-500/30 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-200 flex-1 pr-2">
                {chunk.title}
              </h4>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${
                chunk.score >= 0.9 ? 'bg-green-500/20 text-green-300' :
                chunk.score >= 0.8 ? 'bg-blue-500/20 text-blue-300' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {Math.round(chunk.score * 100)}%
              </span>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed line-clamp-2">
              {chunk.snippet}
            </p>
          </div>
        ))}
      </div>
      
      <p className="text-xs text-gray-600 mt-4 text-center">
        Mock retrieved chunks
      </p>
    </GlassCard>
  )
}
