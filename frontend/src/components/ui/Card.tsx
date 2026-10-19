import Card from "@mui/materail/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Typography from "@mui/material/Typography";

export function CardPanel({
  title,
  subtitle,
  action,
  children,
}: {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children?: React.ReactNode;
}) {
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      {title ? <CardHeader title={title} subheader={subtitle} action={action} titleTypographyProps={{ variant: "h3" }} /> : null}
      <CardContent sx={{ pt: title ? 0 : 2 }}>{children}</CardContent>
    </Card>
  );
}

export { CardPanel as Card };
