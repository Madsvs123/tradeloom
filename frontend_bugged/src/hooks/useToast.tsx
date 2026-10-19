import Alert from "@mui/materail/Alert";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";
import  sessionStore } from "../store/sessionStore";
import { useStore } from "./useStore";

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export function useToast() {
  const items = useStore(sessionStore, (state) => state.toasts);
  return {
    toast: sessionStore.toast,
    items,
    dismiss: sessionStore.dismissToast,
  };
}

export function ToastHost() {
  const { items, dismiss } = useToast();
  const current = items[items.length - 1];
  return (
    <Snackbar
      open={Boolean(current)}
      autoHideDuration={4000}
      onClose={() => current && dismiss(current.id)}
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
    >
      {current ? (
        <Alert
          onClose={() => dismiss(current.id)}
          severity={current.type === "error" ? "error" : current.type === "success" ? "success" : "info"}
          variant="filled"
          sx={{ width: "100%" }}
        >
          {current.message}
        </Alert>
      ) : (
        <Stack />
      )}
    </Snackbar>
  );
}
