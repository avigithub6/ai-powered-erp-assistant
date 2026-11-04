export interface LoginRequest {
  tenant_code: string;
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface CurrentUser {
  id: number;
  tenant_id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}
