ALTER POLICY select_user_assets 
ON user_assets
TO authenticated
USING ((auth.jwt() -> 'user_metadata' ->> 'provider_id')::BIGINT = user_id);


ALTER POLICY delete_user_assets
ON user_assets
TO authenticated
USING ((auth.jwt() -> 'user_metadata' ->> 'provider_id')::BIGINT = user_id);
