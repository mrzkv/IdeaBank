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
	"description" text NOT NULL,
	"status" varchar(255) NOT NULL,
	"start_date" timestamp NOT NULL,
	"end_date" timestamp,
	"creator_id" bigint NOT NULL,
	"expert_id" bigint,
	"solution" varchar(255),
	"solution_description" text,
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

CREATE TABLE IF NOT EXISTS "chats" (
	"id" bigserial NOT NULL UNIQUE,
	"idea_id" bigint NOT NULL UNIQUE,
	"status" varchar(10) NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "chats_messages" (
    "id" bigserial NOT NULL UNIQUE,
	"chat_id" bigint NOT NULL,
	"message" text NOT NULL,
	"author_id" bigint NOT NULL,
	PRIMARY KEY ("id")
);

CREATE TABLE IF NOT EXISTS "notifications" (
  "id" bigserial NOT NULL UNIQUE,
  "user_id" bigint NOT NULL,
  "name" varchar(50) NOT NULL,
  "date" varchar(50) NOT NULL,
  "is_read" boolean NOT NULL,
  PRIMARY KEY ("id")
);

ALTER TABLE "users_fio" ADD CONSTRAINT "users_fio_fk0" FOREIGN KEY ("user_id") REFERENCES "users"("id");
ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk6" FOREIGN KEY ("creator_id") REFERENCES "users"("id");

ALTER TABLE "ideas" ADD CONSTRAINT "ideas_fk7" FOREIGN KEY ("expert_id") REFERENCES "users"("id");

ALTER TABLE "chats" ADD CONSTRAINT "chats_fk1" FOREIGN KEY ("idea_id") REFERENCES "ideas"("id");
ALTER TABLE "chats_messages" ADD CONSTRAINT "chats_messages_fk0" FOREIGN KEY ("chat_id") REFERENCES "chats"("id");

ALTER TABLE "chats_messages" ADD CONSTRAINT "chats_messages_fk2" FOREIGN KEY ("author_id") REFERENCES "users"("id");
ALTER TABLE "notifications" ADD CONSTRAINT "notification_fk1" FOREIGN KEY ("user_id") REFERENCES "users"("id");