export default function PageShell({
  title,
  subtitle,
  children
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <article className="mx-auto max-w-2xl py-4">
      <h1 className="text-2xl font-extrabold text-ink sm:text-3xl">{title}</h1>
      {subtitle && <p className="mt-2 text-gray-500">{subtitle}</p>}
      <div className="prose-lagitren mt-6 space-y-4 text-[15px] leading-relaxed text-gray-700">
        {children}
      </div>
    </article>
  );
}
