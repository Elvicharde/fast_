# main.py
""" Author:
    e-mail:
    Description: This is the entry point for the sample fast API project
"""
# importing relevant libraries and tools
from fastapi import FastAPI, status, Response, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import os
from os import system as SYS, name as SYS_NAME

app = FastAPI()

# 1 -  defining data schema for validating frontend data


class Item(BaseModel):
    name: str
    description: str
    quantity: int
    in_stock: bool = True


def clear(): return SYS('cls') if SYS_NAME == 'nt' else SYS('clear')


# 2 - setting up the database connection to PostgreSql
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='inventory', user='postgres',
                                password='sectumsempra', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
    except Exception as e:
        clear()
        print("\nConnection to database failed!\n")
        print(f"[Error]: {e}")
        time.sleep(3)
    else:
        clear()
        print("\n[Success]: Connection to database successful!\n")
        break


# 3 - Defining endpoints/routes
# GET OPERATIONS

# get all items
@app.get("/items")
def get_all_items():
    query = """SELECT * FROM items"""
    try:
        cursor.execute(query)
    except Exception as e:
        print(f"[Error]: {e}")
        return {"error": "Failed to complete the fetch operation!!"}
    else:
        all_items = cursor.fetchall()
    return {"data": all_items}

# get specific item by id


@app.get("/items/{id}")
def get_single_item(id: int, response: Response):
    query = """SELECT * FROM items WHERE id = %s"""
    try:
        cursor.execute(query, (str(id),))
        item = cursor.fetchone()

    except Exception as e:
        print(f"[Error]: {e}")
    else:
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Item with id {id} was not found!")
    return {"data": item}

# POST OPERATIONS
# add items to the database


@app.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(payload: Item):
    query = """INSERT INTO items (name, description, quantity, in_stock) VALUES (%s, %s, %s, %s) RETURNING *"""
    values = (payload.name, payload.description,
              payload.quantity, payload.in_stock)
    try:
        cursor.execute(query, values)
    except Exception as e:
        print(f"[Error]: {e}")
        return {"error": "Failed to complete insert operation!!"}
    else:
        new_item = cursor.fetchone()
        conn.commit()    # saving the changes to the db

    return {"data": new_item}

# DELETE OPERATIONS
# delete item by id


@app.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(id: int):
    query = """DELETE FROM items WHERE id = %s RETURNING *"""
    try:
        cursor.execute(query, (str(id),))
        deleted_item = cursor.fetchone()
        conn.commit()

    except Exception as e:
        print(f"[Error]: {e}")
    else:
        if deleted_item == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Item with id {id} was not found!")

    return
