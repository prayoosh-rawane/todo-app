#Path and Query can help us to validate path paramters
from fastapi import FastAPI, Path, Query, HTTPException 
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status

app  = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date
    
class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed for create", default=None)
    title: str = Field(min_length=3, max_length=100)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=150)
    rating: int = Field(gt=1, lt=6)
    published_date: int = Field(gt=1900, lt=2026)

    # to provide default value in the swagger using pydantic
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "New Book",
                "author": "CodingWithPrayoosh",
                "description": "A description of the new book.",
                "rating": 4,
                "published_date": 2024
            }
        } 
    }


BOOKS = [
    Book(1, "Computer Science Pro", "John Doe", "A comprehensive guide to computer science.", 5, 1999),
    Book(2, "Python Programming", "Jane Smith", "Learn Python programming from scratch.", 4, 2003),
    Book(3, "Data Structures and Algorithms", "Alice Johnson", "A guide to data structures and algorithms.", 3, 2020),
    Book(4, "HP1", "Alice Johnson", "Book Description", 5, 2020),
    Book(5, "HP2", "Alice Johnson", "Book Description", 3, 2009),
    Book(6, "HP3", "Alice Johnson", "Book Description", 4, 2015)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/publish", status_code=status.HTTP_200_OK)
async def read_books_by_published_date(published_date: int = Query(gt=1900, lt=2026)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)

    return books_to_return

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=1, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)

    return books_to_return




@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # ** converts the key as keyword argumnet and pass it to the book class
    # also pydantic 2 use model_dump and dict function is deprecated
    new_book = Book(**book_request.model_dump())
    print("newBOOK", new_book)
    BOOKS.append(find_book_id(new_book))


def find_book_id(book: Book):
    # if  len(BOOKS) > 0: 
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

    
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_request: BookRequest):
    book_changed = False
    print(book_request)
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_request.id:
            BOOKS[i] = book_request
            book_changed = True

    if not book_changed:
        raise HTTPException(status_code=404, detail=f"Book with id {book_request.id} not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    
    if not book_changed:
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")

