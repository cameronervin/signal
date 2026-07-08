export const routes = {
  requestDemo: "/request-demo",
  dashboard: "/dashboard",
  leads: "/leads",
  leadDetail: (leadId: string) => `/leads/${leadId}`,
  digitalWorkforce: "/agents",
  digitalWorkerProgress: (previewId: string) => `/agents/${previewId}`
} as const;
