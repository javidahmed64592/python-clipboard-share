import type { Metadata } from "next";

import "./globals.css";
import Footer from "@/components/Footer";
import Navigation from "@/components/Navigation";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Python Clipboard Share",
  description:
    "A lightweight FastAPI application to share text across devices.",
  keywords: ["fastapi", "python"],
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  // icons: {
  //   icon: [
  //     { url: "/icon.png", sizes: "192x192", type: "image/png" },
  //     { url: "/icon-512.png", sizes: "512x512", type: "image/png" },
  //   ],
  //   apple: [{ url: "/apple-icon.png", sizes: "180x180", type: "image/png" }],
  //   other: [
  //     {
  //       rel: "android-chrome",
  //       url: "/android-icon-192x192.png",
  //       sizes: "192x192",
  //     },
  //   ],
  // },
  // manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <div className="min-h-screen bg-background">
            <Navigation />
            <main className="container mx-auto px-4 py-4 pb-16">
              {children}
            </main>
            <Footer />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
