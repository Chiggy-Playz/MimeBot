--create types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'asset_type') THEN
        CREATE TYPE asset_type AS ENUM ('emoji', 'sticker');
    END IF;
    --more types here...
END$$;

CREATE TABLE IF NOT EXISTS "assets" (
    id BIGINT NOT NULL,
    type asset_type NOT NULL,
    animated BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "unassigned_assets" (
    user_id BIGINT NOT NULL,
    asset_id BIGINT,
    PRIMARY KEY (user_id, asset_id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE TABLE IF NOT EXISTS "packs" (
    user_id BIGINT NOT NULL,
    pack_id SERIAL NOT NULL,
    name TEXT NOT NULL,
    identifier TEXT NOT NULL,
    PRIMARY KEY (pack_id),
    UNIQUE (user_id, identifier)
);

CREATE TABLE IF NOT EXISTS "pack_contents" (
    pack_id BIGINT NOT NULL,
    asset_id BIGINT NOT NULL,
    PRIMARY KEY (pack_id, asset_id),
    FOREIGN KEY (pack_id) REFERENCES packs(pack_id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
)