export function diagnosisColor(label: string): string {
  const key = label.toLowerCase();
  if (key.includes("bleed")) return "#E5484D";
  if (key.includes("isch")) return "#F5A340";
  if (key.includes("normal")) return "#3FB950";
  return "#8A98A6";
}
