export interface DashboardSummary {
  total_sales: number | null;
  total_purchase_value: number | null;
  sales_order_count: number;
  inventory_item_count: number;
  low_stock_count: number;
}

export interface SalesTrend {
  month: string;
  total_sales: number;
}

export interface TopProduct {
  inventory_id: number;
  item_name: string;
  sku: string;
  total_quantity_sold: number;
}

export interface TopVendor {
  vendor_id: number;
  vendor_name: string;
  total_purchase_value: number;
}

export interface DashboardInventoryItem {
  id: number;
  item_name: string;
  sku: string;
  stock_level: number;
  reorder_level: number;
  unit: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardData {
  summary: DashboardSummary;
  salesTrend: SalesTrend[];
  topProducts: TopProduct[];
  topVendors: TopVendor[];
  inventory: PaginatedResponse<DashboardInventoryItem>;
  lowStock: PaginatedResponse<DashboardInventoryItem>;
}
