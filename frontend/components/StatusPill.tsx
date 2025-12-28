import React from 'react'

interface StatusPillProps {
  status?: string
}

export default function StatusPill({ status = 'Ready' }: StatusPillProps) {
  return (
    <div className="px-4 py-2 rounded-full bg-green-100 border border-green-300 
                    text-green-700 text-sm font-medium flex items-center gap-2">
      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
      {status}
    </div>
  )
}
