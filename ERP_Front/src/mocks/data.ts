export interface OrderRow {
  id: string
  orderNo: string
  customer: string
  product: string
  quantity: number
  amount: number
  dueDate: string
  status: string
  owner: string
}

export interface ProductionRequestRow {
  id: string
  requestNo: string
  orderNo: string
  product: string
  quantity: number
  dueDate: string
  status: string
  owner: string
}

export interface InventoryRow {
  id: string
  sku: string
  name: string
  warehouse: string
  quantity: number
  unit: string
  status: string
}

export interface MovementRow {
  id: string
  movedAt: string
  sku: string
  name: string
  type: string
  quantity: number
  warehouse: string
  refNo: string
}

export interface ShipmentRow {
  id: string
  shipmentNo: string
  orderNo: string
  customer: string
  quantity: number
  status: string
  requestedAt: string
}

export interface AsRow {
  id: string
  asNo: string
  customer: string
  product: string
  symptom: string
  status: string
  assignee: string
  receivedAt: string
}

export interface UserRow {
  id: string
  name: string
  email: string
  department: string
  role: string
  status: string
}

export interface MigrationJobRow {
  id: string
  jobNo: string
  source: string
  startedBy: string
  startedAt: string
  endedAt?: string
  status: string
  successCount: number
  warningCount: number
  failCount: number
}

export const MOCK_ORDERS: OrderRow[] = [
  {
    id: '1',
    orderNo: 'SO-2026-0142',
    customer: '한빛에너지',
    product: 'MC-Pack 48V 100Ah',
    quantity: 20,
    amount: 48000000,
    dueDate: '2026-07-25',
    status: 'confirmed',
    owner: '김영업',
  },
  {
    id: '2',
    orderNo: 'SO-2026-0141',
    customer: '그린모빌리티',
    product: 'MC-Module 12S',
    quantity: 50,
    amount: 27500000,
    dueDate: '2026-07-18',
    status: 'delayed',
    owner: '이재성',
  },
  {
    id: '3',
    orderNo: 'SO-2026-0138',
    customer: '동아전력',
    product: 'MC-Pack 24V 50Ah',
    quantity: 10,
    amount: 12000000,
    dueDate: '2026-07-30',
    status: 'in_progress',
    owner: '박수주',
  },
  {
    id: '4',
    orderNo: 'SO-2026-0135',
    customer: '서울물류',
    product: 'MC-BMS V3',
    quantity: 100,
    amount: 8500000,
    dueDate: '2026-07-12',
    status: 'completed',
    owner: '김영업',
  },
  {
    id: '5',
    orderNo: 'SO-2026-0130',
    customer: '케이배터리',
    product: 'MC-Pack 48V 200Ah',
    quantity: 5,
    amount: 32500000,
    dueDate: '2026-08-05',
    status: 'draft',
    owner: '이재성',
  },
]

export const MOCK_PRODUCTION: ProductionRequestRow[] = [
  {
    id: '1',
    requestNo: 'PR-2026-0088',
    orderNo: 'SO-2026-0142',
    product: 'MC-Pack 48V 100Ah',
    quantity: 20,
    dueDate: '2026-07-22',
    status: 'in_progress',
    owner: '최생산',
  },
  {
    id: '2',
    requestNo: 'PR-2026-0087',
    orderNo: 'SO-2026-0141',
    product: 'MC-Module 12S',
    quantity: 50,
    dueDate: '2026-07-15',
    status: 'delayed',
    owner: '최생산',
  },
  {
    id: '3',
    requestNo: 'PR-2026-0085',
    orderNo: 'SO-2026-0138',
    product: 'MC-Pack 24V 50Ah',
    quantity: 10,
    dueDate: '2026-07-28',
    status: 'requested',
    owner: '정생산',
  },
]

export const MOCK_INVENTORY: InventoryRow[] = [
  {
    id: '1',
    sku: 'FG-PACK-48-100',
    name: 'MC-Pack 48V 100Ah',
    warehouse: '본사 완제품',
    quantity: 12,
    unit: 'EA',
    status: 'active',
  },
  {
    id: '2',
    sku: 'FG-MOD-12S',
    name: 'MC-Module 12S',
    warehouse: '본사 완제품',
    quantity: 3,
    unit: 'EA',
    status: 'shortage',
  },
  {
    id: '3',
    sku: 'FG-BMS-V3',
    name: 'MC-BMS V3',
    warehouse: '본사 완제품',
    quantity: 84,
    unit: 'EA',
    status: 'active',
  },
]

