export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface SalesOrder {
  id: number;
  customer_id: number;
  order_number: string;
  status: string;
  total_amount: number;
  order_date: string;
}

export interface SalesOrderItem {
  id: number;
  inventory_id: number;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface SalesOrderDetail extends SalesOrder {
  items: SalesOrderItem[];
}

export interface PurchaseOrder {
  id: number;
  vendor_id: number;
  order_number: string;
  status: string;
  total_amount: number;
  order_date: string;
}

export interface PurchaseOrderItem {
  id: number;
  inventory_id: number;
  quantity: number;
  unit_cost: number;
  line_total: number;
}

export interface PurchaseOrderDetail extends PurchaseOrder {
  items: PurchaseOrderItem[];
}

export interface InventoryItem {
  id: number;
  item_name: string;
  sku: string;
  category: string | null;
  stock_level: number;
  reorder_level: number;
  selling_price: number;
  unit: string;
  purchase_price?: number;
}

export interface Vendor {
  id: number;
  vendor_name: string;
  contact_person: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
}

export interface Customer {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
}