export default function JarvisUI() {
  return (
    <div className="min-h-screen bg-black overflow-hidden text-cyan-400 relative font-sans">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,255,0.12),transparent_60%)]"></div>
      <div className="absolute inset-0 opacity-20 bg-[linear-gradient(rgba(0,255,255,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.08)_1px,transparent_1px)] bg-[size:40px_40px]"></div>
      <div className="absolute inset-0 animate-pulse bg-[radial-gradient(circle,rgba(0,255,255,0.08),transparent_70%)]"></div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 80 }).map((_, i) => (
          <div
            key={i}
            className="absolute bg-cyan-400 rounded-full opacity-40 animate-pulse"
            style={{
              width: `${Math.random() * 4 + 1}px`,
              height: `${Math.random() * 4 + 1}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              boxShadow: '0 0 15px rgba(0,255,255,0.9)',
            }}
          />
        ))}
      </div>

      {/* Header */}
      <header className="relative z-20 flex items-center justify-between p-5 border-b border-cyan-500/30 backdrop-blur-xl bg-black/20">
        <div>
          <h1 className="text-5xl font-bold tracking-[10px] text-cyan-300 drop-shadow-[0_0_15px_rgba(0,255,255,0.9)]">
            J.A.R.V.I.S
          </h1>
          <p className="text-cyan-500 tracking-[4px] mt-2 text-sm">
            JUST A RATHER VERY INTELLIGENT SYSTEM
          </p>
        </div>

        <div className="text-right">
          <div className="text-5xl font-mono text-cyan-300">01:57</div>
          <div className="flex items-center justify-end gap-2 mt-1">
            <div className="w-3 h-3 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-green-300 tracking-[3px]">ONLINE</span>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="relative z-10 p-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Side */}
        <div className="space-y-6">
          {/* System Monitor */}
          <div className="bg-cyan-500/10 border border-cyan-400/30 rounded-3xl p-6 backdrop-blur-2xl shadow-[0_0_40px_rgba(0,255,255,0.15)]">
            <h2 className="text-xl tracking-[4px] mb-6 text-cyan-300">
              SYSTEM MONITOR
            </h2>

            <div className="space-y-5">
              {[
                ['CPU', '35%'],
                ['RAM', '73%'],
                ['DISK', '76%'],
                ['NETWORK', '98%'],
              ].map(([name, value]) => (
                <div key={name}>
                  <div className="flex justify-between mb-2">
                    <span>{name}</span>
                    <span>{value}</span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-black/50 overflow-hidden">
                    <div className="h-full rounded-full bg-cyan-400 animate-pulse shadow-[0_0_20px_rgba(0,255,255,0.9)]" style={{ width: value }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Radar */}
          <div className="bg-cyan-500/10 border border-cyan-400/30 rounded-3xl p-6 backdrop-blur-2xl flex flex-col items-center shadow-[0_0_40px_rgba(0,255,255,0.15)]">
            <h2 className="text-xl tracking-[4px] mb-6 text-cyan-300">
              RADAR SYSTEM
            </h2>

            <div className="relative w-72 h-72 rounded-full border border-cyan-500 flex items-center justify-center overflow-hidden">
              <div className="absolute inset-0 rounded-full border border-cyan-400 animate-ping opacity-20"></div>
              <div className="absolute w-[90%] h-[90%] border border-cyan-500 rounded-full"></div>
              <div className="absolute w-[65%] h-[65%] border border-cyan-500 rounded-full"></div>
              <div className="absolute w-[40%] h-[40%] border border-cyan-500 rounded-full"></div>

              <div className="absolute w-1/2 h-1 bg-cyan-300 origin-left animate-spin shadow-[0_0_25px_rgba(0,255,255,1)]"></div>

              <div className="w-4 h-4 rounded-full bg-cyan-300 shadow-[0_0_20px_rgba(0,255,255,1)]"></div>
            </div>
          </div>
        </div>

        {/* Center Core */}
        <div className="bg-cyan-500/10 border border-cyan-400/30 rounded-[40px] p-8 backdrop-blur-2xl flex flex-col items-center justify-center shadow-[0_0_60px_rgba(0,255,255,0.2)] min-h-[850px]">
          <h2 className="text-3xl tracking-[8px] mb-10 text-cyan-300">
            AI CORE
          </h2>

          <div className="relative flex items-center justify-center w-[450px] h-[450px]">
            <div className="absolute w-full h-full border border-cyan-500 rounded-full animate-spin"></div>
            <div className="absolute w-[85%] h-[85%] border border-cyan-300 rounded-full animate-pulse"></div>
            <div className="absolute w-[70%] h-[70%] border border-cyan-400 rounded-full animate-spin"></div>
            <div className="absolute w-[55%] h-[55%] border border-cyan-500 rounded-full animate-pulse"></div>

            <div className="absolute w-[180px] h-[180px] bg-cyan-400 rounded-full blur-3xl opacity-40"></div>

            <div className="absolute text-center">
              <div className="text-5xl font-bold text-cyan-200 drop-shadow-[0_0_25px_rgba(0,255,255,1)]">
                ACTIVE
              </div>
              <div className="text-cyan-400 mt-3 tracking-[5px]">
                NEURAL NETWORK ONLINE
              </div>
            </div>
          </div>

          {/* Voice Assistant */}
          <div className="mt-16 w-full">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <div className="absolute inset-0 rounded-full border-4 border-cyan-400 animate-ping opacity-20"></div>
                <div className="w-32 h-32 rounded-full border-4 border-cyan-300 flex items-center justify-center text-5xl bg-black/30 shadow-[0_0_40px_rgba(0,255,255,0.9)]">
                  🎙️
                </div>
              </div>
            </div>

            {/* Audio Waves */}
            <div className="flex justify-center items-end gap-2 h-24">
              {Array.from({ length: 20 }).map((_, i) => (
                <div
                  key={i}
                  className="w-2 bg-cyan-300 rounded-full animate-pulse"
                  style={{
                    height: `${Math.random() * 80 + 20}px`,
                    animationDuration: `${Math.random() * 1 + 0.5}s`,
                    boxShadow: '0 0 15px rgba(0,255,255,0.9)',
                  }}
                ></div>
              ))}
            </div>

            <button className="mt-10 w-full py-5 rounded-3xl bg-cyan-400 text-black font-bold text-xl tracking-[3px] hover:scale-105 transition-all shadow-[0_0_35px_rgba(0,255,255,1)]">
              ACTIVATE JARVIS
            </button>
          </div>
        </div>

        {/* Right Side */}
        <div className="space-y-6">
          {/* Climate */}
          <div className="bg-cyan-500/10 border border-cyan-400/30 rounded-3xl p-6 backdrop-blur-2xl shadow-[0_0_40px_rgba(0,255,255,0.15)]">
            <h2 className="text-xl tracking-[4px] mb-6 text-cyan-300">
              WEATHER SYSTEM
            </h2>

            <div className="text-center py-6">
              <div className="text-7xl">☁️</div>
              <div className="text-6xl text-cyan-200 mt-4">24°C</div>
              <div className="text-cyan-400 mt-3 tracking-[3px]">
                PARTLY CLOUDY
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="bg-cyan-500/10 border border-cyan-400/30 rounded-3xl p-6 backdrop-blur-2xl shadow-[0_0_40px_rgba(0,255,255,0.15)]">
            <h2 className="text-xl tracking-[4px] mb-6 text-cyan-300">
              SECURITY STATUS
            </h2>

            <div className="space-y-5">
              {[
                'FACIAL RECOGNITION',
                'VOICE AUTHORIZATION',
                'NETWORK PROTECTION',
                'AI FIREWALL',
              ].map((item) => (
                <div
                  key={item}
                  className="flex justify-between items-center border border-cyan-500/20 rounded-2xl p-4"
                >
                  <span>{item}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-green-300">ACTIVE</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-2 gap-4">
            {['SCAN', 'ANALYZE', 'NETWORK', 'VOICE'].map((btn) => (
              <button
                key={btn}
                className="py-5 rounded-2xl bg-cyan-400/90 text-black font-bold tracking-[3px] hover:scale-105 transition-all shadow-[0_0_25px_rgba(0,255,255,0.8)]"
              >
                {btn}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
