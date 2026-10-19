import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";
import { commerceStore } from "../../store/commerceStore";

export default function Login() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/dashboard";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    
    setLoading(true);
    try {
      await login(email, password);
      void commerceStore.loadCart();
      toast("Welcome back to TradeLoom", "success");
      navigate(from, { replace: true });
    } catch (err) {
      toast(err instanceof Error ? err.message : "Invalid email or password", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack spacing={2.5} component="form" onSubmit={handleSubmit}>
      <div>
        <Typography variant="h2">Sign in to TradeLoom</Typography>
        <Typography color="text.secondary">Buyer, supplier, and operator access to the commercial network.</Typography>
      </div>
      <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target)} required />
      <Input label="Password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
      <Button type="submit" disabled={loading} fullWidth>
        {loading ? "Signing in..." : "Sign in"}
      </Button>
      <Typography variant="body2">
        <Link to="/auth/forgot-password">Forgot password?</Link>
      </Typography>
      <Typography variant="body2" color="text.secondary">
        New company? <Link to="/auth/register">Create an account</Link>
      </Typography>
    </Stack>
  );
}
