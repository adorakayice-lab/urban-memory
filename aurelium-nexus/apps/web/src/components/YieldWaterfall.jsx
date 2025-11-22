import React from 'react'

export default function YieldWaterfall(){
  const items = [
    {label:'RWA Income', value: 480},
    {label:'Treasury Yield', value: 320},
    {label:'Crypto Yield', value: 200}
  ]
  const total = items.reduce((s,i)=>s+i.value,0)
  return (
    <div style={{marginTop:20}}>
      <h3>Yield Waterfall</h3>
      <div style={{display:'flex',gap:12}}>
        {items.map((it,i)=> (
          <div key={i} style={{flex: it.value, background:'linear-gradient(180deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01))',padding:12,borderRadius:8}}>
            <div style={{fontWeight:700}}>{it.label}</div>
            <div style={{fontSize:12}}>${it.value}M</div>
          </div>
        ))}
      </div>
      <div style={{marginTop:8,fontSize:13,opacity:0.9}}>Total: ${total}M</div>
    </div>
  )
}
