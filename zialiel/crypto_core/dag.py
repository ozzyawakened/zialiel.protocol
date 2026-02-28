
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
        self.tips: Set[str] = set()  # Hashes of vertices that are tips of the DAG

    def add_vertex(self, vertex: Vertex) -> bool:
        """
        Adds a new vertex to the DAG after validation.

        Args:
            vertex (Vertex): The vertex to add.

        Returns:
            bool: True if the vertex was added successfully, False otherwise.
        """
        if vertex.hash in self.vertices:
            logging.warning(f"Attempted to add duplicate vertex {vertex.hash}.")
            return False

        # Basic validation: ensure parents exist
        for parent_hash in vertex.parent_hashes:
            if parent_hash not in self.vertices:
                logging.error(f"Parent vertex {parent_hash} not found for new vertex {vertex.hash}. Cannot add.")
                return False

        self.vertices[vertex.hash] = vertex
        self._update_tips(vertex)
        logging.info(f"Added vertex {vertex.hash} to the DAG.")
        return True

    def add_super_vertex(self, super_vertex: SuperVertex) -> bool:
        """
        Adds a new super-vertex to the DAG.
        """
        if super_vertex.hash in self.super_vertices:
            logging.warning(f"Attempted to add duplicate super-vertex {super_vertex.hash}.")
            return False
        
        # In a real scenario, we would validate the cohort and merkle roots here
        self.super_vertices[super_vertex.hash] = super_vertex
        logging.info(f"Added super-vertex {super_vertex.hash} to the DAG.")
        return True

    def _update_tips(self, new_vertex: Vertex):
        """
        Updates the set of tips after a new vertex is added.
        A tip is a vertex that is not a parent to any other vertex.
        """
        # Remove parents of the new vertex from the tips set
        for parent_hash in new_vertex.parent_hashes:
            if parent_hash in self.tips:
                self.tips.remove(parent_hash)
        
        # Add the new vertex as a tip
        self.tips.add(new_vertex.hash)

    def get_tips(self) -> List[str]:
        """Returns the current list of tip hashes."""
        return list(self.tips)

    def get_vertex(self, vertex_hash: str) -> Vertex:
        """Retrieves a vertex by its hash."""
        return self.vertices.get(vertex_hash)

    def get_unconfirmed_vertices(self) -> List[Vertex]:
        """
        Placeholder for getting vertices not yet included in a super-vertex.
        In a real implementation, this would involve tracking vertex confirmation status.
        """
        # This is a simplified logic. A real system needs a robust way to track this.
        confirmed_hashes = set()
        for sv in self.super_vertices.values():
            confirmed_hashes.update(sv.cohort_hashes)
        
        return [v for h, v in self.vertices.items() if h not in confirmed_hashes]

