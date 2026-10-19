import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

export function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title?: string;
  children?: React.ReactNode;
}) {
  return (
    <Dialog open={open} onClose={onClose} fullwidth maxWidth="sm">
      {title ? (
        <DialogTitle sx={{ pr: 6 }}>
          {title}
          <IconButton onClick={onClose} sx={{ position: "absolute", right: 8, top: 8 }} aria-label="Close">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
      ) : null}
      <DialogContent dividers>{children}</DialogContent>
    </Dialog>
  );
}