export const MOCK_MOVEMENTS: MovementRow[] = [
  {
    id: '1',
    movedAt: '2026-07-10T09:20:00+09:00',
    sku: 'FG-PACK-48-100',
    name: 'MC-Pack 48V 100Ah',
    type: '입고',
    quantity: 8,
    warehouse: '본사 완제품',
    refNo: 'PR-2026-0080',
  },
  {
    id: '2',
    movedAt: '2026-07-09T15:40:00+09:00',
    sku: 'FG-BMS-V3',
    name: 'MC-BMS V3',
    type: '출고',
    quantity: -20,
    warehouse: '본사 완제품',
    refNo: 'SH-2026-0044',
  },
  {
    id: '3',
    movedAt: '2026-07-08T11:05:00+09:00',
    sku: 'FG-MOD-12S',
    name: 'MC-Module 12S',
    type: '조정',
    quantity: -2,
    warehouse: '본사 완제품',
    refNo: 'ADJ-2026-0003',
  },
]

export const MOCK_SHIPMENTS: ShipmentRow[] = [
  {
    id: '1',
    shipmentNo: 'SH-2026-0051',
    orderNo: 'SO-2026-0141',
    customer: '그린모빌리티',
    quantity: 20,
    status: 'requested',
    requestedAt: '2026-07-10',
  },
  {
    id: '2',
    shipmentNo: 'SH-2026-0048',
    orderNo: 'SO-2026-0135',
    customer: '서울물류',
    quantity: 100,
    status: 'completed',
    requestedAt: '2026-07-08',
  },
  {
    id: '3',
    shipmentNo: 'SH-2026-0046',
    orderNo: 'SO-2026-0138',
    customer: '동아전력',
    quantity: 5,
    status: 'in_progress',
    requestedAt: '2026-07-09',
  },
]

export const MOCK_AS: AsRow[] = [
  {
    id: '1',
    asNo: 'AS-2026-0033',
    customer: '한빛에너지',
    product: 'MC-Pack 48V 100Ah',
    symptom: '충전 중 통신 오류',
    status: 'assigned',
    assignee: '윤AS',
    receivedAt: '2026-07-09',
  },
  {
    id: '2',
    asNo: 'AS-2026-0031',
    customer: '케이배터리',
    product: 'MC-BMS V3',
    symptom: '전압 측정 편차',
    status: 'in_progress',
    assignee: '한AS',
    receivedAt: '2026-07-07',
  },
  {
    id: '3',
    asNo: 'AS-2026-0028',
    customer: '동아전력',
    product: 'MC-Pack 24V 50Ah',
    symptom: '외함 손상',
    status: 'closed',
    assignee: '윤AS',
    receivedAt: '2026-07-01',
  },
]

export const MOCK_USERS: UserRow[] = [
  {
    id: '1',
    name: '이재성',
    email: 'jaesung@megacell.local',
    department: '기술영업팀',
    role: 'admin',
    status: 'active',
  },
  {
    id: '2',
    name: '김영업',
    email: 'sales@megacell.local',
    department: '기술영업팀',
    role: 'staff',
    status: 'active',
  },
  {
    id: '3',
    name: '최생산',
    email: 'prod@megacell.local',
    department: '생산팀',
    role: 'manager',
    status: 'active',
  },
  {
    id: '4',
    name: '박조회',
    email: 'viewer@megacell.local',
    department: '경영지원팀',
    role: 'viewer',
    status: 'inactive',
  },
]

export const MOCK_MIGRATION_JOBS: MigrationJobRow[] = [
  {
    id: '1',
    jobNo: 'MIG-2026-0012',
    source: '수주원장_2026Q2.xlsx / Sheet1',
    startedBy: '이재성',
    startedAt: '2026-07-10T10:00:00+09:00',
    endedAt: '2026-07-10T10:08:00+09:00',
    status: 'partial_success',
    successCount: 1180,
    warningCount: 12,
    failCount: 3,
  },
  {
    id: '2',
    jobNo: 'MIG-2026-0011',
    source: '재고원장_202607.xlsx / 현재고',
    startedBy: '이재성',
    startedAt: '2026-07-09T14:20:00+09:00',
    endedAt: '2026-07-09T14:25:00+09:00',
    status: 'success',
    successCount: 420,
    warningCount: 0,
    failCount: 0,
  },
  {
    id: '3',
    jobNo: 'MIG-2026-0010',
    source: 'AS이력.xlsx / 이력',
    startedBy: '관리자',
    startedAt: '2026-07-08T09:00:00+09:00',
    status: 'processing',
    successCount: 90,
    warningCount: 0,
    failCount: 0,
  },
]
