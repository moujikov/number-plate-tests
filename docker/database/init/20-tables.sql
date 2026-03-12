CREATE TABLE "user_records" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "comment" VARCHAR(128),
    "phone" VARCHAR(16),
    "number_plate" VARCHAR(16),
    "added" TIMESTAMPTZ NOT NULL,
    "removed" TIMESTAMPTZ
);
CREATE INDEX "idx_user_records_number_plate" ON "user_records" ("number_plate");
CREATE INDEX "idx_user_records_removed" ON "user_records" ("removed");

CREATE TABLE "detections" (
    "id" UUID NOT NULL PRIMARY KEY,
    "timestamp" TIMESTAMPTZ NOT NULL,
    "number_plate" VARCHAR(16) NOT NULL,
    "region" VARCHAR(4) NOT NULL,
    "box" VARCHAR(128),
    "camera" VARCHAR(32) NOT NULL,
    "image" VARCHAR(128) NOT NULL,
    "user_id" INT REFERENCES "user_records" ("id") ON DELETE RESTRICT
);
CREATE INDEX "idx_detections_timestamp" ON "detections" ("timestamp");
CREATE INDEX "idx_detections_number_plate" ON "detections" ("number_plate");
CREATE INDEX "idx_detections_number_plate_timestamp" ON "detections" ("number_plate", "timestamp");
