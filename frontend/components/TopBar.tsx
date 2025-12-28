import React from 'react'
import StatusPill from './StatusPill'

export default function TopBar() {
  return (
    <div className="glass-card mb-6 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: App name */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-500 
                          flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xl">V</span>
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 
                         bg-clip-text text-transparent">
            VoiceRAG
          </h1>
        </div>
        
        {/* Center: Source info */}
        <div className="hidden md:flex items-center gap-2 text-sm text-gray-600">
          <span className="text-gray-500">Source:</span>
          <span className="text-gray-700 font-mono">hardcoded-site.com</span>
        </div>
        
        {/* Right: Status */}
        <StatusPill />
      </div>
    </div>
  )
}
