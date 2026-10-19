"""Shared in-memory store for books and memebers used as the alternative service implementation to the database service."""

# Import the dataclass decorator and field function from the dataclasses module to define data classes and their fields.
from dataclasses import dataclass, field
# Import the RLock class from the threading module to create a reentrant lock for thread-safe operations on the in-memory store.
from threading import RLock

from app.models.book import Book
from app.models.members import Member

@dataclass
class InMemoryStore:
    """Hold books and memebers for one application instance. 
    This is a singleton class that is used to store books and members in memory for the duration of the application instance. 
    It is not persistent and will be lost when the application is restarted."""

    books: list[Book] = field(default_factory=list)
    members: list[Member] = field(default_factory=list)
    # Create a reentrant lock to ensure thread-safe operations on the in-memory store.
    lock: RLock = field(default_factory=RLock, repr=False)