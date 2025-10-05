import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SiteWatcher',
  description: 'Multi-tenant SaaS for detecting new posts on websites',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

