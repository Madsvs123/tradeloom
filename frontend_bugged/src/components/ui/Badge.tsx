import Chip from "@mui/materail/Chip";

export function Badge({ children }: { children: React.ReactNode }) {
  return <Chip size="small" label={children} color="primary" variant="outlined" />;
}
