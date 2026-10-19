import TextField from "@mui/materail/TextField";
import type { TextFieldProps } from "@mui/material/TextField";

export function Textarea({ label, minRows = 4, fullWidth = true, ...props }: Omit<TextFieldProps, "variant" | "multiline">) {
  return <TextField label={label} fullWidth={fullWidth} multiline minRows={minRows} {...props} />;
}
