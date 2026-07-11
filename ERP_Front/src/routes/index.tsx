import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import { AppShell } from '@/components/layout/AppShell'
import {
  ChangePasswordPage,
  ForbiddenPage,
  HelpPage,
  LoginPage,
  NotFoundPage,
  RequireAuth,
  SignupPage,
} from '@/features/auth/AuthPages'
import { HomePage } from '@/features/home/HomePage'
import {
  OrderDetailPage,
  OrderFormPage,
  OrdersPage,
} from '@/features/sales/OrdersPages'
import {
  AsCreatePage,
  AsDetailPage,
  AsListPage,
  DocumentConvertPage,
  MigrationJobsPage,
  ProductMovementsPage,
  ProductStockPage,
  ProductionRequestDetailPage,
  ProductionRequestsPage,
  ShipmentsPage,
  UsersPage,
} from '@/features/ops/OpsPages'
import {
  AnalyticsDashboardPage,
  AsHistoryPage,
  AuditLogsPage,
  BatteryStockPage,
  BomMasterPage,
  BomRequirementsPage,
  CodesPage,
  CustomersPage,
  DemandPage,
  DocumentTemplatesPage,
  ExecutiveSummaryPage,
  InspectionPage,
  MaterialMovementsPage,
  MaterialShortagePage,
  MaterialStockPage,
  MaterialsMasterPage,
  ProductionProgressPage,
  ProductsMasterPage,
  PurchaseOrdersPage,
  PurchaseRequestsPage,
  QuotesPage,
  ShipmentRequestsPage,
  SuppliersPage,
  SystemStatusPage,
  UnshippedPage,
  WarehousesPage,
} from '@/features/placeholders/PlaceholderPages'
import { useAuth } from '@/auth/AuthContext'
import type { Permission } from '@/types'

