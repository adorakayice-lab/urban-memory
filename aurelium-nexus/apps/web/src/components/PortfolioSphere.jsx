import React from 'react'

const assets = [
  { name: 'Manhattan Tower', value: 428 },
  { name: 'Gold Vault', value: 567 },
  { name: 'US Treasuries', value: 890 },
  { name: 'Dubai Penthouse', value: 42 },
  { name: 'SanFran Loft', value: 120 },
  { name: 'Munich Office', value: 98 }
]

export default function PortfolioSphere(){
  return (
    <div>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
        <h2 style={{margin:0}}>Portfolio Sphere</h2>
        <div style={{fontSize:13,opacity:0.9}}>Total Value: <strong>$2.1B</strong></div>
      </div>
      <div className="portfolio">
        {assets.map((a,i)=> (
          <div key={i} className="asset">
            <div style={{fontWeight:700}}>{a.name}</div>
            <div style={{fontSize:12,opacity:0.9}}>${a.value}M</div>
          </div>
        ))}
      </div>
    </div>
  )
}
