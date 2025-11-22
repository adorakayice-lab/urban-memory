// Lightweight telemetry opt-in/out helper for the web app (dev-only)
export function isTelemetryEnabled(){
  try{
    const v = localStorage.getItem('aurelium_telemetry')
    return v === '1'
  }catch(e){
    return false
  }
}

export function setTelemetryEnabled(enabled){
  try{
    localStorage.setItem('aurelium_telemetry', enabled ? '1' : '0')
  }catch(e){}
}

export function sendTelemetry(event, payload){
  if(!isTelemetryEnabled()) return
  // In a production app, post to analytics endpoint.
  console.info('[telemetry]', event, payload)
}
