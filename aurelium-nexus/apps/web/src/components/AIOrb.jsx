import React, {useState} from 'react'

export default function AIOrb(){
  const [open,setOpen] = useState(false)
  return (
    <>
      <div className="orb" onClick={() => setOpen(v => !v)} />
      {open && (
        <div className="orb-panel">
          <h3 style={{margin:'0 0 8px'}}>AI Concierge</h3>
          <input placeholder="Say: Rebalance to 70/30" style={{width:'100%',padding:8,borderRadius:8,background:'#000',border:'1px solid rgba(255,255,255,0.04)',color:'#fff'}} onKeyDown={(e)=>{if(e.key==='Enter') alert('Executing: '+e.currentTarget.value)}} />
        </div>
      )}
    </>
  )
}
