export const routes = {
  home: "/",
  dashboard: "/dashboard",
  leads: "/leads",
  leadDetail: (leadId: string) => `/leads/${leadId}`,
  agents: "/agents",
  agentRun: (runId: string) => `/agents/${runId}`
} as const;
