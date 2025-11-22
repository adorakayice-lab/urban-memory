import React, {useState, useEffect} from 'react'

export default function TopBar(){
  const [busy, setBusy] = useState(false)
  const [adminToken, setAdminToken] = useState(null)

  useEffect(()=>{
    try{ const t = localStorage.getItem('aurelium_admin_token'); setAdminToken(t) }catch(e){}
  },[])

  function getToken(){
    return localStorage.getItem('aurelium_token')
  }

  async function logout(){
    if(!confirm('Log out locally and revoke this session?')) return
    const token = getToken()
    if(token){
      try{ await fetch('/auth/logout', {method:'POST', headers: {Authorization: `Bearer ${token}`}}) }catch(e){}
    }
    try{ localStorage.removeItem('aurelium_token') }catch(e){}
    alert('Logged out locally.')
    window.location.reload()
  }

  async function adminSignIn(){
    const apiKey = prompt('Enter admin API key (or DEFAULT_API_KEY for dev)')
    if(!apiKey) return
    setBusy(true)
    try{
      const r = await fetch('/auth/token', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({api_key: apiKey, role: 'admin'})})
      if(!r.ok){ alert('Failed to sign in as admin'); setBusy(false); return }
      const j = await r.json()
      const token = j.token
      localStorage.setItem('aurelium_admin_token', token)
      setAdminToken(token)
      alert('Admin signed in successfully')
    }catch(e){ alert('Admin sign-in error') }
    finally{ setBusy(false) }
  }

  function adminSignOut(){
    try{ localStorage.removeItem('aurelium_admin_token') }catch(e){}
    setAdminToken(null)
    alert('Admin signed out')
  }

  async function signOutEverywhere(){
    if(!confirm('Sign out everywhere for your account? This requires an admin token (owner-only).')) return
    const token = getToken()
    if(!token){ alert('No local token found.'); return }
    setBusy(true)
    try{
      const me = await fetch('/auth/me', {headers: {Authorization: `Bearer ${token}`}})
      if(!me.ok){ alert('Unable to determine subject.'); setBusy(false); return }
      const j = await me.json()
      const subject = j.sub
      const admin = adminToken || localStorage.getItem('aurelium_admin_token')
      if(!admin){ alert('Admin token required to sign out everywhere.'); setBusy(false); return }
      const r = await fetch('/auth/revoke-subject', {method:'POST', headers: {'Content-Type':'application/json', Authorization: `Bearer ${admin}`}, body: JSON.stringify({subject})})
      if(r.ok){ alert('Sign out everywhere requested.'); } else { alert('Failed to sign out everywhere.'); }
    }catch(e){ alert('Error while requesting sign out everywhere') }
    finally{ setBusy(false) }
  }

  return (
    <header className="topbar">
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <strong style={{fontSize:18,background:'linear-gradient(90deg,#f6c84c,#06b6d4)',WebkitBackgroundClip:'text',color:'transparent'}}>AURELIUM NEXUS</strong>
        <div style={{opacity:0.9,fontSize:13}}>AUM: <span style={{color:'#34d399'}}>$3.84B</span></div>
      </div>
      <nav style={{display:'flex',gap:12,alignItems:'center'}}>
        <div style={{fontSize:13,opacity:0.9}}>Chain: Ethereum</div>
        <button onClick={logout} style={{padding:'6px 12px',borderRadius:999,background:'linear-gradient(90deg,#7c3aed,#06b6d4)',border:'none',color:'#000'}}>Logout</button>
        <button onClick={signOutEverywhere} disabled={busy} style={{padding:'6px 12px',borderRadius:8,background:'#ef4444',border:'none',color:'#fff'}}>Sign out everywhere</button>
        {adminToken ? (
          <button onClick={adminSignOut} style={{padding:'6px 12px',borderRadius:8,background:'#111827',border:'none',color:'#fff'}}>Admin signed in</button>
        ) : (
          <button onClick={adminSignIn} disabled={busy} style={{padding:'6px 12px',borderRadius:8,background:'#06b6d4',border:'none',color:'#000'}}>Admin Sign In</button>
        )}
      </nav>
    </header>
  )
}
