import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";

export function Select({
  label,
  value,
  onChange,
  children,
  options,
  ...props
}: {
  label?: string;
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  children?: React.ReactNode;
  options?: { value: string; label: string }[];
} & Omit<React.ComponentProps<typeof TextField>, "select" | "onChange">) {
  return (
    <TextField select fullWidth size="small" label={label} value={value || ""} onChange={onChange} {...props}>
      {options
        ? options.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))
        : children}
    </TextField>
  );
}
