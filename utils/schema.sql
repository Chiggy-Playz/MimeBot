CREATE TYPE asset_type AS ENUM ('emoji', 'sticker');

CREATE TABLE IF NOT EXISTS "assets" (
    user_id BIGINT NOT NULL,
    asset_id BIGINT NOT NULL,
    asset_type asset_type NOT NULL,
    animated BOOLEAN NOT NULL,
    PRIMARY KEY (user_id, asset_id)
);