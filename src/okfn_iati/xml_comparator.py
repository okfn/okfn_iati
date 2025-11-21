"""
IATI XML Comparator - Compare two IATI XML files and identify differences.

This module provides utilities to compare IATI XML files and distinguish between
relevant and non-relevant differences.
"""

import xml.etree.ElementTree as ET
import html
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DifferenceType(Enum):
    """Types of differences found in XML comparison."""
    MISSING_ELEMENT = "missing_element"
    EXTRA_ELEMENT = "extra_element"
    ATTRIBUTE_VALUE = "attribute_value"
    ATTRIBUTE_MISSING = "attribute_missing"
    ATTRIBUTE_EXTRA = "attribute_extra"
    TEXT_VALUE = "text_value"
    ELEMENT_COUNT = "element_count"
    ELEMENT_ORDER = "element_order"


@dataclass
class XmlDifference:
    """Represents a difference between two XML elements."""
    diff_type: DifferenceType
    path: str
    expected: Optional[str]
    actual: Optional[str]
    is_relevant: bool = True
    message: str = ""


class IatiXmlComparator:
    """Compare two IATI XML files and identify differences."""

    # Attributes that should be ignored in comparison (order-independent or auto-generated)
    IGNORE_ATTRIBUTES = {
        'generated-datetime',  # Auto-generated timestamp
        'last-updated-datetime'  # May vary
    }

    # Elements where order doesn't matter (can appear in any order)
    ORDER_INDEPENDENT_ELEMENTS = {
        'participating-org',
        'sector',
        'recipient-country',
        'recipient-region',
        'transaction',
        'budget',
        'location',
        'document-link',
        'result',
        'activity-date'
    }

    # Elements where text content whitespace variations are acceptable
    WHITESPACE_FLEXIBLE_ELEMENTS = {
        'narrative',
        'description',
        'title'
    }

    # Known custom namespaces (organization-specific extensions)
    CUSTOM_NAMESPACES = {
        'https://explorer.usaid.gov',  # USAID custom namespace
        '{https://explorer.usaid.gov}',  # With brackets
    }

    def __init__(
        self,
        ignore_element_order: bool = True,
        ignore_whitespace: bool = True,
        ignore_empty_attributes: bool = True
    ):
        """
        Initialize the comparator.

        Args:
            ignore_element_order: If True, ignore order of certain elements
            ignore_whitespace: If True, normalize whitespace in text content
            ignore_empty_attributes: If True, treat missing and empty attributes as equivalent
        """
        self.ignore_element_order = ignore_element_order
        self.ignore_whitespace = ignore_whitespace
        self.ignore_empty_attributes = ignore_empty_attributes
        self.differences: List[XmlDifference] = []

    def compare_files(
        self,
        file1: str,
        file2: str
    ) -> Tuple[bool, List[XmlDifference]]:
        """
        Compare two IATI XML files.

        Args:
            file1: Path to first XML file
            file2: Path to second XML file

        Returns:
            Tuple of (files_are_equivalent, list_of_differences)
        """
        self.differences = []

        try:
            tree1 = ET.parse(file1)
            tree2 = ET.parse(file2)

            root1 = tree1.getroot()
            root2 = tree2.getroot()

            self._compare_elements(root1, root2, "iati-activities")

            # Check if there are any relevant differences
            relevant_diffs = [d for d in self.differences if d.is_relevant]
            are_equivalent = len(relevant_diffs) == 0

            return are_equivalent, self.differences

        except Exception as e:
            diff = XmlDifference(
                diff_type=DifferenceType.MISSING_ELEMENT,
                path="/",
                expected=None,
                actual=None,
                is_relevant=True,
                message=f"Error comparing files: {e}"
            )
            return False, [diff]

    def _normalize_text(self, text: Optional[str]) -> str:
        """Normalize text content for comparison."""
        if text is None:
            return ""

        # Unescape HTML entities to handle double-escaped content
        # e.g. "&#xE1;" vs "á" should be treated as equal
        text = html.unescape(text)

        if self.ignore_whitespace:
            return " ".join(text.split())
        return text

    def _normalize_attribute_value(self, value: Optional[str]) -> str:
        """Normalize attribute value for comparison."""
        if value is None:
            return ""
        if self.ignore_empty_attributes and value.strip() == "":
            return ""
        return value.strip()

    def _should_ignore_attribute(self, attr_name: str) -> bool:
        """Check if attribute should be ignored in comparison."""
        return attr_name in self.IGNORE_ATTRIBUTES

    def _get_element_key(self, elem: ET.Element) -> str:
        """Get a unique key for an element for matching purposes."""
        tag = elem.tag

        # Use ref attribute if available
        if 'ref' in elem.attrib:
            return f"{tag}[@ref='{elem.attrib['ref']}']"

        # Use type attribute for activity-date
        if tag == 'activity-date' and 'type' in elem.attrib:
            return f"{tag}[@type='{elem.attrib['type']}']"

        # Use role attribute for participating-org
        if tag == 'participating-org' and 'role' in elem.attrib:
            return f"{tag}[@role='{elem.attrib['role']}']"

        # Use code attribute for sectors
        if tag == 'sector' and 'code' in elem.attrib:
            return f"{tag}[@code='{elem.attrib['code']}']"

        # Use type attribute for transaction-type
        if tag == 'transaction-type' and 'code' in elem.attrib:
            return f"{tag}[@code='{elem.attrib['code']}']"

        # Default: just use tag name
        return tag

    def _compare_elements(
        self,
        elem1: ET.Element,
        elem2: ET.Element,
        path: str
    ) -> None:
        """Recursively compare two XML elements."""

        # Compare attributes
        self._compare_attributes(elem1, elem2, path)

        # Compare text content
        self._compare_text(elem1, elem2, path)

        # Compare child elements
        self._compare_children(elem1, elem2, path)

    def _compare_attributes(
        self,
        elem1: ET.Element,
        elem2: ET.Element,
        path: str
    ) -> None:
        """Compare attributes of two elements."""
        attrs1 = {k: v for k, v in elem1.attrib.items() if not self._should_ignore_attribute(k)}
        attrs2 = {k: v for k, v in elem2.attrib.items() if not self._should_ignore_attribute(k)}

        for attr in attrs1:
            val1 = self._normalize_attribute_value(attrs1[attr])
            val2 = self._normalize_attribute_value(attrs2.get(attr))

            # --- HUMANITARIAN BOOLEAN DIFF LOGIC ---
            if attr == "humanitarian":
                # Normalize to boolean for comparison
                def _boolish(v):
                    v = v.strip().lower()
                    if v in ("true", "1"):
                        return True
                    if v in ("false", "0"):
                        return False
                    return None
                b1 = _boolish(val1)
                b2 = _boolish(val2)
                if b1 == b2:
                    # Mark as non-relevant if only lexical diff
                    if val1 != val2:
                        self.differences.append(XmlDifference(
                            diff_type=DifferenceType.ATTRIBUTE_VALUE,
                            path=f"{path}/@{attr}",
                            expected=val1,
                            actual=val2,
                            is_relevant=False,
                            message="Humanitarian attribute lexical difference (true/1 or false/0, not relevant)"
                        ))
                    continue  # Do not report as relevant diff

            if attr not in attrs2:
                if val1:  # Only report if the value is not empty
                    self.differences.append(XmlDifference(
                        diff_type=DifferenceType.ATTRIBUTE_MISSING,
                        path=f"{path}/@{attr}",
                        expected=val1,
                        actual=None,
                        is_relevant=True,
                        message=f"Attribute '{attr}' missing in second file"
                    ))
            elif val1 != val2:
                self.differences.append(XmlDifference(
                    diff_type=DifferenceType.ATTRIBUTE_VALUE,
                    path=f"{path}/@{attr}",
                    expected=val1,
                    actual=val2,
                    is_relevant=True,
                    message=f"Attribute '{attr}' value differs"
                ))

        # Check for extra attributes
        for attr in attrs2:
            if attr not in attrs1:
                val2 = self._normalize_attribute_value(attrs2[attr])
                if val2:  # Only report if the value is not empty
                    self.differences.append(XmlDifference(
                        diff_type=DifferenceType.ATTRIBUTE_EXTRA,
                        path=f"{path}/@{attr}",
                        expected=None,
                        actual=val2,
                        is_relevant=True,
                        message=f"Extra attribute '{attr}' in second file"
                    ))

    def _compare_text(
        self,
        elem1: ET.Element,
        elem2: ET.Element,
        path: str
    ) -> None:
        """Compare text content of two elements."""
        text1 = self._normalize_text(elem1.text)
        text2 = self._normalize_text(elem2.text)

        if text1 != text2:
            # Check if it's just a numeric formatting difference (e.g., "36425.00" vs "36425.0")
            is_numeric_formatting_diff = self._is_numeric_formatting_difference(text1, text2)

            is_relevant = elem1.tag not in self.WHITESPACE_FLEXIBLE_ELEMENTS or text1.strip() != text2.strip()

            # Numeric formatting differences are non-relevant
            if is_numeric_formatting_diff:
                is_relevant = False

            self.differences.append(XmlDifference(
                diff_type=DifferenceType.TEXT_VALUE,
                path=path,
                expected=text1,
                actual=text2,
                is_relevant=is_relevant,
                message="Text content differs" if is_relevant else "Numeric formatting differs (not relevant)"
            ))

    def _is_numeric_formatting_difference(self, text1: str, text2: str) -> bool:
        """Check if two strings represent the same number with different formatting."""
        try:
            # Try to parse both as floats
            num1 = float(text1)
            num2 = float(text2)
            # If they're equal as numbers, it's just formatting
            return num1 == num2
        except (ValueError, TypeError):
            # Not numeric values
            return False

    def _is_custom_namespace_element(self, elem: ET.Element) -> bool:
        """Check if element is from a custom namespace."""
        tag = elem.tag

        # Check if tag contains a namespace
        if '{' in tag:
            # Extract namespace
            namespace = tag.split('}')[0] + '}'
            return namespace in self.CUSTOM_NAMESPACES

        return False

    def _compare_children(
        self,
        elem1: ET.Element,
        elem2: ET.Element,
        path: str
    ) -> None:
        """Compare child elements of two elements."""
        children1 = list(elem1)
        children2 = list(elem2)

        # Separate standard and custom namespace children
        standard_children1 = [c for c in children1 if not self._is_custom_namespace_element(c)]
        standard_children2 = [c for c in children2 if not self._is_custom_namespace_element(c)]

        custom_children1 = [c for c in children1 if self._is_custom_namespace_element(c)]
        custom_children2 = [c for c in children2 if self._is_custom_namespace_element(c)]

        # Report missing custom elements as non-relevant (warning only)
        if custom_children1 and not custom_children2:
            for custom_elem in custom_children1:
                self.differences.append(XmlDifference(
                    diff_type=DifferenceType.MISSING_ELEMENT,
                    path=f"{path}/{custom_elem.tag}",
                    expected="present",
                    actual="missing",
                    is_relevant=False,  # Not relevant - just a warning
                    message=f"Custom namespace element '{custom_elem.tag}' not preserved (CSV conversion limitation)"
                ))

        # Group standard children by tag
        children1_by_tag = {}
        for child in standard_children1:
            tag = child.tag
            if tag not in children1_by_tag:
                children1_by_tag[tag] = []
            children1_by_tag[tag].append(child)

        children2_by_tag = {}
        for child in standard_children2:
            tag = child.tag
            if tag not in children2_by_tag:
                children2_by_tag[tag] = []
            children2_by_tag[tag].append(child)

        # Compare each tag group
        all_tags = set(children1_by_tag.keys()) | set(children2_by_tag.keys())

        for tag in all_tags:
            children1_list = children1_by_tag.get(tag, [])
            children2_list = children2_by_tag.get(tag, [])

            # If the tag exist but it's empty (like <website/>), we should not count it
            children1_list = [c for c in children1_list if c.text or list(c)]
            children2_list = [c for c in children2_list if c.text or list(c)]

            if len(children1_list) != len(children2_list):
                self.differences.append(XmlDifference(
                    diff_type=DifferenceType.ELEMENT_COUNT,
                    path=f"{path}/{tag}",
                    expected=str(len(children1_list)),
                    actual=str(len(children2_list)),
                    is_relevant=True,
                    message=f"Different number of '{tag}' elements"
                ))
                # Continue to compare what we can

            # Match elements by key
            if self.ignore_element_order and tag in self.ORDER_INDEPENDENT_ELEMENTS:
                # Match by key
                matched_pairs = self._match_elements_by_key(children1_list, children2_list)

                for child1, child2 in matched_pairs:
                    child_path = f"{path}/{self._get_element_key(child1)}"
                    self._compare_elements(child1, child2, child_path)
            else:
                # Compare in order
                for i, (child1, child2) in enumerate(zip(children1_list, children2_list)):
                    child_path = f"{path}/{tag}[{i+1}]"
                    self._compare_elements(child1, child2, child_path)

    def _match_elements_by_key(
        self,
        elements1: List[ET.Element],
        elements2: List[ET.Element]
    ) -> List[Tuple[ET.Element, ET.Element]]:
        """Match elements from two lists by their keys."""
        matched = []

        # Create lookup for elements2
        elements2_dict = {}
        for elem in elements2:
            key = self._get_element_key(elem)
            if key not in elements2_dict:
                elements2_dict[key] = []
            elements2_dict[key].append(elem)

        # Match elements1 to elements2
        for elem1 in elements1:
            key = self._get_element_key(elem1)
            if key in elements2_dict and elements2_dict[key]:
                elem2 = elements2_dict[key].pop(0)
                matched.append((elem1, elem2))

        return matched

    def format_differences(self, differences: List[XmlDifference], show_non_relevant: bool = False) -> str:
        """
        Format differences as a readable string.

        Args:
            differences: List of differences to format
            show_non_relevant: If True, include non-relevant differences

        Returns:
            Formatted string
        """
        relevant_diffs = [d for d in differences if d.is_relevant]
        non_relevant_diffs = [d for d in differences if not d.is_relevant]

        output = []

        # Show relevant differences (errors)
        if relevant_diffs:
            output.append(f"Found {len(relevant_diffs)} RELEVANT difference(s) (ERRORS):\n")
            for i, diff in enumerate(relevant_diffs, 1):
                output.append(f"{i}. {diff.message}")
                output.append(f"   Type: {diff.diff_type.value}")
                output.append(f"   Path: {diff.path}")
                if diff.expected is not None:
                    output.append(f"   Expected: {diff.expected}")
                if diff.actual is not None:
                    output.append(f"   Actual: {diff.actual}")
                output.append("")

        # Show non-relevant differences (warnings) if requested
        if show_non_relevant and non_relevant_diffs:
            output.append(f"\nFound {len(non_relevant_diffs)} NON-RELEVANT difference(s) (WARNINGS):\n")
            for i, diff in enumerate(non_relevant_diffs, 1):
                output.append(f"{i}. ⚠️  {diff.message}")
                output.append(f"   Type: {diff.diff_type.value}")
                output.append(f"   Path: {diff.path}")
                if diff.expected is not None:
                    output.append(f"   Expected: {diff.expected}")
                if diff.actual is not None:
                    output.append(f"   Actual: {diff.actual}")
                output.append("")

        if not output:
            return "No differences found."

        return "\n".join(output)
