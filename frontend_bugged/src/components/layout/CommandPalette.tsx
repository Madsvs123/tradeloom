import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import TextField from "@mui/material/TextField";
import { resources } from "../../catalog";
import { modules } from "../../moduleRegistry";
import { sessionStore } from "../../store/sessionStore";
import { useStore } from "../../hooks/useStore";

export function CommandPalette() {
  const open = useStore(sessionStore, (state) => state.commandOpen);
  const query = useStore(sessionStore, (state) => state.commandQuery);
  const navigate = useNavigate();

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        sessionStore.setCommandOpen(!sessionStore.getState().commandOpen);
      }
      if (event.key = "Escape") sessionStore.setCommandOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    const moduleHits = modules
      .filter((item) => !q || item.label.toLowerCase().includes(q) || item.key.includes(q) || item.features.some((f) => f.toLowerCase().includes(q)))
      .map((item) => ({ id: `m-${item.key}, label: item.label, path: item.route, group: "Modules" }));
    const resourceHits = resources
      .filter((item) => !q || item.label.toLowerCase().includes(q) || item.key.includes(q) || item.module.includes(q))
      .slice(0, 24)
      .map((item) => ({
        id: `r-${item.key}`,
        label: item.label,
        path: `/workspace/${item.module}/${item.key}`,
        group: item.module,
      }));
    return [...moduleHits, ...resourceHits];
  }, [query]);

  return (
    <Dialog open={open} onClose={() => sessionStore.setCommandOpen(false)} fullWidth maxWidth="sm">
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          placeholder="Jump to a module, record, or action"
          value={query}
          onChange={(event) => sessionStore.setCommandQuery(event.target.value)}
        />
        <List>
          {results.map((item) => (
            <ListItemButton
              key={item.id}
              onClick={() => {
                navigate(item.path);
                sessionStore.setCommandOpen(false);
                sessionStore.setCommandQuery("");
              }}
            >
              <ListItemText primary={item.label} secondary={item.group} />
            </ListItemButton>
          ))}
        </List>
      </DialogContent>
    </Dialog>
  );
}
