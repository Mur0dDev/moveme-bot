from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

<<<<<<< HEAD
=======

>>>>>>> master
class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
<<<<<<< HEAD
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )
=======
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                host=config.DB_HOST,
                database=config.DB_NAME
            )
            print("Database pool created successfully.")
        except Exception as e:
            print(f"Failed to create database pool: {e}")
            raise
>>>>>>> master

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
<<<<<<< HEAD
                      execute: bool = False
                      ):
=======
                      execute: bool = False):
>>>>>>> master
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

<<<<<<< HEAD
    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE 
=======
    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)])
        return sql, tuple(parameters.values())

    # Create tables
    async def create_table_user_credentials(self):
        sql = """
        CREATE TABLE IF NOT EXISTS user_credentials (
            telegram_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            dob DATE NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            role VARCHAR(50) NOT NULL
>>>>>>> master
        );
        """
        await self.execute(sql, execute=True)

<<<<<<< HEAD
    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
=======
    async def create_table_group_credentials(self):
        sql = """
        CREATE TABLE IF NOT EXISTS group_credentials (
            group_id BIGINT PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            group_name VARCHAR(255) NOT NULL,
            group_type VARCHAR(50) NOT NULL,
            truck_number VARCHAR(20) NOT NULL,
            driver_name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_gross_sheet(self):
        sql = """
        CREATE TABLE IF NOT EXISTS gross_sheet (
            load_number VARCHAR(50) PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            dispatcher_name VARCHAR(255) NOT NULL,
            driver_name VARCHAR(255) NOT NULL,
            truck_number VARCHAR(20) NOT NULL,
            broker_name VARCHAR(255) NOT NULL,
            team_or_solo VARCHAR(50) NOT NULL,
            pickup_location TEXT NOT NULL,
            pickup_datetime TIMESTAMP NOT NULL,
            delivery_location TEXT NOT NULL,
            delivery_datetime TEXT NOT NULL,
            deadhead_miles INTEGER NOT NULL,
            loaded_miles INTEGER NOT NULL,
            load_rate FLOAT NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_allowed_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS allowed_users (
            telegram_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            date_added DATE NOT NULL,
            status VARCHAR(20) NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_pwd_credentials(self):
        sql = """
        CREATE TABLE IF NOT EXISTS pwd_credentials (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            account_type VARCHAR(255) NOT NULL,
            email_username VARCHAR(255) NOT NULL,
            password TEXT NOT NULL,
            key TEXT,
            notes TEXT,
            updated_date DATE NOT NULL,
            access_restriction VARCHAR(50) NOT NULL,
            url TEXT
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_access_logs(self):
        sql = """
        CREATE TABLE IF NOT EXISTS access_logs (
            id SERIAL PRIMARY KEY,
            date_time TIMESTAMP NOT NULL,
            user_telegram_id BIGINT NOT NULL REFERENCES allowed_users (telegram_id),
            user_full_name VARCHAR(255) NOT NULL,
            accessed_account_type VARCHAR(255) NOT NULL,
            result VARCHAR(50) NOT NULL,
            remarks TEXT
        );
        """
        await self.execute(sql, execute=True)

    # Add data methods for each table (example for one table, you can expand for others)
    async def add_user_credential(self, telegram_id, full_name, dob, phone_number, role):
        sql = """
        INSERT INTO user_credentials (telegram_id, full_name, dob, phone_number, role)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *;
        """
        return await self.execute(sql, telegram_id, full_name, dob, phone_number, role, fetchrow=True)

    async def select_all_user_credentials(self):
        sql = "SELECT * FROM user_credentials;"
        return await self.execute(sql, fetch=True)

    async def select_user_credential(self, **kwargs):
        sql = "SELECT * FROM user_credentials WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_user_credential(self, telegram_id, **kwargs):
        sql = "UPDATE user_credentials SET "
        sql += ", ".join([f"{key} = ${idx + 2}" for idx, key in enumerate(kwargs.keys())])
        sql += " WHERE telegram_id = $1;"
        values = (telegram_id,) + tuple(kwargs.values())
        await self.execute(sql, *values, execute=True)

    async def delete_user_credential(self, telegram_id):
        sql = "DELETE FROM user_credentials WHERE telegram_id = $1;"
        await self.execute(sql, telegram_id, execute=True)
>>>>>>> master
