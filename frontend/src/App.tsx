import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { App as AntApp } from "antd";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { I18nProvider } from "./i18n";
import ThemeProvider from "./components/ThemeProvider";
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
import ContractsListPage from "./modules/pipeline/pages/ContractsListPage";
import ContractDetailPage from "./modules/pipeline/pages/ContractDetailPage";
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
import ProjectReportPage from "./modules/pm/pages/ProjectReportPage";
import CompletedProjectsArchivePage from "./modules/pm/pages/CompletedProjectsArchivePage";
import EnergyPortfolioPage from "./modules/pm/pages/EnergyPortfolioPage";
import ProjectsListPage from "./modules/pm/pages/ProjectsListPage";
import ImportEnginePage from "./modules/pm/pages/ImportEnginePage";
import RMProjectPage from "./modules/pm/pages/RMProjectPage";
import ResourceDashboardPage from "./modules/rm/pages/ResourceDashboardPage";
import EmployeesPage from "./modules/rm/pages/EmployeesPage";
import EquipmentPage from "./modules/rm/pages/EquipmentPage";
import MaterialsStockPage from "./modules/rm/pages/MaterialsStockPage";
import CompanyCapacityPage from "./modules/rm/pages/CompanyCapacityPage";
import FinancialPlanningPage from "./modules/rm/pages/FinancialPlanningPage";
import ModuleGridPage from "./pages/ModuleGridPage";
import DashboardHomePage from "./pages/DashboardHomePage";
import TenantSetupWizard from "./modules/system/pages/TenantSetupWizard";
import PipelineConfiguratorPage from "./modules/system/pages/PipelineConfiguratorPage";
import RMConfiguratorPage from "./modules/system/pages/RMConfiguratorPage";
import ExecutiveDashboardPage from "./modules/bi/pages/ExecutiveDashboardPage";
import KPIDashboardPage from "./modules/bi/pages/KPIDashboardPage";
import KPIBuilderPage from "./modules/bi/pages/KPIBuilderPage";
import ReportsBuilderPage from "./modules/bi/pages/ReportsBuilderPage";
import AIAssistantPage from "./modules/bi/pages/AIAssistantPage";
import MLForecastPage from "./modules/bi/pages/MLForecastPage";
import BrandingSettingsPage from "./modules/system/pages/BrandingSettingsPage";
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
      <I18nProvider>
        <ThemeProvider>
          <AntApp>
            <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              {/* F160: Tenant Setup Wizard — SaaS onboarding (P3) */}
              <Route
                path="/setup"
                element={
                  <RequireAuth>
                    <TenantSetupWizard />
                  </RequireAuth>
                }
              />
              <Route
                path="/"
                element={
                  <RequireAuth>
                    <AppLayout />
                  </RequireAuth>
                }
              >
                {/* E-001: Dashboard Principal — Home */}
                <Route index element={<DashboardHomePage />} />
                {/* F157: Module Grid Navigation */}
                <Route path="modules" element={<ModuleGridPage />} />

                {/* CRM Routes */}
                <Route path="crm">
                  <Route index element={<Navigate to="contacts" replace />} />
                  <Route path="dashboard" element={<DashboardPage />} />
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
                  {/* Contracts (E-007, E-008) — F031, F035, F063 */}
                  <Route path="contracts" element={<ContractsListPage />} />
                  <Route path="contracts/:id" element={<ContractDetailPage />} />
                </Route>

                {/* PM Routes — E-016 Gantt, E-018 Timesheet, E-019 Consum, F075, F077 */}
                <Route path="pm">
                  <Route index element={<ProjectsListPage />} />
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
                  {/* Task 28: Import Engine (E-037, F123) + RM Project (E-014.7, F083) */}
                  <Route path="projects/:projectId/import" element={<ImportEnginePage />} />
                  <Route path="projects/:projectId/resources" element={<RMProjectPage />} />
                  {/* Task 18: Rapoarte PM + Arhivă — F090, F091, F095, F142, F161 */}
                  <Route path="projects/:projectId/report" element={<ProjectReportPage />} />
                  <Route path="archive" element={<CompletedProjectsArchivePage />} />
                  <Route path="energy-portfolio" element={<EnergyPortfolioPage />} />
                </Route>
                {/* RM Routes — E-032, E-033, E-034, E-035 */}
                <Route path="rm">
                  <Route index element={<ResourceDashboardPage />} />
                  <Route path="dashboard" element={<ResourceDashboardPage />} />
                  <Route path="employees" element={<EmployeesPage />} />
                  <Route path="equipment" element={<EquipmentPage />} />
                  <Route path="materials" element={<MaterialsStockPage />} />
                  {/* E-036: Company Capacity Dashboard — F121, F122 */}
                  <Route path="capacity" element={<CompanyCapacityPage />} />
                  {/* E-040: Financial Planning — F115, F116 */}
                  <Route path="financial" element={<FinancialPlanningPage />} />
                </Route>
                {/* BI Routes — Task 31: F133, F148, F152, E-041/F142 */}
                <Route path="bi">
                  <Route index element={<Navigate to="executive" replace />} />
                  <Route path="executive" element={<ExecutiveDashboardPage />} />
                  <Route path="kpi-dashboard" element={<KPIDashboardPage />} />
                  <Route path="kpi-builder" element={<KPIBuilderPage />} />
                  <Route path="reports" element={<ReportsBuilderPage />} />
                  {/* Task 33: F132 AI Assistant + F135 ML Forecast */}
                  <Route path="assistant" element={<AIAssistantPage />} />
                  <Route path="forecast" element={<MLForecastPage />} />
                </Route>
                <Route path="settings" element={<PlaceholderPage title="Setări" />} />
                {/* Task 32: F137 Branding + F138 Multi-limbă */}
                <Route path="settings/branding" element={<BrandingSettingsPage />} />
                {/* Task 30: Configuratoare avansate — F061, F131 */}
                <Route path="settings/pipeline" element={<PipelineConfiguratorPage />} />
                <Route path="settings/rm" element={<RMConfiguratorPage />} />
              </Route>
            </Routes>
            </BrowserRouter>
          </AntApp>
        </ThemeProvider>
      </I18nProvider>
    </QueryClientProvider>
  );
}

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div style={{ padding: 48, textAlign: "center" }}>
      <h2 style={{ color: "#F1F5F9" }}>{title}</h2>
      <p style={{ color: "#64748B" }}>Modul in curs de implementare.</p>
    </div>
  );
}

export default App;
