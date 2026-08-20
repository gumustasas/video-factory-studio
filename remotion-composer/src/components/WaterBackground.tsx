import { useCurrentFrame, useVideoConfig } from "remotion";

export type WaterBgVariant = "droplets" | "waves" | "molecules" | "city-glow" | "meter";

interface WaterBackgroundProps {
  variant?: WaterBgVariant;
  primaryColor?: string;
  accentColor?: string;
  bgColor?: string;
  intensity?: number;
}

// Deterministic pseudo-random — required by Remotion (no Math.random() in render)
function seededRandom(seed: number): number {
  const x = Math.sin(seed + 1) * 43758.5453123;
  return x - Math.floor(x);
}

export const WaterBackground: React.FC<WaterBackgroundProps> = ({
  variant = "droplets",
  primaryColor = "#0066CC",
  accentColor = "#00A651",
  bgColor = "#0A1628",
  intensity = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  if (variant === "droplets") {
    const drops = Array.from({ length: 18 }, (_, i) => {
      const x = seededRandom(i * 7) * 100;
      const baseY = seededRandom(i * 13) * 120 - 20;
      const speed = 8 + seededRandom(i * 3) * 14;
      const y = ((baseY + t * speed) % 130) - 10;
      const size = 4 + seededRandom(i * 5) * 14;
      const opacity = (0.15 + seededRandom(i * 11) * 0.35) * intensity;
      const isAccent = i % 5 === 0;
      return { x, y, size, opacity, isAccent };
    });

    return (
      <div style={{ position: "absolute", inset: 0, background: bgColor, overflow: "hidden" }}>
        <svg
          viewBox="0 0 100 100"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="bgGrad" cx="50%" cy="30%" r="70%">
              <stop offset="0%" stopColor={primaryColor} stopOpacity="0.18" />
              <stop offset="100%" stopColor={bgColor} stopOpacity="0" />
            </radialGradient>
          </defs>
          <rect width="100" height="100" fill="url(#bgGrad)" />
          {drops.map((d, i) => (
            <ellipse
              key={i}
              cx={d.x}
              cy={d.y}
              rx={d.size * 0.45}
              ry={d.size * 0.7}
              fill={d.isAccent ? accentColor : primaryColor}
              opacity={d.opacity}
            />
          ))}
        </svg>
      </div>
    );
  }

  if (variant === "waves") {
    const waveOffset = t * 0.4 * intensity;
    const waves = [
      { amp: 6, freq: 0.8, phase: 0, color: primaryColor, opacity: 0.25 },
      { amp: 4, freq: 1.2, phase: Math.PI * 0.6, color: accentColor, opacity: 0.15 },
      { amp: 3, freq: 0.6, phase: Math.PI * 1.2, color: primaryColor, opacity: 0.1 },
    ];

    return (
      <div style={{ position: "absolute", inset: 0, background: bgColor, overflow: "hidden" }}>
        <svg
          viewBox="0 0 100 100"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
          preserveAspectRatio="xMidYMid slice"
        >
          {waves.map((w, wi) => {
            const points = Array.from({ length: 41 }, (_, i) => {
              const x = i * 2.5;
              const y = 50 + Math.sin((x * w.freq * Math.PI) / 50 + waveOffset + w.phase) * w.amp;
              return `${x},${y}`;
            });
            const path = `M0,100 L0,${points[0].split(",")[1]} L${points.join(" L")} L100,100 Z`;
            return <path key={wi} d={path} fill={w.color} opacity={w.opacity * intensity} />;
          })}
        </svg>
      </div>
    );
  }

  if (variant === "molecules") {
    const nodes = Array.from({ length: 12 }, (_, i) => ({
      x: 10 + seededRandom(i * 7) * 80,
      y: 10 + seededRandom(i * 11) * 80,
      r: 2 + seededRandom(i * 3) * 3,
      vx: (seededRandom(i * 5) - 0.5) * 0.8,
      vy: (seededRandom(i * 9) - 0.5) * 0.8,
    }));

    const animated = nodes.map((n) => ({
      ...n,
      ax: ((n.x + n.vx * t * 5) % 100 + 100) % 100,
      ay: ((n.y + n.vy * t * 5) % 100 + 100) % 100,
    }));

    const edges: [number, number][] = [];
    for (let i = 0; i < animated.length; i++) {
      for (let j = i + 1; j < animated.length; j++) {
        const dx = animated[i].ax - animated[j].ax;
        const dy = animated[i].ay - animated[j].ay;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 30) edges.push([i, j]);
      }
    }

    return (
      <div style={{ position: "absolute", inset: 0, background: bgColor, overflow: "hidden" }}>
        <svg
          viewBox="0 0 100 100"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
          preserveAspectRatio="xMidYMid slice"
        >
          {edges.map(([i, j], ei) => {
            const dx = animated[i].ax - animated[j].ax;
            const dy = animated[i].ay - animated[j].ay;
            const dist = Math.sqrt(dx * dx + dy * dy);
            return (
              <line
                key={ei}
                x1={animated[i].ax} y1={animated[i].ay}
                x2={animated[j].ax} y2={animated[j].ay}
                stroke={primaryColor}
                strokeWidth={0.4}
                opacity={(1 - dist / 30) * 0.4 * intensity}
              />
            );
          })}
          {animated.map((n, i) => (
            <circle
              key={i}
              cx={n.ax} cy={n.ay} r={n.r}
              fill={i % 3 === 0 ? accentColor : primaryColor}
              opacity={0.6 * intensity}
            />
          ))}
        </svg>
      </div>
    );
  }

  if (variant === "city-glow") {
    const buildings = Array.from({ length: 16 }, (_, i) => ({
      x: i * 6.5,
      w: 4 + seededRandom(i * 7) * 4,
      h: 15 + seededRandom(i * 3) * 40,
    }));

    const glowPulse = 0.6 + Math.sin(t * 1.2) * 0.2;

    return (
      <div style={{ position: "absolute", inset: 0, background: bgColor, overflow: "hidden" }}>
        <svg
          viewBox="0 0 104 100"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
          preserveAspectRatio="xMidYMid slice"
        >
          <defs>
            <radialGradient id="skyGlow" cx="50%" cy="60%" r="60%">
              <stop offset="0%" stopColor={primaryColor} stopOpacity={String(0.3 * intensity)} />
              <stop offset="100%" stopColor={bgColor} stopOpacity="0" />
            </radialGradient>
          </defs>
          <rect width="104" height="100" fill="url(#skyGlow)" />
          {buildings.map((b, i) => {
            const gy = 100 - b.h;
            return (
              <g key={i}>
                <rect
                  x={b.x} y={gy} width={b.w} height={b.h}
                  fill={primaryColor}
                  opacity={0.15 * intensity}
                />
                {Array.from({ length: Math.floor(b.h / 8) }, (_, wi) => (
                  <rect
                    key={wi}
                    x={b.x + 0.8} y={gy + 4 + wi * 8}
                    width={1.2} height={1.5}
                    fill={accentColor}
                    opacity={(seededRandom(i * 100 + wi) > 0.4 ? 0.7 : 0) * glowPulse * intensity}
                  />
                ))}
              </g>
            );
          })}
          <rect x="0" y="88" width="104" height="12" fill={primaryColor} opacity={0.1 * intensity} />
        </svg>
      </div>
    );
  }

  // variant === "meter"
  const meterAngle = -120 + ((t * 15) % 240);
  const needleRad = (meterAngle * Math.PI) / 180;
  const needleX = 50 + Math.cos(needleRad) * 28;
  const needleY = 55 + Math.sin(needleRad) * 28;

  return (
    <div style={{ position: "absolute", inset: 0, background: bgColor, overflow: "hidden" }}>
      <svg
        viewBox="0 0 100 100"
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        preserveAspectRatio="xMidYMid slice"
      >
        <circle cx="50" cy="55" r="35" fill="none" stroke={primaryColor} strokeWidth="0.5" opacity={0.2 * intensity} />
        <circle cx="50" cy="55" r="28" fill="none" stroke={accentColor} strokeWidth="0.3" opacity={0.15 * intensity} />
        {Array.from({ length: 9 }, (_, i) => {
          const ang = (-120 + i * 30) * (Math.PI / 180);
          const x1 = 50 + Math.cos(ang) * 26;
          const y1 = 55 + Math.sin(ang) * 26;
          const x2 = 50 + Math.cos(ang) * 30;
          const y2 = 55 + Math.sin(ang) * 30;
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={primaryColor} strokeWidth="0.8" opacity={0.4 * intensity} />;
        })}
        <line x1="50" y1="55" x2={needleX} y2={needleY} stroke={accentColor} strokeWidth="1.2" opacity={0.7 * intensity} strokeLinecap="round" />
        <circle cx="50" cy="55" r="2.5" fill={primaryColor} opacity={0.5 * intensity} />
      </svg>
    </div>
  );
};
