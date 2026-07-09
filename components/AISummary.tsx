export default function AISummary({ text }: { text?: string }) {
  if (!text) return null;
  return (
    <div className="mt-3 rounded-xl bg-surface p-3">
      <p className="flex items-center gap-1.5 text-xs font-semibold text-brand">
        <span aria-hidden>💡</span> Kenapa tren?
      </p>
      <p className="mt-1 text-sm leading-relaxed text-gray-700">{text}</p>
    </div>
  );
}
