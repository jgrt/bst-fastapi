from neo4j import GraphDatabase
import os
import logging
from neo4j.data import Record

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Database:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASS"]),
        )

    def close(self):
        self.driver.close()

    @staticmethod
    def _create_and_return_root(tx) -> Record:
        result = tx.run("CREATE (root { name: 'ROOT',value: 10 }) RETURN root")
        return result.single()

    def create_root(self) -> Record:
        with self.driver.session() as session:
            root = session.write_transaction(self._create_and_return_root)
        return root

    @staticmethod
    def _get_root(tx) -> Record:
        root = tx.run(
            "MATCH (element) WHERE EXISTS(element.name) return element LIMIT 1"
        )
        return root.single()

    def get_root(self) -> Record:
        with self.driver.session() as session:
            root = session.read_transaction(self._get_root)
        return root

    @staticmethod
    def _get_node(tx, value) -> Record:
        node = tx.run(
            "MATCH (element) where element.value=$value return element", value=value
        )
        return node.single()

    def get_node(self, value) -> Record:
        with self.driver.session() as session:
            node = session.read_transaction(self._get_node, value)
        return node

    @staticmethod
    def _get_child(tx, root: Record, method: str) -> Record:
        child = tx.run(
            "MATCH (n { value: $value })-[:" + method + "]->(element) RETURN element",
            value=root["element"]["value"],
        )
        return child.single()

    def get_child(self, root: Record, method: str) -> Record:
        with self.driver.session() as session:
            child = session.read_transaction(self._get_child, root=root, method=method)
        return child

    @staticmethod
    def _insert(tx, root: Record, value: int, method: str) -> Record:

        node = tx.run(
            "CREATE (node$root)-[:"
            + method
            + "]->(node"
            + str(value)
            + " {value : $value})",
            root=root["element"]["value"],
            value=value,
        )
        return node.single()

    def create_node(self, root: Record, value: int, method: str) -> Record:
        with self.driver.session() as session:
            child_node = session.write_transaction(
                self._insert, root=root, value=value, method=method
            )
        return child_node

    def insert(self, value: int, root=None, start=False, parent=None) -> Record:
        print(value, root, start, parent)

        """
        start = True, root = None, starting condition
        start = True, root = Not None, invalid condition
        start = False, root = None, end condition
        start = False, root = Not None, subtree condition
        """

        if start and root:
            raise ValueError("Can not start with root node.")

        if start and not root:
            node = self.get_node(value)
            if node:
                logger.debug("node already exists")
                return node
            return self.insert(value=value, root=self.get_root(), start=False)

        if not start:
            if root:
                print(type(root))
                method = (
                    "LEFTCHILD" if root["element"]["value"] > value else "RIGHTCHILD"
                )
                child = self.get_child(root=root, method=method)
                return self.insert(root=child, value=value, start=False, parent=root)

            method = "LEFTCHILD" if parent["element"]["value"] > value else "RIGHTCHILD"
            return self.create_node(root=parent, value=value, method=method)
