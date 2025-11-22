import React from 'react'
import ChainSelector from './ChainSelector'
import WalletConnect from './WalletConnect'

export default function TopBarExtra(){
  return (
    <div style={{display:'flex',alignItems:'center',gap:12}}>
      <ChainSelector />
      <WalletConnect />
    </div>
  )
}
