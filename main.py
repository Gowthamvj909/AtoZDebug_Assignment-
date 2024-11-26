from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File
import uvicorn
from fastapi.security import HTTPBasicCredentials
from db_operations.db import users_collection, books_collection
from utils.auth_utils import create_token
from core.dependencies import get_current_user, check_role
from core.config import UPLOAD_DIR
from pathlib import Path
from bson import ObjectId
from fastapi.responses import FileResponse


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Library Management System"}


# Authentication Endpoints
@app.post("/login/")
async def login(credentials: HTTPBasicCredentials, response: Response):
    """
    User login endpoint. Verifies credentials and creates a session.

    Args:
        credentials (HTTPBasicCredentials): Contains username and password.
        response (Response): Used to set cookies.

    Returns:
        dict: A success message.
    """
    user = users_collection.find_one({"username": credentials.username})
    if not user or credentials.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, expiry = create_token(user["username"])
    response.set_cookie("library_session", token, httponly=True, max_age=expiry)
    return {"message": "Logged in successfully"}


@app.post("/logout/")
async def logout(response: Response):
    """
    User logout endpoint. Deletes the session cookie.

    Args:
        response (Response): Used to delete cookies.

    Returns:
        dict: A success message.
    """
    response.delete_cookie("library_session")
    return {"message": "Logged out successfully"}


# Admin Endpoints
@app.post("/books/")
async def add_book(
    title: str, 
    author: str, 
    file: UploadFile = File(...), 
    user=Depends(get_current_user)
):
    """
    Add a new book. Only accessible by Admin users.

    Args:
        title (str): Title of the book.
        author (str): Author of the book.
        file (UploadFile): File to upload.
        user (dict): Current authenticated user.

    Returns:
        dict: Success message and inserted book ID.
    """
    check_role(user, "Admin")
    
    # Save the uploaded file
    file_path = UPLOAD_DIR / file.filename

    # Insert book details into the database
    book = {
        "title": title,
        "author": author,
        "file_path": str(file_path),
    }
    result = books_collection.insert_one(book)
    return {"message": "Book added", "book_id": str(result.inserted_id)}


# Admin Endpoints
@app.put("/books/{book_id}")
async def update_book(
    book_id: str, 
    title: str = None, 
    author: str = None, 
    file: UploadFile = None, 
    user=Depends(get_current_user)
):
    """
    Update an existing book. Only accessible by Admin users.

    Args:
        book_id (str): ID of the book to update.
        title (str, optional): New title of the book.
        author (str, optional): New author of the book.
        file (UploadFile, optional): New file to upload.
        user (dict): Current authenticated user.

    Returns:
        dict: Success message.
    """
    check_role(user, "Admin")
    
    # Find the book
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update the file if provided
    update_data = {}
    if title:
        update_data["title"] = title
    if author:
        update_data["author"] = author
    if file:
        # Save the new file
        file_path = UPLOAD_DIR / file.filename
        # with open(file_path, "wb") as f:
        #     f.write(await file.read())
        update_data["file_path"] = str(file_path)

    # Update the database
    books_collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})
    return {"message": "Book updated successfully"}


# Admin Endpoints
@app.delete("/books/{book_id}")
async def delete_book(book_id: str, user=Depends(get_current_user)):
    """
    Delete an existing book. Only accessible by Admin users.

    Args:
        book_id (str): ID of the book to delete.
        user (dict): Current authenticated user.

    Returns:
        dict: Success message.
    """
    check_role(user, "Admin")
    books_collection.delete_one({"_id": ObjectId(book_id)})
    return {"message": "Book deleted successfully"}


# Admin & Member Endpoints
@app.get("/books/")
async def get_books(user=Depends(get_current_user)):
    """
    Fetch the list of all books. Accessible by both Admin and Member users.

    Args:
        user (dict): Current authenticated user.

    Returns:
        list: List of books.
    """
    # Use aggregation to convert _id to string and include all other fields
    books_cursor = books_collection.aggregate([
        {"$addFields": {"_id": {"$toString": "$_id"}}}
    ])
    # Convert the cursor to a list
    books = list(books_cursor)

    return books


@app.get("/books/{book_id}")
async def download_book(book_id: str, user=Depends(get_current_user)):
    """
    Download the file associated with a book. Accessible by both Admin and Member users.

    Args:
        book_id (str): ID of the book to download.
        user (dict): Current authenticated user.

    Returns:
        FileResponse: The file to download.
    """
    book = books_collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    file_path = Path(book["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Return FileResponse with book details as headers
    headers = {
        "X-Book-Title": book.get("title", "Unknown"),
        "X-Book-Author": book.get("author", "Unknown")
    }
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_path.name,
        headers=headers
    )
    # return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)



if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=5000, reload=True, workers=1
        )