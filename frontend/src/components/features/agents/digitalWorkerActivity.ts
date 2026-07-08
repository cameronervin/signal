import type {
  DigitalWorkerAssignmentDetail,
  DigitalWorkerDraftEmail,
  DigitalWorkerMessageDto
} from "@/types/digital-workforce";
import type { SourceFact } from "@/types/lead";

export interface TimelineEmail {
  id: string;
  label: string;
  subject: string;
  body: string;
  sources: SourceFact[];
  occurredAt?: string | null;
}

export interface ActivityTimelineEvent {
  id: string;
  title: string;
  detail: string;
  occurredAt?: string | null;
  email?: TimelineEmail;
}

export function buildActivityEvents(assignment: DigitalWorkerAssignmentDetail): ActivityTimelineEvent[] {
  const draftEmail = timelineEmailFromDraft(assignment.draftEmail);
  const events: ActivityTimelineEvent[] = assignment.activityLog.map((activity, index) => ({
    id: `activity-${index}`,
    title: activityTitle(activity),
    detail: activityDetail(activity),
    email: draftEmail && isEmailActivity(activity) ? draftEmail : undefined
  }));
  const hasLinkedEmailEvent = events.some((event) => Boolean(event.email));
  const firstOutboundMessage = assignment.messages.find((message) => message.direction === "outbound");

  if (draftEmail && !hasLinkedEmailEvent) {
    events.push({
      id: "draft-email-link",
      title: "Drafted email linked",
      detail: "This worker activity is tied back to the reviewed lead-intelligence draft.",
      occurredAt: firstOutboundMessage?.created_at,
      email: draftEmail
    });
  }

  if (!draftEmail) {
    events.push(...outboundMessageEvents(assignment.messages));
  }

  return events;
}

export function communicationForStep(
  assignment: DigitalWorkerAssignmentDetail,
  stepName: string,
  index: number
): TimelineEmail | undefined {
  const normalized = stepName.toLowerCase();
  const outboundMessages = assignment.messages.filter((message) => message.direction === "outbound");
  const inboundMessages = assignment.messages.filter((message) => message.direction === "inbound");

  if (index === 0 || normalized.includes("initial") || normalized.includes("outreach")) {
    return timelineEmailFromDraft(assignment.draftEmail) ?? timelineEmailFromMessage(outboundMessages[0]);
  }

  if (normalized.includes("reply")) {
    return timelineEmailFromMessage(inboundMessages[0]);
  }

  if (normalized.includes("follow") || normalized.includes("objection")) {
    return timelineEmailFromMessage(outboundMessages[1]);
  }

  return undefined;
}

export function timelineEmailFromDraft(draft: DigitalWorkerDraftEmail | null | undefined): TimelineEmail | undefined {
  return draft
    ? {
        id: draft.id,
        label: "Drafted email",
        subject: draft.subject,
        body: draft.body,
        sources: draft.sources
      }
    : undefined;
}

function outboundMessageEvents(messages: DigitalWorkerMessageDto[]): ActivityTimelineEvent[] {
  return messages
    .filter((message) => message.direction === "outbound")
    .map((message): ActivityTimelineEvent => ({
      id: `message-${message.message_id}`,
      title: "Outreach email linked",
      detail: "The worker connected this activity item to an outbound email record.",
      occurredAt: message.created_at,
      email: timelineEmailFromMessage(message)
    }))
    .filter((event) => Boolean(event.email));
}

function timelineEmailFromMessage(message: DigitalWorkerMessageDto | undefined): TimelineEmail | undefined {
  return message
    ? {
        id: message.message_id,
        label: message.direction === "inbound" ? "Inbound email" : "Outreach email",
        subject: message.subject,
        body: message.body,
        sources: [],
        occurredAt: message.created_at
      }
    : undefined;
}

function isEmailActivity(activity: string) {
  return /\b(draft|email|outreach|message)\b/i.test(activity);
}

function activityTitle(activity: string) {
  const [prefix] = activity.split(":");
  return prefix ? titleize(prefix) : "Worker update";
}

function activityDetail(activity: string) {
  const [, ...detail] = activity.split(":");
  return detail.join(":").trim() || activity;
}

function titleize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace("Sdr", "SDR");
}
