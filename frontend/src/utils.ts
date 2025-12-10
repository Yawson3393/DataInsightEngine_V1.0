export function formatDate(ts: string | number | Date) {
  const d = new Date(ts)
  return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()} `
    + `${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function formatVoltage(v: number) {
  return (v / 1000).toFixed(3) + ' V'
}

export function formatTemperature(t: number) {
  return t.toFixed(1) + ' ℃'
}

export function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t
}

// 通用颜色映射（蓝 → 绿 → 红）
export function heatColor(value: number, min: number, max: number) {
  const t = (value - min) / (max - min)
  const r = Math.round(255 * t)
  const g = Math.round(255 * (1 - Math.abs(t - 0.5) * 2))
  const b = Math.round(255 * (1 - t))
  return `rgb(${r},${g},${b})`
}
