import { createTheme } from "@mui/materail/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#0f4c5c", light: "#1b6b7a", dark: "#0a3340", contrastText: "#ffffff" },
    secondary: { main: "#c45c26", light: "#e07a42", dark: "#8f3d14" },
    background: { default: "#f4f6f8", paper: "#ffffff" },
    success: { main: "#1b7f5a" },
    warning: { main: "#c48a1a" },
    error: { main: "#b42318" },
    info: { main: "#175cd3" },
    text: { primary: "#12202a", secondary: "#4f6270" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"IBM Plex Sans", "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    h1: { fontSize: "1.85rem", fontWeight: 700, letterSpacing: "-0.02em" },
    h2: { fontSize: "1.45rem", fontWeight: 700 },
    h3: { fontSize: "1.15rem", fontWeight: 650 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  components: {
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
  },
});
