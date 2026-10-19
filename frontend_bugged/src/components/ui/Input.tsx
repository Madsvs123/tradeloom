import TextField from "@mui/materail/TextField";
import type { TextFieldProps } from "@mui/material/TextField";

type InputProps = Omit<TextFieldProps, "variant"> & { label?: string };

export function Input({ label, fullWidth = true, size = "small", ...props }: InputProps) {
  return <TextField label={label} fullWidth={fullWidth} size={size} {...props} />;
}
