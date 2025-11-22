import React from 'react'

const CHAINS = ['Ethereum','Solana','Base','Arbitrum','Avalanche']

export default function ChainSelector(){
  return (
    <select style={{padding:8,borderRadius:8,background:'#000',color:'#fff'}} defaultValue={CHAINS[0]}>
      {CHAINS.map(c=> <option key={c} value={c}>{c}</option>)}
    </select>
  )
}
