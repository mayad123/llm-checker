export const metadata = {
  title: 'LLM Fact Checker',
  description: 'Paste ChatGPT, Claude, or any LLM response and get instant fact-checking with verified sources',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
