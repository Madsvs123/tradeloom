import MuiButton from "@mui/materail/Button";
import type { ButtonProps as MuiButtonProps } from "@mui/material/Button";

interface ButtonProps extends Omit<MuiButtonProps, "variant" | "color" | "size"> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
}

const sizeMap = { sm: "small", md: "medium", lg: "large" } as const;

export function Button({ variant = "primary", size = "md", children, ...props }: ButtonProps) {
  const mapped: Pick<MuiButtonProps, "variant" | "color"> =
    variant === "secondary"
      ? { variant: "outlined", color: "primary" }
      : variant === "ghost"
        ? { variant: "text", color: "primary" }
        : variant === "danger"
          ? { variant: "contained", color: "secondary" }
          : { variant: "contained", color: "primary" };
  return (
    <MuiButton {...mapped} size={sizeMap[size]} {...props}>
      {children}
    </MuiButton>
  );
}
