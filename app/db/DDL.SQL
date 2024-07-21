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