CREATE TABLE IF NOT EXISTS "users_fio" (
	"user_id" bigint NOT NULL UNIQUE,
	"name" varchar(255) NOT NULL,
	"surname" varchar(255) NOT NULL,
	"patronymic" varchar(255) NOT NULL,
	PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS "ideas" (
	"id" bigserial NOT NULL UNIQUE,
	"name" varchar(255) NOT NULL,
	"description" varchar(255) NOT NULL,
	"status" varchar(255) NOT NULL,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp,
	"creator_id" bigint NOT NULL,
	"expert_id" bigint,
	"solution" varchar(255),
	"solution_description" varchar(255),
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "users" (
	"id" bigserial NOT NULL UNIQUE,
	"login" varchar(255) NOT NULL UNIQUE,
	"hashed_password" varchar(255) NOT NULL,
	"role" varchar(255) NOT NULL,
	"status" varchar(255) NOT NULL,
	PRIMARY KEY ("id")
);

ALTER TABLE "users_fio" ADD CONSTRAINT "users_fio_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk6" FOREIGN KEY ("creator_id") REFERENCES "users"("id");

ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk7" FOREIGN KEY ("expert_id") REFERENCES "users"("id");
