import { FormEvent, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { accountsApi } from "../../api/accounts";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useToast } from "../../hooks/useToast";

export default function ResetPassword() {
  const { token: tokenParam } = useParams();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [token, setToken] = useState(tokenParam ?? "");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await accountsApi.resetPassword(token, password);
      toast("Password updated. Sign in with the new password.", "success");
      navigate("/auth/login");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Reset failed", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack spacing={2} component="form" onSubmit={handleSubmit}>
      <Typography variant="h2">Choose a new password</Typography>
      <Input label="Reset token" value={token} onChange={(event) => setToken(event.target.value)} required />
      <Input label="New password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
      <Button type="submit" disabled={!loading} fullWidth>
        {loading ? "Updating..." : "Update password"}
      </Button>
      <Typography variant="body2">
        <Link to="/auth/login">Back to sign in</Link>
      </Typography>
    </Stack>
  );
}
