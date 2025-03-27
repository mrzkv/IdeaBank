CREATE TABLE IF NOT EXISTS "users_fio" (
	"user_id" bigint NOT NULL UNIQUE,
	"name" varchar(255) NOT NULL,
	"surname" varchar(255) NOT NULL,
	"patronymic" varchar(255) NOT NULL,
	PRIMARY KEY ("user_id")
);

CREATE TABLE IF NOT EXISTS "ideas" (
	"id" serial NOT NULL UNIQUE,
	"name" varchar(255) NOT NULL,
	"description" varchar(255) NOT NULL,
	"status" varchar(255) NOT NULL,
	"start_date" timestamp with time zone NOT NULL,
	"end_date" timestamp with time zone NOT NULL,
	"creator_id" bigint NOT NULL,
	"expert_id" bigint NOT NULL,
	"solution" varchar(255) NOT NULL,
	"solution_description" varchar(255) NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "users" (
	"id" serial NOT NULL UNIQUE,
	"login" varchar(255) NOT NULL UNIQUE,
	"hashed_password" varchar(255) NOT NULL,
	"role" varchar(255) NOT NULL,
	"status" varchar(255) NOT NULL,
	PRIMARY KEY ("id")
);

ALTER TABLE "users_fio" ADD CONSTRAINT "users_fio_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk6" FOREIGN KEY ("creator_id") REFERENCES "users"("id");

ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk7" FOREIGN KEY ("expert_id") REFERENCES "users"("id");
