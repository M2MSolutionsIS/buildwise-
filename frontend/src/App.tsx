import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ConfigProvider, App as AntApp } from "antd";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import roLocale from "antd/locale/ro_RO";
import AppLayout from "./layouts/AppLayout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./modules/crm/pages/DashboardPage";
import ContactsListPage from "./modules/crm/pages/ContactsListPage";
import ContactDetailPage from "./modules/crm/pages/ContactDetailPage";
import ContactCreatePage from "./modules/crm/pages/ContactCreatePage";
import OffersListPage from "./modules/pipeline/pages/OffersListPage";
import OfferBuilderPage from "./modules/pipeline/pages/OfferBuilderPage";
import OfferDetailPage from "./modules/pipeline/pages/OfferDetailPage";
import PipelineBoardPage from "./modules/pipeline/pages/PipelineBoardPage";
import OpportunityDetailPage from "./modules/pipeline/pages/OpportunityDetailPage";
import OpportunityCreatePage from "./modules/pipeline/pages/OpportunityCreatePage";
import SalesDashboardPage from "./modules/pipeline/pages/SalesDashboardPage";
import { useAuthStore } from "./stores/authStore";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={roLocale}
        theme={{
          token: {
            colorPrimary: "#1677ff",
            borderRadius: 6,
          },
        }}
      >
        <AntApp>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route
                path="/"
                element={
                  <RequireAuth>
                    <AppLayout />
                  </RequireAuth>
                }
              >
                <Route index element={<DashboardPage />} />

                {/* CRM Routes */}
                <Route path="crm">
                  <Route index element={<Navigate to="contacts" replace />} />
                  <Route path="contacts" element={<ContactsListPage />} />
                  <Route path="contacts/new" element={<ContactCreatePage />} />
                  <Route path="contacts/:id" element={<ContactDetailPage />} />
                </Route>

                {/* Pipeline Routes */}
                <Route path="pipeline">
                  <Route index element={<Navigate to="board" replace />} />
                  {/* E-009: Kanban Board */}
                  <Route path="board" element={<PipelineBoardPage />} />
                  {/* E-012: Sales Dashboard */}
                  <Route path="dashboard" element={<SalesDashboardPage />} />
                  {/* Opportunities */}
                  <Route path="opportunities/new" element={<OpportunityCreatePage />} />
                  <Route path="opportunities/:id" element={<OpportunityDetailPage />} />
                  {/* Offers (E-005, E-006) */}
                  <Route path="offers" element={<OffersListPage />} />
                  <Route path="offers/new" element={<OfferBuilderPage />} />
                  <Route path="offers/:id" element={<OfferDetailPage />} />
                </Route>

                <Route path="pm" element={<PlaceholderPage title="Project Management" />} />
                <Route path="rm" element={<PlaceholderPage title="Resource Management" />} />
                <Route path="bi" element={<PlaceholderPage title="Business Intelligence" />} />
                <Route path="settings" element={<PlaceholderPage title="Setări" />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AntApp>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div style={{ padding: 48, textAlign: "center" }}>
      <h2>{title}</h2>
      <p style={{ color: "#888" }}>Modul în curs de implementare.</p>
    </div>
  );
}

export default App;
