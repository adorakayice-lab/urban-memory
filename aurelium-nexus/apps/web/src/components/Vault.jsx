import React from 'react'

export default function Vault(){
  return (
    <div style={{marginTop:20}}>
      <h3>RWA Vault — Dubai Marina Penthouse</h3>
      <div style={{display:'flex',gap:12,alignItems:'center'}}>
        <div style={{width:220,height:140,background:'#071026',borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div style={{color:'#fff',opacity:0.9}}>3D Model Placeholder</div>
        </div>
        <div>
          <p style={{margin:'0 0 6px'}}>Cap Rate: <strong>8.4%</strong></p>
          <p style={{margin:'0 0 6px'}}>Yield: <strong>12.7%</strong></p>
          <p style={{margin:'0 0 6px'}}>$42M tokenized • <button style={{marginLeft:8}}>View Details</button></p>
        </div>
      </div>
    </div>
  )
}
