import React from 'react'

export default function TopBar(){
  return (
    <header className="topbar">
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <strong style={{fontSize:18,background:'linear-gradient(90deg,#f6c84c,#06b6d4)',WebkitBackgroundClip:'text',color:'transparent'}}>AURELIUM NEXUS</strong>
        <div style={{opacity:0.9,fontSize:13}}>AUM: <span style={{color:'#34d399'}}>$3.84B</span></div>
      </div>
      <nav style={{display:'flex',gap:12,alignItems:'center'}}>
        <div style={{fontSize:13,opacity:0.9}}>Chain: Ethereum</div>
        <button style={{padding:'6px 12px',borderRadius:999,background:'linear-gradient(90deg,#7c3aed,#06b6d4)',border:'none',color:'#000'}}>Connect Wallet</button>
      </nav>
    </header>
  )
}
