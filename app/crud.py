from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas

# Создание новой книги
async def create_book(db: AsyncSession, book: schemas.BookCreate):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

# Получение всех книг
async def get_books(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    book_name: str = None,
    author: str = None,
    genre: str = None,
    date_from: str = None,
    date_to: str = None,
    price_min: float = None,
    price_max: float = None
):
    from sqlalchemy import and_
    from sqlalchemy import select
    filters = []
    if book_name:
        filters.append(models.Book.book_name.ilike(f"%{book_name}%"))
    if author:
        filters.append(models.Book.author.ilike(f"%{author}%"))
    if genre:
        filters.append(models.Book.genre.ilike(f"%{genre}%"))
    if date_from:
        filters.append(models.Book.date_issue >= date_from)
    if date_to:
        filters.append(models.Book.date_issue <= date_to)
    if price_min is not None:
        filters.append(models.Book.price >= price_min)
    if price_max is not None:
        filters.append(models.Book.price <= price_max)
    stmt = select(models.Book)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# Получение книги по ID
async def get_book(db: AsyncSession, book_id: int):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    return result.scalars().first()

# Обновление книги
async def update_book(db: AsyncSession, book_id: int, book: schemas.BookCreate):
    db_book = await get_book(db, book_id)
    if db_book:
        db_book.book_name = book.book_name
        db_book.author = book.author
        db_book.genre = book.genre
        db_book.date_issue = book.date_issue
        db_book.price = book.price
        await db.commit()
        await db.refresh(db_book)
    return db_book

# Удаление книги
async def delete_book(db: AsyncSession, book_id: int):
    db_book = await get_book(db, book_id)
    if db_book:
        await db.delete(db_book)
        await db.commit()
    return db_book
