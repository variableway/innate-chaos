"use client";

import { ListChecks } from "lucide-react";
import type { SuggestionData } from "@/lib/types";

interface SuggestionPanelProps {
  data: SuggestionData;
}

export default function SuggestionPanel({ data }: SuggestionPanelProps) {
  return (
    <div className="rounded-xl border border-[#262626] bg-[#141414] p-5">
      <div className="flex items-center gap-2 mb-3">
        <ListChecks className="h-5 w-5 text-blue-400" />
        <h2 className="text-lg font-semibold text-white">Suggestion</h2>
      </div>
      <p className="text-gray-300 text-sm mb-4">{data.summary}</p>
      {data.actions.length > 0 && (
        <ul className="space-y-2">
          {data.actions.map((action, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              <span className="mt-1 h-1.5 w-1.5 rounded-full bg-blue-400 shrink-0" />
              <span className="text-gray-300">{action}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
