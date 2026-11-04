
package com.shivit.erp.config;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
public class InternalAuthFilter extends OncePerRequestFilter {

    private static final String TOKEN_HEADER =
            "X-Internal-Service-Token";

    private final String expectedToken;

    public InternalAuthFilter(
            @Value("${app.internal.token}") String expectedToken
    ) {
        if (expectedToken == null || expectedToken.isBlank()) {
            throw new IllegalStateException(
                    "Internal service token is not configured"
            );
        }

        this.expectedToken = expectedToken;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !request.getRequestURI().startsWith("/internal/");
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String suppliedToken = request.getHeader(TOKEN_HEADER);

        boolean validToken = suppliedToken != null
                && MessageDigest.isEqual(
                        expectedToken.getBytes(StandardCharsets.UTF_8),
                        suppliedToken.getBytes(StandardCharsets.UTF_8)
                );

        if (!validToken) {
            response.sendError(
                    HttpServletResponse.SC_UNAUTHORIZED,
                    "Invalid internal service credentials"
            );
            return;
        }

        filterChain.doFilter(request, response);
    }
}
