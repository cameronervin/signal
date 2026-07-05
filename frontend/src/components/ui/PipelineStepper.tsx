import { Check } from "lucide-react";

interface Step {
  name: string;
  status: "done" | "active" | "pending";
  summary: string;
  duration?: string;
  chips?: string[];
}

interface Props {
  steps: Step[];
}

export function PipelineStepper({ steps }: Props) {
  return (
    <ol className="stepper">
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        const connectorDone = step.status === "done" && steps[index + 1]?.status === "done";

        return (
          <li key={`${step.name}-${index}`} className="stepper-step">
            <span className="stepper-rail" aria-hidden="true">
              <span className={`stepper-dot ${step.status}`}>
                {step.status === "done" && <Check size={12} strokeWidth={3} />}
              </span>
              {!isLast && <span className={`stepper-connector ${connectorDone ? "done" : ""}`} />}
            </span>
            <span className="stepper-content">
              <span className="flex items-baseline justify-between gap-3">
                <strong className={step.status === "pending" ? "text-sm text-[var(--ink-400)]" : "text-sm"}>
                  {step.name}
                </strong>
                {step.duration && (
                  <span
                    className={`mono text-[11px] ${
                      step.status === "active" ? "text-[var(--amber-text)]" : "text-[var(--ink-400)]"
                    }`}
                  >
                    {step.duration}
                  </span>
                )}
              </span>
              <span
                className={`mt-2 block text-sm leading-6 ${
                  step.status === "pending" ? "text-[var(--ink-400)]" : "text-[var(--ink-600)]"
                }`}
              >
                {step.summary}
              </span>
              {step.chips && (
                <span className="mt-3 flex flex-wrap gap-1.5">
                  {step.chips.map((chip) => (
                    <span key={chip} className="source-chip border-solid text-[10.5px]">
                      {chip}
                    </span>
                  ))}
                </span>
              )}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
