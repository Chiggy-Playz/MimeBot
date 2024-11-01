-- Enable Row Level Security for both tables
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assets ENABLE ROW LEVEL SECURITY;

-- Define common user check for user_assets
CREATE POLICY select_user_assets 
ON user_assets 
FOR SELECT
TO authenticated
USING ((auth.jwt() -> 'raw_user_meta_data' ->> 'provider_id')::BIGINT = user_id);

-- Allow users to delete their own assets
CREATE POLICY delete_user_assets
ON user_assets
FOR DELETE
TO authenticated
USING ((auth.jwt() -> 'raw_user_meta_data' ->> 'provider_id')::BIGINT = user_id);

-- Grant unrestricted select access to assets
CREATE POLICY select_assets
ON assets
FOR SELECT
TO authenticated
USING (true);

-- Disallow insert, update and delete on assets
CREATE POLICY insert_assets
ON assets
FOR INSERT
TO authenticated
WITH CHECK (false);

CREATE POLICY update_assets
ON assets
FOR UPDATE
TO authenticated
USING (false);

CREATE POLICY delete_assets
ON assets
FOR DELETE
TO authenticated
USING (false);

-- Disallow insert, update and delete on user_assets
CREATE POLICY insert_user_assets
ON user_assets
FOR INSERT
TO authenticated
WITH CHECK (false);

CREATE POLICY update_user_assets
ON user_assets
FOR UPDATE
TO authenticated
USING (false);

-- Disallow everything for anon role
CREATE POLICY select_assets_anon
ON assets
FOR ALL
TO anon
USING (false);