import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router";
import Stack from "@mui/materail/Stack";
import Typography from "@mui/material/Typography";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";

export default function Register() {
  const { register } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    job_title: "",
    phone_number: "",
  });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      await register(form);
      toast("Account created", "success");
      navigate("/onboarding");
    } catch (err) {
      toast(err instanceof Error ? err.message : "Unable to register", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Stack spacing={2} component="form" onSubmit={handleSubmit}>
      <Typography variant="h2">Create a TradeLoom account</Typography>
      <Input label="Work email" type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
      <Input label="Password" type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
      <Input label="First name" value={form.first_name} onChange={(event) => setForm({ ...form, first_name: event.target.value })} />
      <Input label="Last name" value={form.last_name} onChange={(event) => setForm({ ...form, last_name: event.target.value })} />
      <Input label="Job title" value={form.job_title} onChange={(event) => setForm({ ...form, job_title: event.target.value })} />
      <Input label="Phone" value={form.phone_number} onChange={(event) => setForm({ ...form, phone_number: event.target.value })} />
      <Button type="submit" disabled={loading} fullWidth>
        {loading ? "Creating..." : "Create account"}
      </Button>
      <Typography variant="body2" color="text.secondary">
        Already registered? <Link to="/auth/login">Sign in</Link>
      </Typography>
    </Stack>
  );
}
