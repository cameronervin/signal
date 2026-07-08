"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import {
  createDigitalWorkerAssignment,
  pauseDigitalWorkerAssignment,
  recordDigitalWorkerInboundEmail,
  resumeDigitalWorkerAssignment
} from "@/lib/api/endpoints/digital-workforce";
import { routes } from "@/lib/constants/routes";

export async function createDigitalWorkerAssignmentAction(formData: FormData) {
  const leadId = requireFormValue(formData, "leadId");
  const assignment = await createDigitalWorkerAssignment(leadId);

  revalidatePath(routes.digitalWorkforce);
  revalidatePath(routes.leadDetail(leadId));
  redirect(routes.digitalWorkerProgress(assignment.assignment_id));
}

export async function pauseDigitalWorkerAssignmentAction(formData: FormData) {
  const assignmentId = requireFormValue(formData, "assignmentId");
  const leadId = optionalFormValue(formData, "leadId");

  await pauseDigitalWorkerAssignment(assignmentId);
  revalidateAssignmentPaths(assignmentId, leadId);
  redirect(routes.digitalWorkerProgress(assignmentId));
}

export async function resumeDigitalWorkerAssignmentAction(formData: FormData) {
  const assignmentId = requireFormValue(formData, "assignmentId");
  const leadId = optionalFormValue(formData, "leadId");

  await resumeDigitalWorkerAssignment(assignmentId);
  revalidateAssignmentPaths(assignmentId, leadId);
  redirect(routes.digitalWorkerProgress(assignmentId));
}

export async function recordDigitalWorkerInboundEmailAction(formData: FormData) {
  const assignmentId = requireFormValue(formData, "assignmentId");
  const leadId = optionalFormValue(formData, "leadId");
  const externalMessageId = optionalFormValue(formData, "externalMessageId");
  const subject = requireFormValue(formData, "subject");
  const body = requireFormValue(formData, "body");

  await recordDigitalWorkerInboundEmail(assignmentId, {
    external_message_id: externalMessageId,
    received_at: new Date().toISOString(),
    subject,
    body
  });
  revalidateAssignmentPaths(assignmentId, leadId);
  redirect(routes.digitalWorkerProgress(assignmentId));
}

function revalidateAssignmentPaths(assignmentId: string, leadId: string | null) {
  revalidatePath(routes.digitalWorkforce);
  revalidatePath(routes.digitalWorkerProgress(assignmentId));
  if (leadId) {
    revalidatePath(routes.leadDetail(leadId));
  }
}

function requireFormValue(formData: FormData, key: string) {
  const value = optionalFormValue(formData, key);
  if (!value) {
    throw new Error(`Missing ${key}`);
  }
  return value;
}

function optionalFormValue(formData: FormData, key: string) {
  const value = formData.get(key);
  return typeof value === "string" && value.trim() ? value.trim() : null;
}
