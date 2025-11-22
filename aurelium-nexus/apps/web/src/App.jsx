import React from 'react'
import TopBar from './components/TopBar'
import AIOrb from './components/AIOrb'
import PortfolioSphere from './components/PortfolioSphere'
import TopBarExtra from './components/TopBarExtra'
import YieldWaterfall from './components/YieldWaterfall'
import BridgeVisualizer from './components/BridgeVisualizer'
import Vault from './components/Vault'

export default function App(){
  return (
    <div className="app-root">
      <TopBar />
      <div style={{position:'fixed',top:12,right:12,zIndex:50}}>
        <TopBarExtra />
      </div>
      <main className="main">
        <h1 className="title">AURELIUM NEXUS — Minimal Demo</h1>
        <div className="panel">
          <PortfolioSphere />
          <BridgeVisualizer />
          <YieldWaterfall />
          <Vault />
        </div>
      </main>
      <AIOrb />
    </div>
  )
}
