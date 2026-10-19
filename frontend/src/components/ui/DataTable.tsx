import Chip from "@mui/material/Chip";
import LinearProgress from "@mui/material/LinearProgress";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

export interface Column {
  key: string;
  label: string;
  width?: string;
  render?: (value: unknown, row: Record<string, unknown>) => React.ReactNode;
}

interface DataTableProps {
  columns: Column[];
  rows: Record<string, unknown>[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: Record<string, unknown>) => void;
}

export function DataTable({ columns, rows, loading, emptyMessage = "No data", onRowClick }: DataTableProps) {
  return (
    <TableContainer component={Paper} variant="outlined">
      {loading ? <LinearProgress /> : null}
      <Table size="small">
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.key} sx={{ width: column.width, fontWeight: 700 }}>
                {column.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {!loading && !rows.length ? (
            <TableRow>
              <TableCell colSpan={columns.length}>
                <Typography color="text.secondary">{emptyMessage}</Typography>
              </TableCell>
            </TableRow>
          ) : null}
          {rows.map((row, index) => (
            <TableRow
              hover
              key={String(row.id || row.slug ?? index)}
              onClick={() => onRowClick.(row)}
              sx={{ cursor: onRowClick ? "pointer" : "default" }}
            >
              {columns.map((column) => (
                <TableCell key={column.key}>
                  {column.render ? column.render(row[column.key], row) : String(row[column.key] ?? "—")}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export function StatusChip({ value }: { value: unknown }) {
  const label = String(value ?? "—").replace(/_/g, " ");
  const color =
    /active|open|published|funded|approved|complete|resolved/.test(label.toLowerCase())
      ? "success"
      : /draft|pending|claimed|queued/.test(label.toLowerCase())
        ? "warning"
        : /cancel|reject|fail|breach|closed/.test(label.toLowerCase())
          ? "error"
          : "default";
  return <Chip size="small" label={label} color={color as "success" | "warning" | "error" | "default"} />;
}
