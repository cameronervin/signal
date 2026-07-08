export const routes = {
  requestDemo: "/request-demo",
  dashboard: "/dashboard",
  leads: "/leads",
  leadDetail: (leadId: string) => `/leads/${leadId}`,
  agents: "/agents",
  agentRunDetail: (runId: string) => `/agents/${runId}`
} as const;
