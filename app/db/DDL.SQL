CREATE TABLE
  audio_files (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    user_id UUID NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    record_time INT,
    report_id UUID,
    status VARCHAR(255) DEFAULT 'ready',
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );


create table
  stt_data (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    file_id UUID NOT NULL,
    act_id INT NOT NULL DEFAULT 1,
    talk_more_id INT NOT NULL DEFAULT 1,
    text_order INT NOT NULL,
    start_time INT NOT NULL,
    end_time INT NOT NULL,
    text VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    speaker VARCHAR(255) NOT NULL,
    text_edited VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

  create table
  report_files (
    id UUID DEFAULT gen_random_uuid() NOT NULL,
    user_id UUID NOT NULL,
    file_path VARCHAR(255) NOT NULL ,
    title VARCHAR(255) NOT NULL,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

CREATE TABLE speech_acts
(
	id SERIAL PRIMARY KEY,
	act_name VARCHAR(255) NOT NULL
);

CREATE TABLE talk_more
(
	id SERIAL PRIMARY KEY,
	talk_more VARCHAR(255) NOT NULL
);

CREATE TABLE
  plans (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    status VARCHAR(255) DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

CREATE TABLE
  user_plan (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    user_id UUID NOT NULL,
    plan_id UUID NOT NULL,
    start_at DATE NOT NULL,
    end_at DATE NOT NULL,
    status VARCHAR(255) DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

CREATE TABLE
  missions (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    plan_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    day int NOT NULL,
    status VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

CREATE TABLE
  user_missions (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    user_id UUID NOT NULL,
    mission_id UUID NOT NULL,
    status VARCHAR(255) NOT NULL DEFAULT 'ready',
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );


CREATE TABLE
  missions_message (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    mission_id UUID NOT NULL,
    message_type VARCHAR(255) NOT NULL,
    message text NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

CREATE TABLE
  user_missions_message (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    user_mission_id UUID NOT NULL,
    message_type VARCHAR(255) NOT NULL,
    message_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );

  CREATE TABLE
  user_missions_audio (
    id UUID DEFAULT gen_random_uuid () NOT NULL,
    user_id UUID NOT NULL,
    user_mission_id UUID NOT NULL,
    audio_file_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY (id)
  );