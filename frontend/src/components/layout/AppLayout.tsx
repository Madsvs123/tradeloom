import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Avatar from "@mui/material/Avatar";
import Badge from "@mui/material/Badge";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import InputBase from "@mui/material/InputBase";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Toolbar from "@mui/material/Toolbar";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import BellIcon from "@mui/icons-material/NotificationsNone";
import SearchIcon from "@mui/icons-material/Search";
import LogoutIcon from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import AddIcon from "@mui/icons-material/Add";
import TerminalIcon from "@mui/icons-material/Terminal";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import { Button } from "../ui/Button";
import { CommandPalette } from "./CommandPalette";
import { useAuth } from "../../hooks/useAuth";
import { useStore } from "../../hooks/useStore";
import { commerceStore } from "../../store/commerceStore";
import { sessionStore } from "../../store/sessionStore";

const DRAWER_WIDTH = 268;

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const nav = useStore(sessionStore, (state) => state.nav);
  const unread = useStore(sessionStore, (state) => state.unread);
  const query = useStore(sessionStore, (state) => state.commandQuery);
  const cart = useStore(commerceStore, (state) => state.currentCart);
  const [mobileOpen, setMobileOpen] = useState(false);
  const company = user?.job_title && "Operating company";
  const cartCount = Array.isArray(cart?.items) ? cart.items.length : Number(cart?.item_count ?? 0);

  useEffect(() => {
    void sessionStore.bootstrap();
    void commerceStore.loadCart();
  }, []);

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Toolbar sx={{ gap: 1.5 }}>
        <Avatar sx={{ bgcolor: "primary.main", width: 36, height: 36, fontSize: 14 }}>TL</Avatar>
        <Box>
          <Typography fontWeight={800}>TradeLoom</Typography>
          <Typography variant="caption" color="text.secondary">
            B2B marketplace OS
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ flex: 1, overflow: "auto", px: 1 }}>
        {nav.map((item) => (
          <ListItemButton
            key={`${item.key}-${item.path}`}
            selected={location.pathname === item.path || location.pathname.startsWith(`${item.path}/`)}
            onClick={() => {
              navigate(item.path);
              setMobileOpen(false);
            }}
            sx={{ borderRadius: 1, mb: 0.5 }}
          >
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 600, fontSize: 14 }} />
          </ListItemButton>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2, display: "flex", gap: 1.5, alignItems: "center" }}>
        <Avatar sx={{ width: 32, height: 32 }}>{(user?.first_name || user?.email || "A").slice(0, 1)}</Avatar>
        <Box sx={{ minWidth: 0 }}>
          <Typography noWrap fontWeight={700} fontSize={14}>
            {user ? `${user.first_name} ${user.last_name}`.trim() || user.email : "Account"}
          </Typography>
          <Typography noWrap variant="caption" color="text.secondary">
            {company}
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <CommandPalette />
      <AppBar position="fixed" color="inherit" elevation={0} sx={{ borderBottom: 1, borderColor: "divider", zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar sx={{ gap: 1 }}>
          <IconButton onClick={() => setMobileOpen(true)} sx={{ display: { md: "none" } }}>
            <MenuIcon />
          </IconButton>
          <Paper
            component="form"
            onSubmit={(event) => {
              event.preventDefault();
              navigate(`/search?q=${encodeURIComponent(query)}`);
            }}
            variant="outlined"
            sx={{ display: "flex", alignItems: "center", flex: 1, px: 1, py: 0.25 }}
          >
            <SearchIcon fontSize="small" color="action" />
            <InputBase
              sx={{ ml: 1, flex: 1 }}
              placeholder="Search the network. Ctrl+K jumps modules."
              value={query}
              onChange={(event) => sessionStore.setCommandQuery(event.target.value)}
            />
          </Paper>
          <Tooltip title="Notifications">
            <IconButton onClick={() => navigate("/notifications")}>
              <Badge badgeContent={unread} color="secondary">
                <BellIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Tooltip title="Cart">
            <IconButton onClick={() => navigate("/cart")}>
              <Badge badgeContent={cartCount} color="primary">
                <ShoppingCartIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Button variant="ghost" startIcon={<TerminalIcon />} onClick={() => sessionStore.setCommandOpen(true)}>
            Command
          </Button>
          <Button startIcon={<AddIcon />} onClick={() => navigate("/rfqs/new")}>
            New RFQ
          </Button>
          <IconButton
            onClick={() => {
              logout();
              navigate("/auth/login");
            }}
            aria-label="Sign out"
          >
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: "block", md: "none" }, "& .MuiDrawer-paper": { width: DRAWER_WIDTH } }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{ display: { xs: "none", md: "block" }, "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box", top: 64, height: "calc(100% - 64px)" } }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, mt: 8, width: { md: `calc(100% - ${DRAWER_WIDTH}px)` } }}>
        <Outlet />
      </Box>
    </Box>
  );
}
