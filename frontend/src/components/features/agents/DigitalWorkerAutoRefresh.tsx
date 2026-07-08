"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface Props {
  enabled?: boolean;
  intervalMs?: number;
}

export function DigitalWorkerAutoRefresh({ enabled = true, intervalMs = 8000 }: Props) {
  const router = useRouter();

  useEffect(() => {
    if (!enabled) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        router.refresh();
      }
    }, intervalMs);

    return () => window.clearInterval(intervalId);
  }, [enabled, intervalMs, router]);

  return null;
}
