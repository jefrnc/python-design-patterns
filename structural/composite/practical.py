"""
Composite Design Pattern - Real World Implementation

A real-world example demonstrating the Composite pattern through a 
file system management application that handles both files and directories
uniformly while supporting complex operations like compression, search,
synchronization, and permission management.

This example shows how to:
- Treat individual files and directories uniformly
- Build hierarchical tree structures
- Implement recursive operations (size calculation, search, etc.)
- Handle complex file operations (copy, move, delete)
- Manage permissions and metadata
- Support different file types with specialized behavior
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Iterator, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import os
import hashlib
import mimetypes
from pathlib import Path


class FileType(Enum):
    """Types of files supported by the system."""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    EXECUTABLE = "executable"
    DIRECTORY = "directory"
    UNKNOWN = "unknown"


class Permission(Enum):
    """File system permissions."""
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"


@dataclass
class FileMetadata:
    """Comprehensive metadata for file system objects."""
    name: str
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    owner: str = "system"
    group: str = "users"
    permissions: Dict[str, Set[Permission]] = field(default_factory=lambda: {
        "owner": {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        "group": {Permission.READ, Permission.EXECUTE},
        "others": {Permission.READ}
    })
    file_type: FileType = FileType.UNKNOWN
    mime_type: str = "application/octet-stream"
    checksum: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchCriteria:
    """Criteria for searching file system objects."""
    name_pattern: Optional[str] = None
    file_type: Optional[FileType] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    owner: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    has_permission: Optional[Permission] = None


# Component Interface
class FileSystemObject(ABC):
    """
    Abstract base class for all file system objects.
    This is the Component in the Composite pattern.
    """
    
    def __init__(self, metadata: FileMetadata):
        self.metadata = metadata
        self.parent: Optional['Directory'] = None
    
    @abstractmethod
    def get_size(self) -> int:
        """Get the total size in bytes."""
        pass
    
    @abstractmethod
    def get_file_count(self) -> int:
        """Get the total number of files."""
        pass
    
    @abstractmethod
    def search(self, criteria: SearchCriteria) -> List['FileSystemObject']:
        """Search for objects matching criteria."""
        pass
    
    @abstractmethod
    def copy_to(self, destination_path: str) -> bool:
        """Copy this object to destination."""
        pass
    
    @abstractmethod
    def move_to(self, destination_path: str) -> bool:
        """Move this object to destination."""
        pass
    
    @abstractmethod
    def delete(self) -> bool:
        """Delete this object."""
        pass
    
    @abstractmethod
    def compress(self, compression_level: int = 5) -> bool:
        """Compress this object."""
        pass
    
    @abstractmethod
    def get_tree_representation(self, indent: int = 0) -> str:
        """Get string representation of the tree structure."""
        pass
    
    def get_path(self) -> str:
        """Get the full path of this object."""
        if self.parent is None:
            return self.metadata.name
        return f"{self.parent.get_path()}/{self.metadata.name}"
    
    def has_permission(self, user: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        if user == self.metadata.owner:
            return permission in self.metadata.permissions.get("owner", set())
        elif user in self.metadata.group:
            return permission in self.metadata.permissions.get("group", set())
        else:
            return permission in self.metadata.permissions.get("others", set())
    
    def set_permission(self, user_type: str, permissions: Set[Permission]) -> None:
        """Set permissions for user type (owner/group/others)."""
        self.metadata.permissions[user_type] = permissions
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to this object."""
        self.metadata.tags.add(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this object."""
        self.metadata.tags.discard(tag)
    
    def update_access_time(self) -> None:
        """Update the last access time."""
        self.metadata.accessed_at = datetime.now()


# Leaf Classes (Individual Files)
class RegularFile(FileSystemObject):
    """
    Represents a regular file in the file system.
    This is a Leaf in the Composite pattern.
    """
    
    def __init__(self, metadata: FileMetadata, content: bytes = b""):
        super().__init__(metadata)
        self.content = content
        self.metadata.size_bytes = len(content)
        self._calculate_checksum()
        self._determine_file_type()
    
    def _calculate_checksum(self) -> None:
        """Calculate and store file checksum."""
        if self.content:
            self.metadata.checksum = hashlib.sha256(self.content).hexdigest()
    
    def _determine_file_type(self) -> None:
        """Determine file type based on name and content."""
        mime_type, _ = mimetypes.guess_type(self.metadata.name)
        
        if mime_type:
            self.metadata.mime_type = mime_type
            
            if mime_type.startswith('text/') or mime_type in ['application/pdf', 'application/msword']:
                self.metadata.file_type = FileType.DOCUMENT
            elif mime_type.startswith('image/'):
                self.metadata.file_type = FileType.IMAGE
            elif mime_type.startswith('video/'):
                self.metadata.file_type = FileType.VIDEO
            elif mime_type.startswith('audio/'):
                self.metadata.file_type = FileType.AUDIO
            elif mime_type in ['application/zip', 'application/x-rar', 'application/x-tar']:
                self.metadata.file_type = FileType.ARCHIVE
            elif mime_type in ['application/x-executable', 'application/x-msdownload']:
                self.metadata.file_type = FileType.EXECUTABLE
    
    def get_size(self) -> int:
        """Get file size."""
        return self.metadata.size_bytes
    
    def get_file_count(self) -> int:
        """Files count as 1."""
        return 1
    
    def search(self, criteria: SearchCriteria) -> List[FileSystemObject]:
        """Search this file against criteria."""
        if self._matches_criteria(criteria):
            return [self]
        return []
    
    def _matches_criteria(self, criteria: SearchCriteria) -> bool:
        """Check if this file matches search criteria."""
        # Name pattern check
        if criteria.name_pattern and criteria.name_pattern not in self.metadata.name:
            return False
        
        # File type check
        if criteria.file_type and criteria.file_type != self.metadata.file_type:
            return False
        
        # Size checks
        if criteria.min_size and self.metadata.size_bytes < criteria.min_size:
            return False
        if criteria.max_size and self.metadata.size_bytes > criteria.max_size:
            return False
        
        # Date checks
        if criteria.created_after and self.metadata.created_at < criteria.created_after:
            return False
        if criteria.created_before and self.metadata.created_at > criteria.created_before:
            return False
        if criteria.modified_after and self.metadata.modified_at < criteria.modified_after:
            return False
        if criteria.modified_before and self.metadata.modified_at > criteria.modified_before:
            return False
        
        # Owner check
        if criteria.owner and criteria.owner != self.metadata.owner:
            return False
        
        # Tags check
        if criteria.tags and not criteria.tags.issubset(self.metadata.tags):
            return False
        
        # Permission check
        if criteria.has_permission:
            if criteria.has_permission not in self.metadata.permissions.get("owner", set()):
                return False
        
        return True
    
    def copy_to(self, destination_path: str) -> bool:
        """Copy file to destination."""
        try:
            # In a real implementation, this would copy the actual file
            print(f"Copying file '{self.metadata.name}' to '{destination_path}'")
            return True
        except Exception as e:
            print(f"Failed to copy file '{self.metadata.name}': {e}")
            return False
    
    def move_to(self, destination_path: str) -> bool:
        """Move file to destination."""
        try:
            # In a real implementation, this would move the actual file
            print(f"Moving file '{self.metadata.name}' to '{destination_path}'")
            if self.parent:
                self.parent.remove_child(self)
            return True
        except Exception as e:
            print(f"Failed to move file '{self.metadata.name}': {e}")
            return False
    
    def delete(self) -> bool:
        """Delete this file."""
        try:
            print(f"Deleting file '{self.metadata.name}'")
            if self.parent:
                self.parent.remove_child(self)
            return True
        except Exception as e:
            print(f"Failed to delete file '{self.metadata.name}': {e}")
            return False
    
    def compress(self, compression_level: int = 5) -> bool:
        """Compress file content."""
        try:
            # Simulate compression
            original_size = len(self.content)
            compression_ratio = 0.7 - (compression_level * 0.05)  # Higher level = better compression
            
            # In real implementation, would use actual compression
            simulated_compressed_size = int(original_size * compression_ratio)
            
            print(f"Compressing '{self.metadata.name}': {original_size} -> {simulated_compressed_size} bytes")
            self.metadata.size_bytes = simulated_compressed_size
            return True
        except Exception as e:
            print(f"Failed to compress file '{self.metadata.name}': {e}")
            return False
    
    def get_tree_representation(self, indent: int = 0) -> str:
        """Get string representation."""
        prefix = "  " * indent
        size_mb = self.metadata.size_bytes / (1024 * 1024)
        return f"{prefix}📄 {self.metadata.name} ({size_mb:.2f} MB) [{self.metadata.file_type.value}]"
    
    def read_content(self, user: str) -> Optional[bytes]:
        """Read file content if user has permission."""
        if self.has_permission(user, Permission.READ):
            self.update_access_time()
            return self.content
        return None
    
    def write_content(self, user: str, content: bytes) -> bool:
        """Write file content if user has permission."""
        if self.has_permission(user, Permission.WRITE):
            self.content = content
            self.metadata.size_bytes = len(content)
            self.metadata.modified_at = datetime.now()
            self._calculate_checksum()
            return True
        return False


class SymbolicLink(FileSystemObject):
    """
    Represents a symbolic link in the file system.
    This is a special type of Leaf.
    """
    
    def __init__(self, metadata: FileMetadata, target_path: str):
        super().__init__(metadata)
        self.target_path = target_path
        self.metadata.file_type = FileType.UNKNOWN
        self.metadata.size_bytes = 0
    
    def get_size(self) -> int:
        """Symbolic links have minimal size."""
        return 0
    
    def get_file_count(self) -> int:
        """Symbolic links count as 0 for file counting."""
        return 0
    
    def search(self, criteria: SearchCriteria) -> List[FileSystemObject]:
        """Search this symlink."""
        if criteria.name_pattern and criteria.name_pattern in self.metadata.name:
            return [self]
        return []
    
    def copy_to(self, destination_path: str) -> bool:
        """Copy symbolic link."""
        print(f"Copying symlink '{self.metadata.name}' -> '{self.target_path}' to '{destination_path}'")
        return True
    
    def move_to(self, destination_path: str) -> bool:
        """Move symbolic link."""
        print(f"Moving symlink '{self.metadata.name}' to '{destination_path}'")
        return True
    
    def delete(self) -> bool:
        """Delete symbolic link."""
        print(f"Deleting symlink '{self.metadata.name}'")
        if self.parent:
            self.parent.remove_child(self)
        return True
    
    def compress(self, compression_level: int = 5) -> bool:
        """Symbolic links can't be compressed."""
        print(f"Cannot compress symbolic link '{self.metadata.name}'")
        return False
    
    def get_tree_representation(self, indent: int = 0) -> str:
        """Get string representation."""
        prefix = "  " * indent
        return f"{prefix}🔗 {self.metadata.name} -> {self.target_path}"


# Composite Class (Directory)
class Directory(FileSystemObject):
    """
    Represents a directory in the file system.
    This is the Composite in the Composite pattern.
    """
    
    def __init__(self, metadata: FileMetadata):
        super().__init__(metadata)
        self.children: List[FileSystemObject] = []
        self.metadata.file_type = FileType.DIRECTORY
        self.metadata.size_bytes = 0
    
    def add_child(self, child: FileSystemObject) -> None:
        """Add a child object to this directory."""
        if child.metadata.name not in [c.metadata.name for c in self.children]:
            self.children.append(child)
            child.parent = self
            self._update_size()
        else:
            raise ValueError(f"Object with name '{child.metadata.name}' already exists")
    
    def remove_child(self, child: FileSystemObject) -> bool:
        """Remove a child object from this directory."""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self._update_size()
            return True
        return False
    
    def get_child(self, name: str) -> Optional[FileSystemObject]:
        """Get child by name."""
        for child in self.children:
            if child.metadata.name == name:
                return child
        return None
    
    def _update_size(self) -> None:
        """Update directory size based on children."""
        self.metadata.size_bytes = sum(child.get_size() for child in self.children)
        self.metadata.modified_at = datetime.now()
    
    def get_size(self) -> int:
        """Get total size of directory and all contents."""
        return sum(child.get_size() for child in self.children)
    
    def get_file_count(self) -> int:
        """Get total number of files in directory and subdirectories."""
        return sum(child.get_file_count() for child in self.children)
    
    def search(self, criteria: SearchCriteria) -> List[FileSystemObject]:
        """Search this directory and all subdirectories."""
        results = []
        
        # Check if this directory matches
        if self._matches_directory_criteria(criteria):
            results.append(self)
        
        # Search all children
        for child in self.children:
            results.extend(child.search(criteria))
        
        return results
    
    def _matches_directory_criteria(self, criteria: SearchCriteria) -> bool:
        """Check if this directory matches search criteria."""
        # Only check criteria that apply to directories
        if criteria.name_pattern and criteria.name_pattern not in self.metadata.name:
            return False
        
        if criteria.file_type and criteria.file_type != FileType.DIRECTORY:
            return False
        
        if criteria.owner and criteria.owner != self.metadata.owner:
            return False
        
        if criteria.tags and not criteria.tags.issubset(self.metadata.tags):
            return False
        
        return True
    
    def copy_to(self, destination_path: str) -> bool:
        """Copy directory and all contents."""
        try:
            print(f"Copying directory '{self.metadata.name}' to '{destination_path}'")
            
            # Copy all children
            for child in self.children:
                child_dest = f"{destination_path}/{self.metadata.name}/{child.metadata.name}"
                child.copy_to(child_dest)
            
            return True
        except Exception as e:
            print(f"Failed to copy directory '{self.metadata.name}': {e}")
            return False
    
    def move_to(self, destination_path: str) -> bool:
        """Move directory and all contents."""
        try:
            print(f"Moving directory '{self.metadata.name}' to '{destination_path}'")
            
            # Move all children
            for child in self.children:
                child_dest = f"{destination_path}/{self.metadata.name}/{child.metadata.name}"
                child.move_to(child_dest)
            
            if self.parent:
                self.parent.remove_child(self)
            
            return True
        except Exception as e:
            print(f"Failed to move directory '{self.metadata.name}': {e}")
            return False
    
    def delete(self) -> bool:
        """Delete directory and all contents."""
        try:
            print(f"Deleting directory '{self.metadata.name}' and all contents")
            
            # Delete all children first
            for child in self.children[:]:  # Copy list to avoid modification during iteration
                child.delete()
            
            if self.parent:
                self.parent.remove_child(self)
            
            return True
        except Exception as e:
            print(f"Failed to delete directory '{self.metadata.name}': {e}")
            return False
    
    def compress(self, compression_level: int = 5) -> bool:
        """Compress all files in directory."""
        try:
            print(f"Compressing directory '{self.metadata.name}' (level {compression_level})")
            
            success_count = 0
            for child in self.children:
                if child.compress(compression_level):
                    success_count += 1
            
            self._update_size()
            print(f"Successfully compressed {success_count}/{len(self.children)} items")
            return success_count > 0
        except Exception as e:
            print(f"Failed to compress directory '{self.metadata.name}': {e}")
            return False
    
    def get_tree_representation(self, indent: int = 0) -> str:
        """Get string representation of directory tree."""
        prefix = "  " * indent
        size_mb = self.get_size() / (1024 * 1024)
        tree = f"{prefix}📁 {self.metadata.name}/ ({size_mb:.2f} MB, {self.get_file_count()} files)"
        
        for child in self.children:
            tree += "\n" + child.get_tree_representation(indent + 1)
        
        return tree
    
    def create_file(self, name: str, content: bytes = b"", owner: str = "system") -> RegularFile:
        """Create a new file in this directory."""
        metadata = FileMetadata(
            name=name,
            owner=owner,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        file_obj = RegularFile(metadata, content)
        self.add_child(file_obj)
        return file_obj
    
    def create_directory(self, name: str, owner: str = "system") -> 'Directory':
        """Create a new subdirectory."""
        metadata = FileMetadata(
            name=name,
            owner=owner,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        dir_obj = Directory(metadata)
        self.add_child(dir_obj)
        return dir_obj
    
    def create_symlink(self, name: str, target_path: str, owner: str = "system") -> SymbolicLink:
        """Create a symbolic link in this directory."""
        metadata = FileMetadata(
            name=name,
            owner=owner,
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        
        symlink_obj = SymbolicLink(metadata, target_path)
        self.add_child(symlink_obj)
        return symlink_obj
    
    def list_contents(self, show_hidden: bool = False) -> List[FileSystemObject]:
        """List directory contents."""
        if show_hidden:
            return self.children[:]
        else:
            return [child for child in self.children if not child.metadata.name.startswith('.')]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive directory statistics."""
        file_types = {}
        total_files = 0
        total_dirs = 0
        
        for child in self.children:
            if isinstance(child, Directory):
                total_dirs += 1
                child_stats = child.get_statistics()
                total_files += child_stats['total_files']
                total_dirs += child_stats['total_directories']
                
                # Merge file type counts
                for file_type, count in child_stats['file_types'].items():
                    file_types[file_type] = file_types.get(file_type, 0) + count
            else:
                total_files += 1
                file_type = child.metadata.file_type.value
                file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_size_bytes': self.get_size(),
            'total_files': total_files,
            'total_directories': total_dirs,
            'direct_children': len(self.children),
            'file_types': file_types,
            'last_modified': self.metadata.modified_at
        }


# Specialized Directory Types
class ProjectDirectory(Directory):
    """A specialized directory for software projects."""
    
    def __init__(self, metadata: FileMetadata, project_type: str = "general"):
        super().__init__(metadata)
        self.project_type = project_type
        self.metadata.custom_attributes['project_type'] = project_type
        self._setup_project_structure()
    
    def _setup_project_structure(self) -> None:
        """Setup standard project directory structure."""
        if self.project_type == "python":
            self.create_directory("src")
            self.create_directory("tests")
            self.create_directory("docs")
            self.create_file("README.md", b"# Project README")
            self.create_file("requirements.txt", b"")
            self.create_file(".gitignore", b"__pycache__/\n*.pyc\n")
        elif self.project_type == "web":
            self.create_directory("assets")
            self.create_directory("css")
            self.create_directory("js")
            self.create_file("index.html", b"<!DOCTYPE html><html></html>")
    
    def add_dependency(self, dependency: str) -> None:
        """Add dependency to project."""
        requirements_file = self.get_child("requirements.txt")
        if isinstance(requirements_file, RegularFile):
            current_content = requirements_file.content.decode('utf-8')
            new_content = f"{current_content}\n{dependency}"
            requirements_file.write_content("system", new_content.encode('utf-8'))


# FileSystem Manager (Client)
class FileSystemManager:
    """
    Manager class for file system operations.
    Demonstrates how to work with the Composite pattern.
    """
    
    def __init__(self):
        self.root = Directory(FileMetadata("root", owner="system"))
        self.current_directory = self.root
    
    def change_directory(self, path: str) -> bool:
        """Change current directory."""
        if path == "/":
            self.current_directory = self.root
            return True
        elif path == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
                return True
            return False
        else:
            child = self.current_directory.get_child(path)
            if isinstance(child, Directory):
                self.current_directory = child
                return True
            return False
    
    def list_directory(self) -> None:
        """List current directory contents."""
        print(f"\nContents of {self.current_directory.get_path()}:")
        print("-" * 50)
        for child in self.current_directory.list_contents():
            size_mb = child.get_size() / (1024 * 1024)
            type_icon = "📁" if isinstance(child, Directory) else "📄"
            print(f"{type_icon} {child.metadata.name:<20} {size_mb:>8.2f} MB")
    
    def search_files(self, criteria: SearchCriteria) -> List[FileSystemObject]:
        """Search files from current directory."""
        return self.current_directory.search(criteria)
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage statistics."""
        return {
            'total_size_gb': self.root.get_size() / (1024**3),
            'total_files': self.root.get_file_count(),
            'directory_stats': self.root.get_statistics()
        }
    
    def backup_directory(self, source_path: str, backup_path: str) -> bool:
        """Backup a directory."""
        source = self.root.search(SearchCriteria(name_pattern=source_path))
        if source and isinstance(source[0], Directory):
            return source[0].copy_to(backup_path)
        return False
    
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories."""
        def is_empty_directory(obj):
            return isinstance(obj, Directory) and len(obj.children) == 0
        
        empty_dirs = self.root.search(SearchCriteria())
        empty_dirs = [d for d in empty_dirs if is_empty_directory(d)]
        
        for empty_dir in empty_dirs:
            empty_dir.delete()
        
        return len(empty_dirs)


# Demonstration Function
def demonstrate_composite_pattern():
    """Demonstrate the Composite pattern with file system operations."""
    
    print("=== File System Management - Composite Pattern Demo ===\n")
    
    # Create file system manager
    fs = FileSystemManager()
    
    # Create directory structure
    print("1. Creating Directory Structure:")
    print("-" * 40)
    
    # Create main directories
    documents = fs.root.create_directory("Documents", "alice")
    downloads = fs.root.create_directory("Downloads", "alice")
    projects = ProjectDirectory(
        FileMetadata("Projects", owner="alice"),
        project_type="python"
    )
    fs.root.add_child(projects)
    
    # Add files to Documents
    resume = documents.create_file("resume.pdf", b"PDF content for resume", "alice")
    resume.metadata.file_type = FileType.DOCUMENT
    resume.add_tag("important")
    resume.add_tag("personal")
    
    photo = documents.create_file("vacation.jpg", b"JPEG image data", "alice")
    photo.metadata.file_type = FileType.IMAGE
    photo.add_tag("vacation")
    
    # Add files to Downloads
    movie = downloads.create_file("movie.mp4", b"Video content" * 1000, "alice")
    movie.metadata.file_type = FileType.VIDEO
    
    software = downloads.create_file("installer.exe", b"Executable content", "alice")
    software.metadata.file_type = FileType.EXECUTABLE
    
    # Create nested structure
    work = documents.create_directory("Work")
    presentations = work.create_directory("Presentations")
    
    # Add work files
    presentation = presentations.create_file("quarterly_report.pptx", b"PowerPoint content", "alice")
    presentation.metadata.file_type = FileType.DOCUMENT
    presentation.add_tag("work")
    presentation.add_tag("quarterly")
    
    # Create symbolic link
    fs.root.create_symlink("quick_access_docs", "/Documents")
    
    # Display file system tree
    print("File System Structure:")
    print(fs.root.get_tree_representation())
    print()
    
    # Demonstrate uniform interface
    print("2. Uniform Interface Operations:")
    print("-" * 40)
    
    # Calculate sizes
    print(f"Total system size: {fs.root.get_size() / (1024*1024):.2f} MB")
    print(f"Documents size: {documents.get_size() / (1024*1024):.2f} MB")
    print(f"Single file size: {movie.get_size() / (1024*1024):.2f} MB")
    print()
    
    # File count
    print(f"Total files in system: {fs.root.get_file_count()}")
    print(f"Files in Documents: {documents.get_file_count()}")
    print(f"Files in Downloads: {downloads.get_file_count()}")
    print()
    
    # Search operations
    print("3. Search Operations:")
    print("-" * 40)
    
    # Search by file type
    image_criteria = SearchCriteria(file_type=FileType.IMAGE)
    images = fs.root.search(image_criteria)
    print(f"Found {len(images)} image files:")
    for img in images:
        print(f"  - {img.get_path()}")
    print()
    
    # Search by tags
    work_criteria = SearchCriteria(tags={"work"})
    work_files = fs.root.search(work_criteria)
    print(f"Found {len(work_files)} work-related files:")
    for work_file in work_files:
        print(f"  - {work_file.get_path()}")
    print()
    
    # Search by name pattern
    pdf_criteria = SearchCriteria(name_pattern=".pdf")
    pdf_files = fs.root.search(pdf_criteria)
    print(f"Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.get_path()}")
    print()
    
    # Complex operations
    print("4. Complex Operations:")
    print("-" * 40)
    
    # Compression
    print("Compressing Downloads directory:")
    downloads.compress(compression_level=7)
    print(f"Downloads size after compression: {downloads.get_size() / (1024*1024):.2f} MB")
    print()
    
    # Copy operation
    print("Copying Documents to backup location:")
    documents.copy_to("/backup/documents_backup")
    print()
    
    # Permission management
    print("5. Permission Management:")
    print("-" * 40)
    
    # Check permissions
    can_read = resume.has_permission("alice", Permission.READ)
    can_write = resume.has_permission("bob", Permission.WRITE)
    
    print(f"Alice can read resume: {can_read}")
    print(f"Bob can write resume: {can_write}")
    
    # Change permissions
    resume.set_permission("others", {Permission.READ})
    print("Changed resume permissions for others to read-only")
    print()
    
    # Statistics
    print("6. System Statistics:")
    print("-" * 40)
    
    stats = fs.get_disk_usage()
    print(f"Total disk usage: {stats['total_size_gb']:.3f} GB")
    print(f"Total files: {stats['total_files']}")
    
    dir_stats = stats['directory_stats']
    print(f"File type distribution:")
    for file_type, count in dir_stats['file_types'].items():
        print(f"  {file_type}: {count} files")
    print()
    
    # Navigation
    print("7. Directory Navigation:")
    print("-" * 40)
    
    fs.list_directory()
    
    print("\nChanging to Documents directory:")
    fs.change_directory("Documents")
    fs.list_directory()
    
    print("\nChanging to Work subdirectory:")
    fs.change_directory("Work")
    fs.list_directory()
    
    print("\nReturning to root:")
    fs.change_directory("/")
    print()
    
    # Cleanup operations
    print("8. Cleanup Operations:")
    print("-" * 40)
    
    # Create and remove empty directory
    empty_dir = fs.root.create_directory("EmptyTemp")
    print(f"Created empty directory: {empty_dir.metadata.name}")
    
    removed_count = fs.cleanup_empty_directories()
    print(f"Removed {removed_count} empty directories")
    print()
    
    print("=== Composite Pattern Benefits Demonstrated ===")
    print("✓ Uniform treatment of files and directories")
    print("✓ Recursive operations on tree structures")
    print("✓ Easy addition of new file system object types")
    print("✓ Complex operations (search, copy, compress) work on any level")
    print("✓ Transparent navigation and manipulation")


if __name__ == "__main__":
    demonstrate_composite_pattern()