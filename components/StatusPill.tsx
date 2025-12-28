import React from 'react'

interface StatusPillProps {
  status?: string
}

export default function StatusPill({ status = 'Ready' }: StatusPillProps) {
  return (
    <div className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30 
                    text-green-300 text-sm font-medium flex items-center gap-2">
      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
      {status}
    </div>
  )
}
