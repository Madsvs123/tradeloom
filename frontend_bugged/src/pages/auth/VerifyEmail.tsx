import { FormEvent, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { accountsApi } from "../../api/accounts";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";

export default function VerifyEmail() {
  const { token: tokenParam } = useParams();
  const { refreshUser, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [token, setToken] = useState(tokenParam ?? "");
  const [loading, setLoading] = useState(false);

  async function requestToken() {
    try {
      const data = await accountsApi.requestEmailVerification();
      setToken(data.token);
      toast("Verification token issued", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to request verification", "error");
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await accountsApi.verifyEmail(token);
      await refreshUser();
      toast("Email verified", "success");
      navigate("/dashboard");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Verification failed", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack spacing={2} component="div" onSubmit={handleSubmit}>
      <Typography variant="h2">Verify email</Typography>
      <Typography color="text.secondary">Confirm the work inbox so the company can transact on TradeLoom.</Typography>
      <Input label="Verification token" value={token} onChange={(event) => setToken(event.target.value)} required />
      <Button type="submit" disabled={loading} fullwidth>
        {loading ? "Verifying..." : "Verify email"}
      </Button>
      {isAuthenticated ? (
        <Button type="button" variant="secondary" onClick={() => void requestToken()} fullWidth>
          Request a new token
        </Button>
      ) : null}
    </Stack>
  );
}
