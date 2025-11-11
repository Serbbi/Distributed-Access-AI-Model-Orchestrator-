import AppBar from "@/components/custom-components/app-bar/app-bar";
import SideBar from "@/components/custom-components/side-menu/side-menu";

/** This is the sub-layout used to render the AppBar and SideBar on pages
 * which should support it.
 */
export default function SubLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AppBar />
      <SideBar />
      {children}
    </>
  );
}
