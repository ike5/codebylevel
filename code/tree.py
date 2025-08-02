import json
import os
from typing import Optional


class TreeNode:
    def __init__(self, file_name, version, language, file_path):
        self.file_name = file_name
        self.version = version
        self.language = language
        self.file_path = file_path
        self.left = None
        self.right = None

    def key(self):
        return (self.file_name, self._version_tuple(), self.language)

    def _version_tuple(self):
        return tuple(map(int, self.version.split(".")))

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "version": self.version,
            "language": self.language,
            "file_path": self.file_path,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        node = cls(data["file_name"], data["version"], data["language"], data["file_path"])
        node.left = cls.from_dict(data["left"])
        node.right = cls.from_dict(data["right"])
        return node


class FileBinaryTree:
    def __init__(self, save_file="tree_data.json"):
        self.root: Optional[TreeNode] = None
        self.save_file = save_file
        self.load()

    def _compare(self, a, b):
        return (a > b) - (a < b)

    def insert(self, file_name, version, language, file_path):
        def _insert(node, new_node):
            if not node:
                return new_node
            if self._compare(new_node.key(), node.key()) < 0:
                node.left = _insert(node.left, new_node)
            else:
                node.right = _insert(node.right, new_node)
            return node

        new_node = TreeNode(file_name, version, language, file_path)
        self.root = _insert(self.root, new_node)
        self.save()

    def search(self, file_name, version, language):
        def _search(node, target_key):
            if not node:
                return None
            if node.key() == target_key:
                return node
            elif self._compare(target_key, node.key()) < 0:
                return _search(node.left, target_key)
            else:
                return _search(node.right, target_key)

        key = (file_name, tuple(map(int, version.split("."))), language)
        return _search(self.root, key)

    def save(self):
        with open(self.save_file, "w") as f:
            json.dump(self.root.to_dict() if self.root else None, f, indent=2)

    def load(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.root = TreeNode.from_dict(data)

    def list_all(self):
        def _in_order(node):
            if not node:
                return []
            return _in_order(node.left) + [(node.file_name, node.version, node.language)] + _in_order(node.right)

        return _in_order(self.root)
