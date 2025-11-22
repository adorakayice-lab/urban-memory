import React from 'react'

export default function BridgeVisualizer(){
  const chains = ['Ethereum','Solana','Base','Arbitrum','Avalanche']
  return (
    <div style={{height:200,display:'flex',alignItems:'center',justifyContent:'center'}}>
      <svg width="600" height="200">
        {chains.map((c,i)=> (
          <g key={c} transform={`translate(${50 + i*110},100)`}> 
            <circle r="18" fill="#06b6d4" />
            <text x="0" y="40" textAnchor="middle" fontSize="12" fill="#fff">{c}</text>
          </g>
        ))}
        {chains.map((_,i)=> (
          <line key={i} x1={300} y1={100} x2={50 + i*110} y2={100} stroke="#00d4ff" strokeOpacity="0.6" strokeWidth="2" />
        ))}
      </svg>
    </div>
  )
}
