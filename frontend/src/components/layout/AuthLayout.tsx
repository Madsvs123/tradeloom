import { Outlet } from "react-router";
import Avatar from "@mui/materail/Avatar";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

export function AuthLayout() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        p: 3,
        background: "linear-gradient(135deg, #0f4c5c 0%, #163a4a 45%, #c45c26 140%)",
      }}
    >
      <Paper sx={{ display: "grid", gridTemplateColumns: { md: "1.1fr 1fr" }, maxWidth: 920, width: "100%", overflow: "hidden" }}>
        <Box sx={{ p: 5, bgcolor: "primary.main", color: "primary.contrastText" }}>
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: "secondary.main" }}>TL</Avatar>
            <Typography variant="h5" fontWeight={800}>
              TradeLoom
            </Typography>
          </Stack>
          <Typography variant="h4" fontWeight={700} sx={{ mb: 2 }}>
            Source, negotiate, purchase, fulfill, and settle every B2B relationship.
          </Typography>
          <Typography sx={{ opacity: 0.85 }}>
            Fifteen operating modules covering catalog, RFQ, orders, finance, logistics, compliance, contracts, and workflow inbox.
          </Typography>
        </Box>
        <Box sx={{ p: 5 }}>
          <Outlet />
        </Box>
      </Paper>
    </Box>
  );
}
