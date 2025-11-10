
import { Bell, UserCircle, Search } from "lucide-react";
import { ThemeToggle } from "../../../components/theme-toggle";
import { Input } from "../../../components/ui/input";

export default function StoreTopbar() {

  return (
    <header className="w-full h-14 bg-background/95 backdrop-blur-sm border-b border-border flex items-center px-4 justify-between">
      {/* Search */}
      <div className="flex-1 max-w-sm">
       <div className="relative">
         <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
         <Input
           placeholder="Search..."
           className="pl-9 h-9 text-sm border-none bg-accent/50 focus-visible:ring-1"
         />
       </div>
      </div>

      {/* Right side: Notifications & Profile */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Notifications */}
        <button className="relative p-2 hover:bg-accent rounded-md transition-colors">
          <Bell className="text-muted-foreground w-4 h-4" />
          <span className="absolute top-1 right-1 bg-primary text-primary-foreground text-[10px] rounded-full w-4 h-4 flex items-center justify-center font-medium">3</span>
        </button>

        {/* Profile Dropdown */}
        <div className="flex items-center gap-2 cursor-pointer hover:bg-accent px-2 py-1.5 rounded-md transition-colors">
          <span className="w-7 h-7 bg-primary/10 rounded-full flex items-center justify-center">
            <UserCircle className="w-5 h-5 text-primary" />
          </span>
          <span className="text-sm font-medium text-foreground hidden md:block">Admin</span>
        </div>
      </div>
    </header>
  );
}