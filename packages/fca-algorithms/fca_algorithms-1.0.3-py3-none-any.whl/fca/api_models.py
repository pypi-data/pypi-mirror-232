# -*- coding: utf-8 -*-
"""Interface with the basic classes to be used in the entire `fca` module."""

from typing import List
from collections import deque, UserString
from fca_algorithms_cpp import LatticeCpp, ContextCpp, ConceptCpp

from .base_models import Context as Ctx, Concept
from .get_lattice import FCASolver, Inclose
from .utils.utils import to_subscript
from .plot.plot import plot_from_hasse


class RelationalAttribute(UserString):
    def __init__(self, p, relation=None, concepts=None):
        """
        :param p: the p18n operator or a string, in which case the relation and concepts are expected to be None.
                  This is mainly to maintain the idea of string[:2] in which another string is expected as a return.
        :param relation: the relation instance
        :param concepts: a list of tuples (lattice_id, concept_id, concept)
        """
        if isinstance(p, str):
            super().__init__(p)
        else:
            value = f'{p}{relation} : {self._concepts_subscripts(concepts)}'
            self.concepts = concepts
            super().__init__(value)

    def _concepts_subscripts(self, combination):
        return ",".join(
            [f'C{to_subscript(lattice_idx)}₋{to_subscript(c_idx)}' for lattice_idx, c_idx, _ in combination])


class Context(Ctx):
    """The representation of a formal context"""

    def __init__(self, O, A, I, solver: FCASolver = None):
        """
        Args:
            O (List[str]): list of object names
            A (List[str]): list of attribute names
            I (List[List[int]]) incidence matrix (`1` and `0` or `True` and `False` work)
            solver (FCASolver): the solver that should know how to calculate concepts.
        """
        super().__init__(O, A, I)

        if solver is None:
            solver = Inclose()

        self.solver = solver
        self.iteration = 0

        # for each relation, we know what are the attributes already added
        self._relational_attributes = {}

        # FIXME: The ideal would be to cache the last_lattice
        #        and also calculate them from the point they were already calculated
        #        * is that possible not to repeat calculations?
        #        * if not, can we bound the amount of calculations that ought to be repeated?
        self._last_lattice = None

    def get_concepts(self):
        """
        Returns:
            A List[:class:`Concept`]
        """
        return self.solver.get_concepts(self)

    def get_lattice(self):
        """
        Returns:
            A :class:`Lattice`"""
        hasse, concepts = self.solver.get_lattice(self)
        if self._last_lattice is None:
            self._last_lattice = Lattice(hasse, concepts)
        else:
            self._last_lattice = Lattice(hasse, concepts)
        return self._last_lattice

    def get_association_rules(self, **kwargs):
        """
        Keyword Args:
            min_support=0.5 (float): a float between 0 and 1
            min_confidence=1 (float): a float between 0 and 1
        Yields:
            association rules with
                - Base Item
                - Appended Item
                - Support
                - Confidence
                - Lift
            see (https://pypi.org/project/apyori/)
        """
        return self.solver.get_association_rules(self, **kwargs)

    def graduate(self, relation, p, lattices):
        """
        Applies graduation. Extends the formal context with more attributes
        with the relation `relation`, using the p18n operator, against the lattices `lattices` (a list of lattice, lattice_idx)
        """
        for combination in self._tuple_iterator(lattices, 0):
            key = RelationalAttribute(p, relation, combination)
            if key not in self._relational_attributes:
                self.A.append(key)
                self._relational_attributes[key] = len(
                    self.A) - 1  # adding the idx of the attribute

            attribute_idx = self._relational_attributes[key]
            have_to_add_column = attribute_idx > len(self.I[0]) - 1
            for o, relations in enumerate(self.I):
                has_attribute = p(
                    o, relation, [
                        concept for _, _, concept in combination])
                if have_to_add_column:
                    relations.append(has_attribute)
                else:
                    relations[attribute_idx] = has_attribute

        self.iteration += 1

    def _tuple_iterator(self, lattices, i):
        current_lattice_idx = lattices[i][0]
        current_lattice = lattices[i][1]
        if i == len(lattices) - 1:
            for c_idx, concept in enumerate(current_lattice.concepts):
                yield deque([(current_lattice_idx, c_idx, concept)])
        else:
            for c_idx, concept in enumerate(current_lattice.concepts):
                for combination in self._tuple_iterator(lattices, i + 1):
                    combination.appendleft(
                        (current_lattice_idx, c_idx, concept))
                    yield combination


