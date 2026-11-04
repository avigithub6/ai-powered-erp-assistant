
package com.shivit.erp.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class SalesOrderService {

    private final JdbcTemplate jdbcTemplate;

    public SalesOrderService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public SalesOrderPage getSalesOrders(
            int tenantId,
            int limit,
            int offset
    ) {
        String sql = """
                SELECT
                    id,
                    order_number,
                    status,
                    total_amount,
                    order_date
                FROM sales_orders
                WHERE tenant_id = ?
                ORDER BY order_date DESC, id DESC
                LIMIT ? OFFSET ?
                """;

        List<SalesOrder> orders = jdbcTemplate.query(
                sql,
                (rs, rowNum) -> new SalesOrder(
                        rs.getInt("id"),
                        rs.getString("order_number"),
                        rs.getString("status"),
                        rs.getBigDecimal("total_amount"),
                        rs.getTimestamp("order_date").toLocalDateTime()
                ),
                tenantId,
                limit,
                offset
        );

        String countSql = """
                SELECT COUNT(*)
                FROM sales_orders
                WHERE tenant_id = ?
                """;

        Long total = jdbcTemplate.queryForObject(
                countSql,
                Long.class,
                tenantId
        );

        return new SalesOrderPage(
                orders,
                total == null ? 0 : total,
                limit,
                offset
        );
    }

    public record SalesOrder(
            int id,
            String order_number,
            String status,
            BigDecimal total_amount,
            LocalDateTime order_date
    ) {
    }

    public record SalesOrderPage(
            List<SalesOrder> items,
            long total,
            int limit,
            int offset
    ) {
    }
}
