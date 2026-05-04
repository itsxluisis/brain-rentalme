import type { BlockType } from "@/types/knowledge";

export const BLOCK_TYPE_LABELS: Record<BlockType, string> = {
  description: "Descripción",
  rules: "Normas",
  access_instructions: "Acceso",
  faq: "FAQ",
  sop: "Procedimiento",
  integration_guide: "Guía de integración",
  pricing_notes: "Precios",
  checkin_notes: "Check-in",
  custom: "Personalizado",
};

export const BLOCK_TYPE_COLORS: Record<BlockType, string> = {
  description: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  rules: "bg-red-500/10 text-red-400 border-red-500/20",
  access_instructions: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  faq: "bg-violet-500/10 text-violet-400 border-violet-500/20",
  sop: "bg-teal-500/10 text-teal-400 border-teal-500/20",
  integration_guide: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  pricing_notes: "bg-green-500/10 text-green-400 border-green-500/20",
  checkin_notes: "bg-pink-500/10 text-pink-400 border-pink-500/20",
  custom: "bg-white/5 text-white/55 border-white/10",
};
