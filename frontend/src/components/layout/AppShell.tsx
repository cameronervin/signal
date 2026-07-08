import Link from "next/link";
import type { ReactNode } from "react";

import { SidebarNavigation } from "@/components/layout/SidebarNavigation";
import { routes } from "@/lib/constants/routes";

interface Props {
  children: ReactNode;
}

export function AppShell({ children }: Props) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <Link className="signal-mark" href={routes.leads} aria-label="Signal home">
          <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 15.5c3.2 0 3.2-7 6.4-7s3.2 7 6.4 7"
              stroke="currentColor"
              strokeLinecap="round"
              strokeWidth="2.2"
            />
            <circle cx="19.4" cy="6" fill="currentColor" r="2.1" />
          </svg>
        </Link>
        <SidebarNavigation />
        <div className="sidebar-avatar" aria-label="SDR profile">
          CE
        </div>
      </aside>
      <div className="workspace">{children}</div>
    </div>
  );
}
