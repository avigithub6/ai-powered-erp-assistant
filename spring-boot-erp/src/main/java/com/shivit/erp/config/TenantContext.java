
package com.shivit.erp.config;

import jakarta.servlet.http.HttpServletRequest;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

public final class TenantContext {

    private static final String TENANT_HEADER = "X-Tenant-Id";

    private TenantContext() {
    }

    public static int requireTenantId(HttpServletRequest request) {

        String tenantValue = request.getHeader(TENANT_HEADER);

        if (tenantValue == null || tenantValue.isBlank()) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Tenant identifier is required"
            );
        }

        try {
            int tenantId = Integer.parseInt(tenantValue);

            if (tenantId <= 0) {
                throw new NumberFormatException();
            }

            return tenantId;

        } catch (NumberFormatException exception) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Invalid tenant identifier"
            );
        }
    }
}
