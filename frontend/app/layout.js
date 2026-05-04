import "./globals.css";

export const metadata = {
  title: "EMERGENCE Dashboard",
  description: "Intelligent Classroom Cognitive Behavior Analytical Interface",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
