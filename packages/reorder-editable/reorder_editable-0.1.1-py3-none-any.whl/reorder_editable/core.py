"""
Core functionality, reads/writes to the editable and checks if order matches what the user specifies
"""

import os
import site
from typing import Optional, List, Tuple


class ReorderEditableError(FileNotFoundError):
    """ReorderEditable related errors"""

    pass


class Editable:
    """
    Encapsulates all possible interaction with the easy-install.pth file
    """

    def __init__(self, *, location: Optional[str], use_user_site: bool = True) -> None:
        """
        can optionally pass a location, to prevent the locate_editable editable call
        """
        if location is None:
            found_editable = self.__class__.locate_editable(use_user_site=use_user_site)
            if found_editable is not None:
                self.location = found_editable
            else:
                raise ReorderEditableError("Could not locate easy-install.pth")
        else:
            self.location = location

        assert os.path.exists(
            self.location
        ), f"The easy-install.pth file at '{self.location}' doesn't exist"
        self.lines: List[str] = self.read_lines()

    def read_lines(self) -> List[str]:
        """
        Read lines from the editable path file

        splitlines removes newlines from the end of each line
        """
        with open(self.location, "r") as src:
            self.lines = src.read().splitlines()
        return self.lines

    def write_lines(self, new_lines: List[str]) -> None:
        """
        Write lines back to the editable path file

        new_lines is a list of absolute paths, so for the format of
        the file to be the same, add newlines on each write
        """
        with open(self.location, "w") as target:
            for line in new_lines:
                target.write(f"{line}\n")

    def assert_ordered(self, expected: List[str]) -> None:
        """
        returns None on success, an Error if the file is not ordered correctly given 'expected'

        expected should be a list of absolute paths, in the order you expect to see
        them in the easy-install.pth
        """
        # iterated through all the items in the easy-install.pth file
        # but 'i' didn't reach the end of the list of expected items
        left = self.find_unordered(expected)
        if len(left) > 0:
            raise ReorderEditableError(
                f"Reached the end of the easy-install.pth, but did not encounter '{left}' in the correct order"
            )

    def find_unordered(self, expected: List[str]) -> List[str]:
        """
        Given a list of absolute paths in an expected order, compares that against
        the read order from the easy-install.pth file

        Returns any items not found in the correct order by the
        time it reaches the end of the easy-install.pth
        """
        return self.__class__.find_unordered_pure(self.lines, expected)

    @staticmethod
    def find_unordered_pure(lines: List[str], expected: List[str]) -> List[str]:
        """
        Pure function encapsulating all the logic for find_unordered
        """

        if len(expected) == 0:
            return expected
        i = 0  # current index of the expected items
        for path in lines:
            # use os.stat instead?
            if path == expected[i]:
                i += 1
                if len(expected) == i:
                    break

        return expected[i:]

    def reorder(self, expected: List[str]) -> bool:
        """
        If needed, reorder the easy-install.pth

        If the user specifies an item which doesn't exist in the
        easy-install.pth, this throws an error, since it has
        no way to determine where that value should go

        Return value is True if the file was edited, False
        if it didn't need to be edited.
        """
        do_reorder, new_lines = self.__class__.reorder_pure(self.lines, expected)
        if do_reorder is False:
            return False
        # write new_lines to file
        self.write_lines(new_lines)
        return True

    @classmethod
    def reorder_pure(
        cls, lines: List[str], expected: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Pure function encapsulating all the logic for reordering
        Returns (whether or not to edit the file, resulting changes)
        """
        unordered: List[str] = cls.find_unordered_pure(lines, expected)
        # everything is ordered right, dont need to reorder anything!
        if len(unordered) == 0:
            return False, lines

        # check that expected is a subset of lines
        expected_set = set(expected)
        lines_set = set(lines)
        if not expected_set.issubset(lines_set):
            raise ReorderEditableError(
                f"Provided one or more value(s) which don't appear in the easy-install.pth: {expected_set - lines_set}"
            )

        result: List[str] = []

        # if an item isn't mentioned in expected, leave it in the same
        # order -- extract all items not mentioned
        for path in lines:
            if path not in expected_set:
                result.append(path)

        # add anything in expected, in the order the user specified
        for path in expected:
            assert path in lines_set
            result.append(path)

        # sanity check
        assert len(result) == len(lines)

        return True, result

    @staticmethod
    def locate_editable(*, use_user_site: bool) -> Optional[str]:
        """
        try to find an editable install path in the user site-packages
        """
        if use_user_site:
            site_packages_dir = site.getusersitepackages()
        else:
            system_site_packages_dirs = site.getsitepackages()
            if len(system_site_packages_dirs) != 1:
                raise ReorderEditableError(
                    f'Expected exactly one package in system site, got: {system_site_packages_dirs}'
                )
            site_packages_dir = system_site_packages_dirs[0]

        editable_pth = os.path.join(site_packages_dir, "easy-install.pth")
        if not os.path.exists(editable_pth):
            return None
        return editable_pth
