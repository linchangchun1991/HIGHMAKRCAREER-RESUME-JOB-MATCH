import Sidebar from '@/components/layout/Sidebar';

export default function RecruiterLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar type="recruiter" />
      <main className="flex-1 p-8 overflow-auto">
        {children}
      </main>
    </div>
  );
}