function Permit({
  permission,
  children,
}: {
  permission?: Permission
  children: ReactNode
}) {
  const { hasPermission } = useAuth()
  if (permission && !hasPermission(permission)) {
    return <ForbiddenPage />
  }
  return children
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<HomePage />} />
        <Route path="/account/password" element={<ChangePasswordPage />} />
        <Route path="/help" element={<HelpPage />} />

        {/* 영업 */}
        <Route
          path="/sales/quotes"
          element={
            <Permit permission="sales.view">
              <QuotesPage />
            </Permit>
          }
        />
        <Route
          path="/sales/orders"
          element={
            <Permit permission="sales.view">
              <OrdersPage />
            </Permit>
          }
        />
        <Route
          path="/sales/orders/new"
          element={
            <Permit permission="sales.edit">
              <OrderFormPage />
            </Permit>
          }
        />
        <Route
          path="/sales/orders/:id"
          element={
            <Permit permission="sales.view">
              <OrderDetailPage />
            </Permit>
          }
        />
        <Route
          path="/sales/orders/:id/edit"
          element={
            <Permit permission="sales.edit">
              <OrderFormPage />
            </Permit>
          }
        />
        <Route
          path="/sales/unshipped"
          element={
            <Permit permission="sales.view">
              <UnshippedPage />
            </Permit>
          }
        />
        <Route
          path="/sales/shipment-requests"
          element={
            <Permit permission="sales.view">
              <ShipmentRequestsPage />
            </Permit>
          }
        />
        <Route
          path="/sales/customers"
          element={
            <Permit permission="sales.view">
              <CustomersPage />
            </Permit>
          }
        />
        <Route
          path="/sales/document-convert"
          element={
            <Permit permission="document.generate">
              <DocumentConvertPage />
            </Permit>
          }
        />

        {/* 생산 */}
        <Route
          path="/production/requests"
          element={
            <Permit permission="production.view">
              <ProductionRequestsPage />
            </Permit>
          }
        />
        <Route
          path="/production/requests/:id"
          element={
            <Permit permission="production.view">
              <ProductionRequestDetailPage />
            </Permit>
          }
        />
        <Route
          path="/production/progress"
          element={
            <Permit permission="production.view">
              <ProductionProgressPage />
            </Permit>
          }
        />
        <Route
          path="/production/bom-requirements"
          element={
            <Permit permission="production.view">
              <BomRequirementsPage />
            </Permit>
          }
        />
        <Route
          path="/production/shortages"
          element={
            <Permit permission="production.view">
              <MaterialShortagePage />
            </Permit>
          }
        />
        <Route
          path="/production/inspection"
          element={
            <Permit permission="production.view">
              <InspectionPage />
            </Permit>
          }
        />

        {/* 구매·자재 */}
        <Route
          path="/purchasing/requests"
          element={
            <Permit permission="purchasing.view">
              <PurchaseRequestsPage />
            </Permit>
          }
        />
        <Route
          path="/purchasing/orders"
          element={
            <Permit permission="purchasing.view">
              <PurchaseOrdersPage />
            </Permit>
          }
        />
        <Route
          path="/purchasing/material-stock"
          element={
            <Permit permission="purchasing.view">
              <MaterialStockPage />
            </Permit>
          }
        />
        <Route
          path="/purchasing/material-movements"
          element={
            <Permit permission="purchasing.view">
              <MaterialMovementsPage />
            </Permit>
          }
        />
        <Route
          path="/purchasing/suppliers"
          element={
            <Permit permission="purchasing.view">
              <SuppliersPage />
            </Permit>
          }
        />

        {/* 재고·출고 */}
        <Route
          path="/inventory/product-stock"
          element={
            <Permit permission="inventory.view">
              <ProductStockPage />
            </Permit>
          }
        />
        <Route
          path="/inventory/product-movements"
          element={
            <Permit permission="inventory.view">
              <ProductMovementsPage />
            </Permit>
          }
        />
        <Route
          path="/inventory/battery"
          element={
            <Permit permission="inventory.view">
              <BatteryStockPage />
            </Permit>
          }
        />
        <Route
          path="/inventory/shipments"
          element={
            <Permit permission="inventory.view">
              <ShipmentsPage />
            </Permit>
          }
        />

        {/* AS */}
        <Route
          path="/as"
          element={
            <Permit permission="as.view">
              <AsListPage />
            </Permit>
          }
        />
        <Route
          path="/as/new"
          element={
            <Permit permission="as.edit">
              <AsCreatePage />
            </Permit>
          }
        />
        <Route
          path="/as/history"
          element={
            <Permit permission="as.view">
              <AsHistoryPage />
            </Permit>
          }
        />
        <Route
          path="/as/:id"
          element={
            <Permit permission="as.view">
              <AsDetailPage />
            </Permit>
          }
        />

        {/* 기준정보 */}
        <Route
          path="/master/products"
          element={
            <Permit permission="master.view">
              <ProductsMasterPage />
            </Permit>
          }
        />
        <Route
          path="/master/materials"
          element={
            <Permit permission="master.view">
              <MaterialsMasterPage />
            </Permit>
          }
        />
        <Route
          path="/master/bom"
          element={
            <Permit permission="master.view">
              <BomMasterPage />
            </Permit>
          }
        />
        <Route
          path="/master/warehouses"
          element={
            <Permit permission="master.view">
              <WarehousesPage />
            </Permit>
          }
        />
        <Route
          path="/master/codes"
          element={
            <Permit permission="master.view">
              <CodesPage />
            </Permit>
          }
        />

        {/* 분석 */}
        <Route
          path="/analytics/dashboard"
          element={
            <Permit permission="analytics.view">
              <AnalyticsDashboardPage />
            </Permit>
          }
        />
        <Route
          path="/analytics/executive"
          element={
            <Permit permission="analytics.view">
              <ExecutiveSummaryPage />
            </Permit>
          }
        />
        <Route
          path="/analytics/demand"
          element={
            <Permit permission="analytics.view">
              <DemandPage />
            </Permit>
          }
        />

        {/* 관리 */}
        <Route
          path="/admin/users"
          element={
            <Permit permission="admin.manage">
              <UsersPage />
            </Permit>
          }
        />
        <Route
          path="/admin/migration"
          element={
            <Permit permission="admin.view">
              <MigrationJobsPage />
            </Permit>
          }
        />
        <Route
          path="/admin/audit-logs"
          element={
            <Permit permission="admin.view">
              <AuditLogsPage />
            </Permit>
          }
        />
        <Route
          path="/admin/templates"
          element={
            <Permit permission="admin.view">
              <DocumentTemplatesPage />
            </Permit>
          }
        />
        <Route
          path="/admin/system"
          element={
            <Permit permission="admin.view">
              <SystemStatusPage />
            </Permit>
          }
        />

        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
