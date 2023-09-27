
with Langkit_Support;
with Langkit_Support.Diagnostics;
with Langkit_Support.Slocs;
with Langkit_Support.Text;

package Librflxlang is

   Version    : constant String := "0.13.1.dev35+gca7f2ee9a";
   Build_Date : constant String := "undefined";

   --  Librflxlang's main entry point is the Librflxlang.Analysis
   --  package.

   --  Convenience renaming for support package that Langkit provides

   package Support renames Langkit_Support;
   package Diagnostics renames Support.Diagnostics;
   package Slocs renames Support.Slocs;
   package Text renames Support.Text;

end;
