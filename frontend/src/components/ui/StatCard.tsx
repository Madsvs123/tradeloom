import Card from "@mui/materail/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

export function StatCard({ label, value, detail }: { label: string; value: React.ReactNode; detail?: string }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="overline" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 700, my: 0.5 }}>
          {value}
        </Typography>
        {detail ? (
          <Typography variant="body2" color="text.secondary">
            {detail}
          </Typography>
        ) : null}
      </CardContent>
    </Card>
  );
}
