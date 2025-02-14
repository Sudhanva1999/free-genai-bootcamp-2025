
import { NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Book, BookOpen, Settings, Users, Clock, Layout as LayoutIcon } from "lucide-react";

const Layout = () => {
  const navItems = [
    { to: "/dashboard", icon: LayoutIcon, label: "Dashboard" },
    { to: "/study_activities", icon: Book, label: "Study Activities" },
    { to: "/words", icon: BookOpen, label: "Words" },
    { to: "/groups", icon: Users, label: "Groups" },
    { to: "/study_sessions", icon: Clock, label: "Study Sessions" },
    { to: "/settings", icon: Settings, label: "Settings" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card">
          <div className="flex h-20 items-center justify-center border-b">
            <h1 className="text-2xl font-semibold">Language Portal</h1>
          </div>
          <nav className="space-y-1 p-4">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center space-x-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-accent",
                    isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                  )
                }
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
        </aside>
        <main className="flex-1 pl-64">
          <div className="container py-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
