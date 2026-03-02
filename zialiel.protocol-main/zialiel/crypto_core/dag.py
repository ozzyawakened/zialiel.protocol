
import logging
from typing import Dict, List, Set

from .vertex import Vertex, SuperVertex

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DAG:
    """
    Manages the Directed Acyclic Graph of vertices and super-vertices.
    """
    def __init__(self):
        self.vertices: Dict[str, Vertex] = {}
        self.super_vertices: Dict[str, SuperVertex] = {}
        self.tips: Set[str] = set()

    def add_vertex(self, vertex: Vertex) -> bool:
        """
        Adds a new vertex to the DAG after validation.
        """
        if vertex.hash in self.vertices:
            logging.warning(f"Attempted to add duplicate vertex {vertex.hash}.")
            return False

        # Tillat 'genesis' som spesiell parent
        for parent_hash in vertex.parent_hashes:
            if parent_hash == 'genesis':
                continue  # Genesis er alltid gyldig
            if parent_hash not in self.vertices:
                logging.error(f"Parent vertex {parent_hash} not found for new vertex {vertex.hash}. Cannot add.")
                return False

        self.vertices[vertex.hash] = vertex
        self._update_tips(vertex)
        logging.info(f"Added vertex {vertex.hash[:8]} to the DAG.")
        return True

    def add_super_vertex(self, super_vertex: SuperVertex) -> bool:
        """
        Adds a new super-vertex to the DAG.
        """
        if super_vertex.hash in self.super_vertices:
            logging.warning(f"Attempted to add duplicate super-vertex {super_vertex.hash}.")
            return False
        
        self.super_vertices[super_vertex.hash] = super_vertex
        logging.info(f"Added super-vertex {super_vertex.hash[:8]} to the DAG.")
        return True

    def _update_tips(self, new_vertex: Vertex):
        """
        Updates the set of tips after a new vertex is added.
        """
        # Remove parents from tips
        for parent_hash in new_vertex.parent_hashes:
            if parent_hash in self.tips:
                self.tips.remove(parent_hash)
        
        # Add new vertex as tip
        self.tips.add(new_vertex.hash)

    def get_tips(self) -> List[str]:
        """Returns the current list of tip hashes."""
        return list(self.tips)

    def get_vertex(self, vertex_hash: str):
        """Retrieves a vertex by its hash."""
        return self.vertices.get(vertex_hash)

    def get_unconfirmed_vertices(self) -> List[Vertex]:
        """
        Gets vertices not yet included in a super-vertex.
        """
        confirmed_hashes = set()
        for sv in self.super_vertices.values():
            confirmed_hashes.update(sv.cohort_hashes)
        
        return [v for h, v in self.vertices.items() if h not in confirmed_hashes]

