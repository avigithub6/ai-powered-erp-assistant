
package com.shivit.erp.controller;

import com.shivit.erp.config.TenantContext;
import com.shivit.erp.service.SalesOrderService;
import com.shivit.erp.service.SalesOrderService.SalesOrderPage;

import jakarta.servlet.http.HttpServletRequest;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/internal/erp/sales")
public class InternalSalesController {

    private final SalesOrderService salesOrderService;

    public InternalSalesController(
            SalesOrderService salesOrderService
    ) {
        this.salesOrderService = salesOrderService;
    }

    @GetMapping("/orders")
    public SalesOrderPage getSalesOrders(
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "0") int offset,
            HttpServletRequest request
    ) {
        if (limit < 1 || limit > 100 || offset < 0) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Invalid pagination parameters"
            );
        }

        int tenantId = TenantContext.requireTenantId(request);

        return salesOrderService.getSalesOrders(
                tenantId,
                limit,
                offset
        );
    }
}
