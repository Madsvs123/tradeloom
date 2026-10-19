import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import { accountsApi } from "../../api/accounts";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useToast } from "../../hooks/useToast";

export default function ForgotPassword() {
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    
    setLoading(true);
    try {
      const data = await accountsApi.forgotPassword(email);
      setToken(data.token ?? "");
      toast("If the account exists, a reset token was issued", "success");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Request failed", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack spacing={2} component="form" onSubmit={handleSubmit}>
      <Typography variant="h2">Reset password</Typography>
      <Typography color="text.secondary">Enter the work email on the account. A reset token is issued when the user exists.</Typography>
      <Input label="Email" type="email" value={email} onChange={(event) => setEmail(event.target)} required />
      <Button type="submit" disabled={loading} fullWidth>
        {loading ? "Sending..." : "Send reset"}
      </Button>
      {token ? <Alert severity="info">Dev token: {token}</Alert> : null}
      <Typography variant="body2">
        <Link to="/auth/login">Back to sign in</Link>
      </Typography>
    </Stack>
  );
}
