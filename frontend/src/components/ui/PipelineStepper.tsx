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
                <strong className={step.status === "pending" ? "text-sm text-soft" : "text-sm"}>
                  {step.name}
                </strong>
                {step.duration && (
                  <span
                    className={`mono text-xs ${
                      step.status === "active" ? "text-warning" : "text-soft"
                    }`}
                  >
                    {step.duration}
                  </span>
                )}
              </span>
              <span
                className={`mt-2 block text-sm leading-6 ${
                  step.status === "pending" ? "text-soft" : "text-muted"
                }`}
              >
                {step.summary}
              </span>
              {step.chips && (
                <span className="mt-3 flex flex-wrap gap-1.5">
                  {step.chips.map((chip) => (
                    <span key={chip} className="source-chip solid">
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
