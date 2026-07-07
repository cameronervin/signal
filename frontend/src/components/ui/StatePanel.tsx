import Link from "next/link";

import { routes } from "@/lib/constants/routes";

interface Props {
  title: string;
  message: string;
  actionLabel?: string;
  actionHref?: string;
}

export function StatePanel({ title, message, actionLabel = "Back to leads", actionHref = routes.leads }: Props) {
  return (
    <main className="content">
      <section className="surface-card state-panel">
        <h2>{title}</h2>
        <p>{message}</p>
        <Link className="button secondary" href={actionHref}>
          {actionLabel}
        </Link>
      </section>
    </main>
  );
}
