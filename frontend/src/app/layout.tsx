import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Content Repurposer | AI-Powered Content Transformation",
  description: "Transform your content into summaries and social media posts using AI. Extract YouTube transcripts, generate summaries, and create platform-specific social media content with customizable length and tone.",
  keywords: ["content repurposing", "AI summarization", "social media content", "YouTube transcript", "content transformation", "AI writing"],
  authors: [{ name: "Justin Han" }],
  openGraph: {
    title: "Content Repurposer | AI-Powered Content Transformation",
    description: "Transform your content into summaries and social media posts using AI. Extract YouTube transcripts, generate summaries, and create platform-specific social media content.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
