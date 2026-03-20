-- =============================================================================
-- Sinistrinha — Row Level Security (RLS) Policies
-- =============================================================================
-- Execute this SQL in your Supabase Dashboard → SQL Editor, or via supabase CLI.
-- It enables RLS on all core tables and creates policies that restrict data
-- access so each authenticated user can only see/modify their own records.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. users_userprofile
-- ---------------------------------------------------------------------------
ALTER TABLE users_userprofile ENABLE ROW LEVEL SECURITY;

-- Users can read only their own profile
CREATE POLICY "users_select_own_profile"
    ON users_userprofile
    FOR SELECT
    USING (user_id = auth.uid()::int);

-- Users can update only their own profile
CREATE POLICY "users_update_own_profile"
    ON users_userprofile
    FOR UPDATE
    USING (user_id = auth.uid()::int)
    WITH CHECK (user_id = auth.uid()::int);

-- Service role can do everything (for backend operations)
CREATE POLICY "service_role_full_access_profiles"
    ON users_userprofile
    FOR ALL
    USING (auth.role() = 'service_role');

-- ---------------------------------------------------------------------------
-- 2. game_spinhistory
-- ---------------------------------------------------------------------------
ALTER TABLE game_spinhistory ENABLE ROW LEVEL SECURITY;

-- Users can read only their own spin history
CREATE POLICY "users_select_own_spins"
    ON game_spinhistory
    FOR SELECT
    USING (user_id IN (
        SELECT id FROM users_userprofile WHERE user_id = auth.uid()::int
    ));

-- Only service role can insert spins (backend does this)
CREATE POLICY "service_role_insert_spins"
    ON game_spinhistory
    FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- Service role full access
CREATE POLICY "service_role_full_access_spins"
    ON game_spinhistory
    FOR ALL
    USING (auth.role() = 'service_role');

-- ---------------------------------------------------------------------------
-- 3. game_levelconfig (read-only for all authenticated users)
-- ---------------------------------------------------------------------------
ALTER TABLE game_levelconfig ENABLE ROW LEVEL SECURITY;

-- Any authenticated user can read level configs
CREATE POLICY "authenticated_read_level_config"
    ON game_levelconfig
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Only service role can modify level configs
CREATE POLICY "service_role_full_access_levels"
    ON game_levelconfig
    FOR ALL
    USING (auth.role() = 'service_role');

-- ---------------------------------------------------------------------------
-- 4. game_jackpotpool (read-only for all authenticated users)
-- ---------------------------------------------------------------------------
ALTER TABLE game_jackpotpool ENABLE ROW LEVEL SECURITY;

-- Any authenticated user can read the jackpot pool
CREATE POLICY "authenticated_read_jackpot"
    ON game_jackpotpool
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Only service role can modify jackpot pool
CREATE POLICY "service_role_full_access_jackpot"
    ON game_jackpotpool
    FOR ALL
    USING (auth.role() = 'service_role');

-- ---------------------------------------------------------------------------
-- 5. payments_transaction
-- ---------------------------------------------------------------------------
ALTER TABLE payments_transaction ENABLE ROW LEVEL SECURITY;

-- Users can read only their own transactions
CREATE POLICY "users_select_own_transactions"
    ON payments_transaction
    FOR SELECT
    USING (user_id IN (
        SELECT id FROM users_userprofile WHERE user_id = auth.uid()::int
    ));

-- Only service role can insert/update transactions
CREATE POLICY "service_role_full_access_transactions"
    ON payments_transaction
    FOR ALL
    USING (auth.role() = 'service_role');
