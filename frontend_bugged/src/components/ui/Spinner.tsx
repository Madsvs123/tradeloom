import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";

export function Spinner() 
  return <CircularProgress size={28} />;
}

export function PageSpinner() {
  return (
    <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 240 }}>
      <CircularProgress />
    </Box>
  );
}
