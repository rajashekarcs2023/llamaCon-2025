"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  FileVideo,
  User,
  TimerIcon as Timeline,
  Network,
  MessageSquare,
  Users,
  Menu,
  X,
  Search,
  Home,
} from "lucide-react"

const navItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: Home,
  },
  {
    name: "Video Upload",
    href: "/videos",
    icon: FileVideo,
  },
  {
    name: "Suspect Identification",
    href: "/suspect",
    icon: User,
  },
  {
    name: "Timeline",
    href: "/timeline",
    icon: Timeline,
  },
  {
    name: "Graph View",
    href: "/graph",
    icon: Network,
  },
  {
    name: "Query Panel",
    href: "/query",
    icon: MessageSquare,
  },
  {
    name: "Crew",
    href: "/crew",
    icon: Users,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile sidebar toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X /> : <Menu />}
      </Button>

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 transform bg-card shadow-lg transition-transform duration-200 ease-in-out md:relative md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center border-b px-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="rounded-md bg-detective-primary p-1">
                <Search className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight">ReConstructR</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  pathname === item.href
                    ? "bg-detective-primary text-white"
                    : "text-muted-foreground hover:bg-muted hover:text-white",
                )}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>

          {/* User info */}
          <div className="border-t p-4">
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-full bg-detective-secondary">
                <span className="flex h-full w-full items-center justify-center text-xs font-medium text-white">
                  DI
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">Detective Inspector</p>
                <p className="text-xs text-muted-foreground">Metropolitan Police</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
