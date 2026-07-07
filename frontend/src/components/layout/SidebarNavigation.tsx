"use client";

import { Home, Inbox, LayoutGrid } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { routes } from "@/lib/constants/routes";
import { cn } from "@/lib/utils/cn";

const navItems = [
  { href: routes.dashboard, label: "Dashboard", icon: Home },
  { href: routes.leads, label: "Inbound leads", icon: Inbox },
  { href: routes.agents, label: "Agents", icon: LayoutGrid }
];

export function SidebarNavigation() {
  const pathname = usePathname();

  return (
    <>
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

        return (
          <Link
            key={item.href}
            aria-current={active ? "page" : undefined}
            aria-label={item.label}
            className={cn("nav-button", active && "active")}
            href={item.href}
          >
            <Icon size={21} />
          </Link>
        );
      })}
    </>
  );
}
