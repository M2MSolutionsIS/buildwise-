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
import ActivityPlannerPage from "./modules/pipeline/pages/ActivityPlannerPage";
import GanttChartPage from "./modules/pm/pages/GanttChartPage";
import TimesheetPage from "./modules/pm/pages/TimesheetPage";
import MaterialConsumptionPage from "./modules/pm/pages/MaterialConsumptionPage";
import SubcontractorsPage from "./modules/pm/pages/SubcontractorsPage";
import DeliveriesPage from "./modules/pm/pages/DeliveriesPage";
import DailyReportPage from "./modules/pm/pages/DailyReportPage";
import ProgressMonitoringPage from "./modules/pm/pages/ProgressMonitoringPage";
import BudgetControlPage from "./modules/pm/pages/BudgetControlPage";
import WorkSituationsPage from "./modules/pm/pages/WorkSituationsPage";
import RiskRegisterPage from "./modules/pm/pages/RiskRegisterPage";
import ReceptionPunchListPage from "./modules/pm/pages/ReceptionPunchListPage";
import WarrantyTrackingPage from "./modules/pm/pages/WarrantyTrackingPage";
import EnergyImpactPage from "./modules/pm/pages/EnergyImpactPage";
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
                  {/* E-011: Activity Planner */}
                  <Route path="activities" element={<ActivityPlannerPage />} />
                  {/* Offers (E-005, E-006) */}
                  <Route path="offers" element={<OffersListPage />} />
                  <Route path="offers/new" element={<OfferBuilderPage />} />
                  <Route path="offers/:id" element={<OfferDetailPage />} />
                </Route>

                {/* PM Routes — E-016 Gantt, E-018 Timesheet, E-019 Consum, F075, F077 */}
                <Route path="pm">
                  <Route index element={<PlaceholderPage title="Project Management" />} />
                  <Route path="projects/:projectId/gantt" element={<GanttChartPage />} />
                  <Route path="projects/:projectId/timesheet" element={<TimesheetPage />} />
                  <Route path="projects/:projectId/consumption" element={<MaterialConsumptionPage />} />
                  <Route path="projects/:projectId/subcontractors" element={<SubcontractorsPage />} />
                  <Route path="projects/:projectId/deliveries" element={<DeliveriesPage />} />
                  <Route path="projects/:projectId/daily-reports" element={<DailyReportPage />} />
                  {/* Task 16: Monitoring — F078, F079, F080, F084 */}
                  <Route path="projects/:projectId/progress" element={<ProgressMonitoringPage />} />
                  <Route path="projects/:projectId/budget" element={<BudgetControlPage />} />
                  <Route path="projects/:projectId/work-situations" element={<WorkSituationsPage />} />
                  <Route path="projects/:projectId/risks" element={<RiskRegisterPage />} />
                  {/* Task 17: Recepție + Garanție + Măsurători — F081, F082, F086, F088 */}
                  <Route path="projects/:projectId/reception" element={<ReceptionPunchListPage />} />
                  <Route path="projects/:projectId/warranties" element={<WarrantyTrackingPage />} />
                  <Route path="projects/:projectId/energy-impact" element={<EnergyImpactPage />} />
                </Route>
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
