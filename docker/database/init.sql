CREATE USER processor WITH PASSWORD '__POSTGRES_PROCESSOR_PASSWORD__';
GRANT USAGE, CREATE ON SCHEMA public TO processor;
GRANT ALL PRIVILEGES ON DATABASE number_plates TO processor;

CREATE USER skud WITH PASSWORD '__POSTGRES_SKUD_PASSWORD__';
GRANT USAGE, CREATE ON SCHEMA public TO skud;
GRANT ALL PRIVILEGES ON DATABASE number_plates TO skud;

CREATE USER frontend WITH PASSWORD '__POSTGRES_FRONTEND_PASSWORD__';
GRANT USAGE, CREATE ON SCHEMA public TO frontend;
GRANT ALL PRIVILEGES ON DATABASE number_plates TO frontend;



 CREATE TABLE "detections" (
	    "id" UUID NOT NULL PRIMARY KEY,
	    "timestamp" TIMESTAMPTZ NOT NULL,
	    "number_plate" VARCHAR(16) NOT NULL,
	    "region" VARCHAR(4) NOT NULL,
	    "box" VARCHAR(128),
	    "camera" VARCHAR(32) NOT NULL,
	    "image" VARCHAR(128) NOT NULL
	);
	CREATE INDEX "idx_detections_timestamp" ON "detections" ("timestamp");
	CREATE INDEX "idx_detections_number_plate" ON "detections" ("number_plate");
	CREATE INDEX "idx_detections_number_plate_timestamp" ON "detections" ("number_plate", "timestamp");
