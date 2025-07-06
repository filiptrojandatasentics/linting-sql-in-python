create table if not exists {{ table_name }} (
    user_id serial primary key
    , username varchar({{ username_length }}) not null
    , email varchar(255) unique not null
    , status varchar(20) default 'active'
    , created_at timestamp default CURRENT_TIMESTAMP
);
