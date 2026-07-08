import { LeadSubmissionForm } from "@/components/features/leads/LeadSubmissionForm";

export const metadata = {
  title: "Request a demo · Signal",
  description: "Submit an inbound multifamily leasing lead for Signal review."
};

export default function RequestDemoPage() {
  return <LeadSubmissionForm />;
}
