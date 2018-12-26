CREATE TABLE users(
id integer PRIMARY KEY,
name text,
rank text,
respect text,
points integer,
completion real
)

CREATE TABLE users_machines(
name text,
userid integer,
user integer,
root integer,
FOREIGN KEY(userid) REFERENCES users(id)
)

CREATE TABLE universities(
rank integer,
name text,
students integer,
respect integer,
country integer,
points integer,
ownership real,
challenges integer,
users integer,
systems integer,
fortresses integer,
endgames integer
)

CREATE VIEW machines_view(
name,
users,
roots)
AS SELECT
users_machines.name,
sum(user) as users,
sum(root) as roots FROM 'users_machines' join 'users'
on userid = id group BY users_machines.name ORDER BY roots"
