export type DemoMode = "live" | "snapshot";

export function getDemoMode(): DemoMode {
  return process.env.NEXT_PUBLIC_DEMO_MODE === "snapshot" ? "snapshot" : "live";
}

export function isSnapshotMode(): boolean {
  return getDemoMode() === "snapshot";
}

export function isLiveMode(): boolean {
  return getDemoMode() === "live";
}
