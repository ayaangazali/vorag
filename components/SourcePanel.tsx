'use client'

import React from 'react'
import { motion } from 'framer-motion'
import Card from './Card'

type Status = 'idle' | 'scraping' | 'indexing' | 'ready' | 'error'

interface SourcePanelProps {
  status: Status
  onRunScrape: () => void
  lastRunTime?: string
}

const steps = [
  { id: 'scrape', label: 'Scrape' },
  { id: 'chunk', label: 'Chunk' },
  { id: 'embed', label: 'Embed' },
  { id: 'index', label: 'Index' },
]

export default function SourcePanel({ status, onRunScrape, lastRunTime }: SourcePanelProps) {
  const getStepStatus = (stepId: string) => {
    if (status === 'error') return 'error'
    if (status === 'idle') return 'pending'
    if (status === 'scraping' && stepId === 'scrape') return 'active'
    if (status === 'scraping') return 'pending'
    if (status === 'indexing' && (stepId === 'chunk' || stepId === 'embed' || stepId === 'index')) return 'active'
    if (status === 'ready') return 'complete'
    return 'pending'
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold mb-6 text-gray-100">Source & Index</h2>
      
      {/* Run button */}
      <button
        onClick={onRunScrape}
        disabled={status === 'scraping' || status === 'indexing'}
        className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 
                   hover:from-purple-600 hover:to-blue-600 text-white font-medium 
                   transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
                   focus:outline-none focus:ring-2 focus:ring-purple-400 focus:ring-offset-2 
                   focus:ring-offset-black mb-6"
        aria-label="Run Spiffy scrape"
      >
        {status === 'scraping' || status === 'indexing' ? 'Running...' : 'Run Spiffy Scrape'}
      </button>

      {/* Progress steps */}
      <div className="space-y-3 mb-6">
        {steps.map((step, idx) => {
          const stepStatus = getStepStatus(step.id)
          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="flex items-center gap-3"
            >
              {/* Step indicator */}
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-medium transition-all ${
                stepStatus === 'complete' ? 'border-green-500 bg-green-500/20 text-green-300' :
                stepStatus === 'active' ? 'border-blue-500 bg-blue-500/20 text-blue-300 animate-pulse' :
                stepStatus === 'error' ? 'border-red-500 bg-red-500/20 text-red-300' :
                'border-gray-600 bg-gray-600/10 text-gray-500'
              }`}>
                {stepStatus === 'complete' ? '✓' : idx + 1}
              </div>
              
              {/* Step label */}
              <span className={`text-sm ${
                stepStatus === 'complete' ? 'text-green-300' :
                stepStatus === 'active' ? 'text-blue-300 font-medium' :
                stepStatus === 'error' ? 'text-red-300' :
                'text-gray-500'
              }`}>
                {step.label}
              </span>

              {/* Connector line */}
              {idx < steps.length - 1 && (
                <div className={`flex-1 h-0.5 ml-4 ${
                  stepStatus === 'complete' ? 'bg-green-500/30' : 'bg-gray-700'
                }`} />
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Last run timestamp */}
      {lastRunTime && (
        <div className="pt-4 border-t border-gray-800">
          <p className="text-xs text-gray-500">Last run:</p>
          <p className="text-sm text-gray-400 mt-1">{lastRunTime}</p>
        </div>
      )}

      {/* Loading skeleton during processing */}
      {(status === 'scraping' || status === 'indexing') && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 space-y-2"
        >
          <div className="h-2 bg-gray-700/50 rounded animate-pulse" />
          <div className="h-2 bg-gray-700/50 rounded animate-pulse w-3/4" />
        </motion.div>
      )}
    </Card>
  )
}
