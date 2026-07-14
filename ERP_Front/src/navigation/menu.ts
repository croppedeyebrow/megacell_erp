import type { Permission } from '@/types'
import {
  Home,
  Users,
  ShoppingCart,
  Factory,
  Package,
  Warehouse,
  Wrench,
  BookOpen,
  BarChart3,
  Settings,
  type LucideIcon,
} from 'lucide-react'

export interface NavChild {
  id: string
  label: string
  path: string
  permission?: Permission
}

export interface NavItem {
  id: string
  label: string
  path?: string
  icon: LucideIcon
  permission?: Permission
  children?: NavChild[]
}

export const NAV_ITEMS: NavItem[] = [
  {
    id: 'home',
    label: '홈',
    path: '/',
    icon: Home,
    permission: 'home.view',
  },
  {
    id: 'org',
    label: '조직도',
    path: '/org',
    icon: Users,
    permission: 'home.view',
  },
  {
    id: 'sales',
    label: '영업',
    icon: ShoppingCart,
    permission: 'sales.view',
    children: [
      { id: 'quotes', label: '견적', path: '/sales/quotes' },
      { id: 'orders', label: '수주', path: '/sales/orders' },
      { id: 'unshipped', label: '미출고', path: '/sales/unshipped' },
      { id: 'shipment-requests', label: '출고 요청', path: '/sales/shipment-requests' },
      { id: 'customers', label: '고객/거래처', path: '/sales/customers' },
      {
        id: 'document-convert',
        label: '문서 변환',
        path: '/sales/document-convert',
        permission: 'document.generate',
      },
    ],
  },
  {
    id: 'production',
    label: '생산',
    icon: Factory,
    permission: 'production.view',
    children: [
      { id: 'prod-requests', label: '생산 요청', path: '/production/requests' },
      { id: 'prod-progress', label: '생산 계획/진행', path: '/production/progress' },
      { id: 'bom-req', label: 'BOM 소요량', path: '/production/bom-requirements' },
      { id: 'shortage', label: '부족 자재', path: '/production/shortages' },
      { id: 'inspection', label: '검수/출고 준비', path: '/production/inspection' },
    ],
  },
  {
    id: 'purchasing',
    label: '구매·자재',
    icon: Package,
    permission: 'purchasing.view',
    children: [
      { id: 'purchase-requests', label: '구매 요청', path: '/purchasing/requests' },
      { id: 'purchase-orders', label: '발주', path: '/purchasing/orders' },
      { id: 'material-stock', label: '자재 현재고', path: '/purchasing/material-stock' },
      { id: 'material-movements', label: '자재 입출고', path: '/purchasing/material-movements' },
      { id: 'suppliers', label: '공급업체', path: '/purchasing/suppliers' },
    ],
  },
  {
    id: 'inventory',
    label: '재고·출고',
    icon: Warehouse,
    permission: 'inventory.view',
    children: [
      { id: 'product-stock', label: '제품 현재고', path: '/inventory/product-stock' },
      { id: 'product-movements', label: '제품 입출고', path: '/inventory/product-movements' },
      { id: 'battery', label: '배터리 재고/이력', path: '/inventory/battery' },
      { id: 'shipments', label: '출고 관리', path: '/inventory/shipments' },
    ],
  },
  {
    id: 'as',
    label: 'AS',
    icon: Wrench,
    permission: 'as.view',
    children: [
      { id: 'as-list', label: 'AS 처리', path: '/as' },
      { id: 'as-create', label: 'AS 접수', path: '/as/new' },
      { id: 'as-history', label: '고객·제품별 이력', path: '/as/history' },
    ],
  },
  {
    id: 'master',
    label: '기준정보',
    icon: BookOpen,
    permission: 'master.view',
    children: [
      { id: 'products', label: '제품', path: '/master/products' },
      { id: 'materials', label: '자재', path: '/master/materials' },
      { id: 'bom', label: 'BOM/리비전', path: '/master/bom' },
      { id: 'warehouses', label: '창고', path: '/master/warehouses' },
      { id: 'codes', label: '코드 관리', path: '/master/codes' },
    ],
  },
  {
    id: 'analytics',
    label: '분석',
    icon: BarChart3,
    permission: 'analytics.view',
    children: [
      { id: 'dashboard', label: '업무 대시보드', path: '/analytics/dashboard' },
      { id: 'executive', label: '경영 요약', path: '/analytics/executive' },
      { id: 'demand', label: '수요·적정재고', path: '/analytics/demand' },
    ],
  },
  {
    id: 'admin',
    label: '관리',
    icon: Settings,
    permission: 'admin.view',
    children: [
      { id: 'users', label: '사용자/권한', path: '/admin/users', permission: 'admin.manage' },
      { id: 'migration', label: 'Excel 이관·동기화', path: '/admin/migration' },
      { id: 'audit', label: '감사 로그', path: '/admin/audit-logs' },
      { id: 'templates', label: '문서 템플릿', path: '/admin/templates' },
      { id: 'system', label: '시스템 상태', path: '/admin/system' },
    ],
  },
]
