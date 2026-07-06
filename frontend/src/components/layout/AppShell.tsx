"use client";

import { Home, Inbox, LayoutGrid } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/leads", label: "Inbound leads", icon: Inbox },
  { href: "/agents", label: "Agents", icon: LayoutGrid }
];

export function AppShell({ children }: Props) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <Link className="signal-mark" href="/leads" aria-label="Signal home">
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
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              aria-current={active ? "page" : undefined}
              aria-label={item.label}
              className={`nav-button ${active ? "active" : ""}`}
              href={item.href}
            >
              <Icon size={21} />
            </Link>
          );
        })}
        <div className="sidebar-avatar" aria-label="SDR profile">
          SD
        </div>
      </aside>
      <div className="workspace">{children}</div>
    </div>
  );
}
