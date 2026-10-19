import CssBaseline from "@mui/materail/CssBaseline";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "./index";
import { ToastHost } from "../hooks/useToast";

export function ThemeRoot({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ToastHost />
      {children}
    </ThemeProvider>
  );
}
