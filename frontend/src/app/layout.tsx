import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "700"],
});

export const metadata: Metadata = {
  title: "Maproom — AI-Powered Travel Orchestrator",
  description: "Multi-agent travel recommendation and group conflict resolution ecosystem built on CrewAI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased scroll-smooth">
      <body className={`${outfit.className} min-h-full flex flex-col`}>
        {children}
      </body>
    </html>
  );
}
