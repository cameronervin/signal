import { create } from "zustand";

interface UiState {
  selectedLeadId: string | null;
  setSelectedLeadId: (leadId: string | null) => void;
}

export const useUiStore = create<UiState>((set) => ({
  selectedLeadId: null,
  setSelectedLeadId: (leadId) => set({ selectedLeadId: leadId })
}));
