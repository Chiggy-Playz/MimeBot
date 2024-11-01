-- Create an enum type for the asset types
CREATE TYPE asset_type AS ENUM ('emoji', 'sticker', 'attachment');

CREATE TABLE assets (
  id bigint NOT NULL PRIMARY KEY,
  name text NOT NULL,
  animated boolean NOT NULL,
  type asset_type NOT NULL
);

COMMENT ON COLUMN assets.id IS 'Either sticker id, emoji id or attachment id';

CREATE TABLE user_assets (
  user_id bigint NOT NULL,
  asset_id bigint NOT NULL,
  PRIMARY KEY (user_id, asset_id),
  FOREIGN KEY (asset_id) REFERENCES assets (id)
);
