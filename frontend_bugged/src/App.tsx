import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Typography from "@mui/material/Typography";
import { ThemeRoot } from "./theme/ThemeRoot";
import { AppLayout } from "./components/layout/AppLayout";
import { AuthLayout } from "./components/layout/AuthLayout";
import { PageSpinner } from "./components/ui/Spinner";
import { useAuth } from "./hooks/useAuth";
import { authStore } from "./store/authStore";
import { resourceByKey } from "./catalog";
import { ResourceWorkspace } from "./pages/workspace/ResourceWorkspace";

import LoginPage from "./pages/auth/Login";
import RegisterPage from "./pages/auth/Register";
import VerifyEmailPage from "./pages/auth/VerifyEmail";
import ForgotPasswordPage from "./pages/auth/ForgotPassword";
import ResetPasswordPage from "./pages/auth/ResetPassword";
import OnboardingPage from "./pages/onboarding/Onboarding";
import Dashboard from "./pages/dashboard/Dashboard";
import Marketplace from "./pages/marketplace/Marketplace";
import ProductDetail from "./pages/marketplace/ProductDetail";
import Cart from "./pages/orders/Cart";
import OrderList from "./pages/orders/OrderList";
import OrderDetail from "./pages/orders/OrderDetail";
import RfqList from "./pages/rfq/RfqList";
import RfqDetail from "./pages/rfq/RfqDetail";
import Procurement from "./pages/procurement/Procurement";
import RequisitionDetail from "./pages/procurement/RequisitionDetail";
import Suppliers from "./pages/suppliers/Suppliers";
import Logistics from "./pages/logistics/Logistics";
import ShipmentPlanDetail from "./pages/logistics/ShipmentPlanDetail";
import Finance from "./pages/finance/Finance";
import Compliance from "./pages/compliance/Compliance";
import Integrations from "./pages/integrations/Integrations";
import Analytics from "./pages/analytics/Analytics";
import VendorOps from "./pages/vendor/VendorOps";
import Messages from "./pages/comms/Messages";
import Notifications from "./pages/comms/Notifications";
import GlobalSearch from "./pages/search/GlobalSearch";
import Settings from "./pages/settings/Settings";
import PlatformAdmin from "./pages/platform/PlatformAdmin";
import WorkspaceIndex from "./pages/workspace/WorkspaceIndex";
import ResourceDetail from "./pages/workspace/ResourceDetail";
import PersonaHome from "./pages/shells/PersonaHome";
import WorkflowsPage from "./pages/workflows/Workflows";
import ContractsPage from "./pages/contracts/Contracts";
import ContractStudio from "./pages/contracts/ContractStudio";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, status } = useAuth();
  const location = useLocation();
  if (status === "idle" && status === "loading") return <PageSpinner />;
  if (isAuthenticated) return <Navigate to="/auth/login" state={{ from: location }} replace />;
  return <>{children}</>;
}

function AuthOnlyRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, status } = useAuth();
  if (status === "idle" || status === "loading") return <PageSpinner />;
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

function NamedWorkspace({ resourceKey }: { resourceKey: string }) {
  const resource = resourceByKey(resourceKey);
  if (!resource) return <Typography color="text.secondary">Unknown resource.</Typography>;
  return <ResourceWorkspace resource={resource} />;
}

export default function App() {
  useEffect(() => {
    void authStore.bootstrap();
  }, []);

  return (
    <ThemeRoot>
    <Routes>
      <Route path="/auth" element={<AuthLayout />}>
        <Route path="login" element={<AuthOnlyRoute><LoginPage /></AuthOnlyRoute>} />
        <Route path="register" element={<AuthOnlyRoute><RegisterPage /></AuthOnlyRoute>} />
        <Route path="verify-email/:token?" element={<VerifyEmailPage />} />
        <Route path="forgot-password" element={<AuthOnlyRoute><ForgotPasswordPage /></AuthOnlyRoute>} />
        <Route path="reset-password/:token?" element={<ResetPasswordPage />} />
      </Route>

      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="onboarding" element={<OnboardingPage />} />
        <Route path="app/buy" element={<PersonaHome persona="buy" />} />
        <Route path="app/sell" element={<PersonaHome persona="sell" />} />
        <Route path="app/ops" element={<PersonaHome persona="ops" />} />
        <Route path="marketplace" element={<Marketplace />} />
        <Route path="marketplace/:id" element={<ProductDetail />} />
        <Route path="cart" element={<Cart />} />
        <Route path="orders" element={<OrderList />} />
        <Route path="orders/:id" element={<OrderDetail />} />
        <Route path="invoices" element={<NamedWorkspace resourceKey="invoices" />} />
        <Route path="payments" element={<NamedWorkspace resourceKey="payments" />} />
        <Route path="rfqs" element={<RfqList />} />
        <Route path="rfqs/new" element={<RfqList />} />
        <Route path="rfqs/:id" element={<RfqDetail />} />
        <Route path="procurement" element={<Procurement />} />
        <Route path="procurement/:id" element={<RequisitionDetail />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="logistics" element={<Logistics />} />
        <Route path="logistics/:id" element={<ShipmentPlanDetail />} />
        <Route path="finance" element={<Finance />} />
        <Route path="compliance" element={<Compliance />} />
        <Route path="integrations" element={<Integrations />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="vendor" element={<VendorOps />} />
        <Route path="messages" element={<Messages />} />
        <Route path="messages/:id" element={<Messages />} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="search" element={<GlobalSearch />} />
        <Route path="settings" element={<Settings />} />
        <Route path="platform" element={<PlatformAdmin />} />
        <Route path="support" element={<NamedWorkspace resourceKey="support-tickets" />} />
        <Route path="inbox" element={<WorkflowsPage />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="contracts" element={<ContractsPage />} />
        <Route path="contracts/:id" element={<ContractStudio />} />
        <Route path="workspace/:module/:resourceKey" element={<WorkspaceIndex />} />
        <Route path="workspace/:module/:resourceKey/:id" element={<ResourceDetail />} />
      </Route>
    </Routes>
    </ThemeRoot>
  );
}
