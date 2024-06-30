-- CREATE TABLE users
-- (
--     id varchar(255) NOT NULL,
--     user_name varchar(255) NOT NULL,
--     role_id int,
--     plan_id int,
--     created_at timestamp NOT NULL DEFAULT current_timestamp,
--     PRIMARY KEY (id)
-- );

create table
  audio_files (
    id uuid default gen_random_uuid () not null,
    user_id varchar(255) not null,
    file_path varchar(255) not null,
    record_time int,
    report_id varchar(255),
    created_at timestamp not null default current_timestamp,
    primary key (id)
  );


create table
  stt_data (
    id uuid DEFAULT gen_random_uuid() not null,
    file_id varchar(255) not null,
    act_id int not null default 1,
    text_order int not null,
    start_time int not null,
    end_time int not null,
    text varchar(255) not null,
    confidence float not null,
    speaker varchar(255) not null,
    text_edited varchar(255),
    created_at timestamp not null default current_timestamp,
    primary key (id)
  );

  create table
  report_files (
    id UUID DEFAULT gen_random_uuid() not null,
    user_id varchar(255) not null,
    file_path varchar(255) not null ,
    title varchar(255) not null,
    created_at timestamp not null default current_timestamp,
    primary key (id)
  );

-- CREATE TABLE roles
-- (
--     id int NOT NULL,
--     role_name varchar(255) NOT NULL,
--     created_at timestamp NOT NULL DEFAULT current_timestamp,
--     PRIMARY KEY (id)
-- );

-- CREATE TABLE plans
-- (
--     id int NOT NULL,
--     plan_name varchar(255) NOT NULL,
--     created_at timestamp NOT NULL DEFAULT current_timestamp,
--     PRIMARY KEY (id)
-- );

-- CREATE TABLE image_file
-- (
--     id varchar(255) NOT NULL,
--     user_id varchar(255) NOT NULL,
--     start_date timestamp NOT NULL,
--     end_date timestamp NOT null,
--     image_path varchar(255) NOT NULL,
--     PRIMARY KEY (id)
-- );

CREATE TABLE speech_acts
(
	id SERIAL PRIMARY key,
	act_name varchar(255) not null
);