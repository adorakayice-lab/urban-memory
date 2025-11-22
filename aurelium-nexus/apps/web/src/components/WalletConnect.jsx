import React, { useState } from 'react'
import { ethers } from 'ethers'

export default function WalletConnect(){
  const [connected, setConnected] = useState(false)
  const [address, setAddress] = useState(null)
  const [hasNft, setHasNft] = useState(null)
  const [network, setNetwork] = useState(null)

  async function connect(){
    if (!window.ethereum) {
      alert('No injected wallet found. Install MetaMask or another Web3 wallet.')
      return
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum)
      await provider.send('eth_requestAccounts', [])
      const signer = await provider.getSigner()
      const addr = await signer.getAddress()
      setAddress(addr)
      setConnected(true)
      try {
        const net = await provider.getNetwork()
        setNetwork(net.name || net.chainId)
      } catch (e) {
        setNetwork('unknown')
      }

      // Call backend NFT check
      const res = await fetch('/nft-check?address=' + addr, { headers: { 'x-api-key': 'dev-api-key' } })
      if (res.ok) {
        const j = await res.json()
        setHasNft(!!j.owns)
      } else {
        setHasNft(false)
      }
    } catch (e) {
      console.error(e)
      alert('Wallet connection failed: ' + String(e))
    }
  }

  function disconnect(){
    setConnected(false)
    setAddress(null)
    setHasNft(null)
  }

  if (!connected) return <button onClick={connect} style={{padding:'6px 12px',borderRadius:999}}>Connect Wallet</button>

  return (
    <div style={{display:'flex',alignItems:'center',gap:8}}>
      <div style={{fontSize:12,opacity:0.9}}>{address ? `${address.slice(0,6)}...${address.slice(-4)}` : '—'}</div>
      <div style={{fontSize:11,opacity:0.8}}>Net: {network}</div>
      {hasNft === null ? <div style={{fontSize:12,opacity:0.7}}>Checking NFT…</div> : hasNft ? <div style={{background:'linear-gradient(90deg,#7c3aed,#f59e0b)',padding:'6px 10px',borderRadius:999,color:'#000'}}>Black Card Tier</div> : <div style={{fontSize:12,opacity:0.8}}>No NFT</div>}
      <button onClick={disconnect} style={{padding:'6px 8px',borderRadius:999}}>Disconnect</button>
    </div>
  )
}
