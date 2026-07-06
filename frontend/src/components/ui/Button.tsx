import type { LucideIcon } from "lucide-react";
import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "purple";
type ButtonSize = "default" | "small" | "icon";

interface BaseButtonProps {
  children?: ReactNode;
  className?: string;
  icon?: LucideIcon;
  size?: ButtonSize;
  variant?: ButtonVariant;
}

interface LinkButtonProps extends BaseButtonProps {
  href: string;
  "aria-label"?: string;
}

interface NativeButtonProps extends BaseButtonProps, ButtonHTMLAttributes<HTMLButtonElement> {
  href?: never;
}

type Props = LinkButtonProps | NativeButtonProps;

export function Button({
  children,
  className = "",
  icon: Icon,
  size = "default",
  variant = "secondary",
  ...props
}: Props) {
  const classes = ["button", variant, size === "small" ? "small" : "", size === "icon" ? "icon-button" : "", className]
    .filter(Boolean)
    .join(" ");
  const iconSize = size === "small" ? 14 : 16;
  const content = (
    <>
      {Icon && <Icon aria-hidden="true" size={iconSize} />}
      {children}
    </>
  );

  if ("href" in props && props.href) {
    const { href, ...linkProps } = props;

    return (
      <Link className={classes} href={href} {...linkProps}>
        {content}
      </Link>
    );
  }

  return (
    <button className={classes} type="button" {...props}>
      {content}
    </button>
  );
}