class Lattice:
    """Representation of a lattice with all the concepts and the hasse diagram"""
    def __init__(self, hasse, concepts, from_iteration=None):
        self.hasse = hasse
        self.concepts = concepts
        self.ctx = self.concepts[-1].context

        self._inverted_hasse = None

    def isomorph(self, other_lattice):
        """
        This method needs the two lattices to have the concepts ordered in the same way, othetwise it'll fail
        - Complexity: `O(|self.concepts|), \\omega(1)`
        """
        if len(self.concepts) != len(other_lattice.concepts):
            return False

        for i, concept in enumerate(self.concepts):
            if len(concept.O) != len(other_lattice.concepts[i].O) or \
               len(concept.A) != len(other_lattice.concepts[i].A):
                return False
        return True

    @property
    def inverted_hasse(self):
        """The inverse of the hasse digraph"""
        if self._inverted_hasse is None:
            self._calculate_inverted_hasse()
        return self._inverted_hasse

    def plot(self, **kwargs):
        """
        Keyword Args:
            show_plot (bool): Whether to show the plot or not.
            save_plot (str): The path where to save the plot. If None, the plot wont be saved.
            ax (Axes | List[Axes]): to reuse axes from another plot.
            fig (Figure): the figure where to draw the plot.
            print_latex (bool): Whether to print the latex code of the plot in the standard output
            instance is destructed.

        Returns:
            (fig, ax, diameter)
        """
        return plot_from_hasse(self.hasse, self.concepts, **kwargs)

    
    def __repr__(self):
        return str(self.concepts)


    def _calculate_inverted_hasse(self):
        inv_hasse = []
        for _ in range(len(self.hasse)):
            inv_hasse.append([])

        for i, neighbours in enumerate(self.hasse):
            for j in neighbours:
                inv_hasse[j].append(i)
        
        self._inverted_hasse = inv_hasse


class IncLattice:
    """Incremenal Lattice that can receive objects on the fly.

    Its purpose is to be able to receive objects and update only the minimal parts of it
    each update takes `O(|G|²|M||L|)` where L is the Lattice we have so far, and G are the objects so far.
    """

    def __init__(self, attributes : List[str]):
        """
        Args:
            attributes (List[str]): The list of attributes the Lattice will have.
        Example:
            .. code-block:: python
                
                L = IncLattice(['a', 'b', 'c'])
        """
        self.ctx = ContextCpp([], attributes, [])
        self._lat_cpp = LatticeCpp(self.ctx)
    
    def add_intent(self, object_name : str, intent : List[int]):
        """
        Args:
            object_name (str): the name of the object being added.
            intent (List[int]): The list of attribute indices the object has.

        Example:
            .. code-block:: python

                L.add_intent('o1', [1, 3, 6])
        """
        self._lat_cpp.add_intent(object_name, intent)
    
    def get_concept(self, i : int) -> ConceptCpp:
        """
        Args:
            i (int): index of the concept to be returned
        Returns:
            :class:`ConceptCpp` in `i`-th position
        """
        return self._lat_cpp.get_concept(i)

    def plot(self, **kwargs):
        """
        Keyword Args:
            show_plot (bool): Whether to show the plot or not.
            save_plot (str): The path where to save the plot. If None, the plot wont be saved.
            ax (Axes | List[Axes]): to reuse axes from another plot.
            fig (Figure): the figure where to draw the plot.
            print_latex (bool): Whether to print the latex code of the plot in the standard output
            instance is destructed.

        Returns:
            (fig, ax, diameter)
        """
        return plot_from_hasse(
            [t[1] for t in self._lat_cpp.graph],
            [Concept(self.ctx, t[0].X, t[0].Y) for t in self._lat_cpp.graph],
            amount_of_objects=len(self.ctx.G),
            **kwargs)
    
    def __repr__(self) -> str:
        return self._lat_cpp.__repr__()



# This is a variable later used for automatically generating the docs
__all__ = (
    'Context',
    'Lattice',
    'IncLattice',
)
