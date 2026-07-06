import { AlertTriangle, Inbox, WifiOff } from "lucide-react";
import type { ReactNode } from "react";

type Tone = "neutral" | "warning" | "danger";

interface Props {
  action?: ReactNode;
  description: string;
  eyebrow?: string;
  title: string;
  tone?: Tone;
}

const toneIcon = {
  neutral: Inbox,
  warning: WifiOff,
  danger: AlertTriangle
} satisfies Record<Tone, typeof AlertTriangle>;

export function StateNotice({ action, description, eyebrow, title, tone = "neutral" }: Props) {
  const Icon = toneIcon[tone];

  return (
    <section aria-label={title} className={`state-notice ${tone}`} role="status">
      <div className="empty-icon">
        <Icon aria-hidden="true" size={26} />
      </div>
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {action && <div className="state-notice-actions">{action}</div>}
    </section>
  );
}
