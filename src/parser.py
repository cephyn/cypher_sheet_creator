"""
Parser module for converting character sheet text files to structured data.
"""

import re
from typing import Dict, List, Any, Optional


class CharacterSheetParser:
    """Parses Cypher System character sheet text files."""

    def __init__(self, text: str):
        self.text = text
        self.lines = text.split("\n")
        self.data: Dict[str, Any] = {
            "header": {},
            "attributes": {},
            "special_abilities": [],
            "skills": [],
            "attacks": [],
            "cyphers": [],
            "equipment": [],
            "advancements": {},
            "background": {},
            "notes": {},
        }
        # Canonical section headers in parse order for boundary detection
        self._section_order: List[str] = [
            "Special Abilities",
            "Skills",
            "Attacks",
            "Cyphers",
            "Equipment",
            "Advancements",
            "Background",
            "Notes",
        ]

    def parse(self) -> Dict[str, Any]:
        """Parse the entire character sheet."""
        self._parse_header()
        self._parse_attributes()
        self._parse_special_abilities()
        self._parse_skills()
        self._parse_attacks()
        self._parse_cyphers()
        self._parse_equipment()
        self._parse_advancements()
        self._parse_background()
        self._parse_notes()
        return self.data

    def _parse_header(self):
        """Parse header information (name and descriptors)."""
        # The header may span multiple physical lines (wrapping). Collect the
        # contiguous non-empty lines from the top until we hit a horizontal
        # ruler (---) or an empty line and join them for robust parsing.
        if not self.lines:
            return

        header_lines: List[str] = []
        for line in self.lines:
            if not line.strip():
                break
            # Stop if we encounter a line that's just dashes (HR)
            if set(line.strip()) == {"-"}:
                break
            header_lines.append(line.strip())

        header_text = " ".join(header_lines).strip()
        if not header_text:
            return

        # Format examples we support:
        # "Name is a Weird Explorer who Crafts ... in a Historical world"
        # Allow multi-word names (including punctuation like slashes) and both
        # "is a" and "is an" forms. Be case-insensitive.
        match = re.match(
            r"^(.+?)\s+is\s+(?:a|an)\s+(.+?)(?:\s+in\s+(?:a|an)\s+(.+?))?$",
            header_text,
            flags=re.IGNORECASE,
        )

        if not match:
            return

        # Name may include slashes or multiple words; keep original casing
        name = match.group(1).strip()
        descriptors_text = match.group(2) or ""
        world = match.group(3) or "Standard"

        self.data["header"]["name"] = name
        self.data["header"]["world"] = world

        # Parse descriptors into type / focus / flavor by splitting on the
        # common separators 'who' and 'with'. Use case-insensitive split.
        parts = re.split(r"\s+who\s+|\s+with\s+", descriptors_text, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p and p.strip()]
        if len(parts) > 0:
            self.data["header"]["type"] = parts[0]
        if len(parts) > 1:
            self.data["header"]["focus"] = parts[1]
        if len(parts) > 2:
            self.data["header"]["flavor"] = parts[2]

    def _parse_attributes(self):
        """Parse Might, Speed, Intellect pools and related stats."""
        for i, line in enumerate(self.lines):
            if line.startswith("Might:"):
                self._extract_pool_line("Might", line)
            elif line.startswith("Speed:"):
                self._extract_pool_line("Speed", line)
            elif line.startswith("Intellect:"):
                self._extract_pool_line("Intellect", line)
            elif line.startswith("Initiative:"):
                match = re.search(r"Initiative:\s+(\w+)", line)
                if match:
                    self.data["attributes"]["initiative"] = match.group(1)
            elif line.startswith("Effort:"):
                match = re.search(r"Effort:\s+(\d+)", line)
                if match:
                    self.data["attributes"]["effort"] = int(match.group(1))
            elif line.startswith("Armor:"):
                match = re.search(r"Armor:\s+(\d+)", line)
                if match:
                    self.data["attributes"]["armor"] = int(match.group(1))
            elif line.startswith("Experience Points:"):
                match = re.search(r"Experience Points:\s+(\d+)", line)
                if match:
                    self.data["attributes"]["xp"] = int(match.group(1))
            elif line.startswith("Recovery Roll:"):
                match = re.search(r"Recovery Roll:\s+(.+)", line)
                if match:
                    self.data["attributes"]["recovery_roll"] = match.group(1)

    def _extract_pool_line(self, attr_name: str, line: str):
        """Extract pool, edge, and defense from attribute line."""
        match = re.search(r"Pool:\s+(\d+)\s+Edge:\s+(\d+)\s+Defense:\s+(\w+)", line)
        if match:
            self.data["attributes"][attr_name.lower()] = {
                "pool": int(match.group(1)),
                "edge": int(match.group(2)),
                "defense": match.group(3),
            }

    def _parse_section(self, section_name: str) -> Optional[int]:
        """Find the line number where a section starts."""
        section_header = f"{section_name}\n" if section_name != "Notes" else "Notes\n"
        for i, line in enumerate(self.lines):
            if line.strip() == section_name or (
                line.strip() == section_name and i + 1 < len(self.lines)
            ):
                return i
        return None

    def _get_section_content(
        self, start_marker: str, end_marker: Optional[str] = None
    ) -> List[str]:
        """Get content of a section from its header up to (but not including) the next section header.

        If end_marker is provided, stop at that explicit marker; otherwise stop at the
        next known section header in the canonical order.
        """
        # Find start line where the stripped text equals start_marker
        start_idx: Optional[int] = None
        for i, line in enumerate(self.lines):
            if line.strip().lower() == start_marker.strip().lower():
                start_idx = i + 1
                break

        if start_idx is None:
            return []

        # Optionally skip a horizontal rule line right after header
        if start_idx < len(self.lines) and self.lines[start_idx].strip().startswith(
            "---"
        ):
            start_idx += 1

        # Determine end index
        end_idx = len(self.lines)
        if end_marker:
            # Stop at explicit end marker occurrence
            for i in range(start_idx, len(self.lines)):
                if self.lines[i].strip().lower() == end_marker.strip().lower():
                    end_idx = i
                    break
        else:
            # Stop at the next known section header
            # Determine the sequence of section headers to consider after the current one
            lowered_order = [s.lower() for s in self._section_order]
            try:
                pos = lowered_order.index(start_marker.strip().lower())
            except ValueError:
                pos = -1
            next_headers = (
                set(lowered_order[pos + 1 :]) if pos != -1 else set(lowered_order)
            )

            for i in range(start_idx, len(self.lines)):
                s = self.lines[i].strip().lower()
                if s in next_headers:
                    end_idx = i
                    break

        # Return non-empty, rstripped lines within boundaries, skipping lone HRs
        content: List[str] = []
        for line in self.lines[start_idx:end_idx]:
            t = line.rstrip()
            if not t:
                continue
            # Skip lines made purely of dashes (section separators)
            if set(t) == {"-"}:
                continue
            content.append(t)
        return content

    def _looks_like_subsection_header(self, line: str) -> bool:
        """Heuristic: decide whether a non-indented line is a subsection header.

        Rules used:
        - Ignore pure HR lines.
        - Reject lines that end with typical sentence punctuation.
        - Reject lines that start with common sentence-leading words (you, this, the, a, an, they, your).
        - Prefer relatively short, title-like lines (few words).
        - Accept lines that are Title Case or short single words.
        """
        if not line:
            return False
        s = line.strip()
        if not s:
            return False
        # HR line
        if set(s) == {"-"}:
            return False
        # Sentence-like lines end with punctuation
        if s.endswith((".", "!", "?", ":")):
            return False
        lower = s.lower()
        # Reject obvious sentence starts
        for prefix in (
            "you ",
            "this ",
            "they ",
            "the ",
            "a ",
            "an ",
            "your ",
            "possible ",
            "sometimes ",
            "depending ",
        ):
            if lower.startswith(prefix):
                return False

        words = s.split()
        # If it's too long, it's probably body text wrapped across lines
        if len(words) > 8 or len(s) > 80:
            return False

        # If it's title-cased or a short single word, assume header
        if s == s.title() or len(words) <= 3:
            return True

        return False

    def _parse_special_abilities(self):
        """Parse the Special Abilities section."""
        content = self._get_section_content("Special Abilities")
        ability = None

        for line in content:
            # Start of a new ability: non-indented, non-HR line
            if line and not line.startswith(("\t", " ")) and line.strip():
                if ability:
                    self.data["special_abilities"].append(ability)
                ability = {"name": line.strip(), "description": []}
            elif ability and line.strip():
                ability["description"].append(line.strip())

        if ability:
            self.data["special_abilities"].append(ability)

    def _parse_skills(self):
        """Parse the Skills section."""
        content = self._get_section_content("Skills")
        skill = None

        for line in content:
            # Check for skill with level indicator like "Skill (Trained)" or "Skill (Inability)"
            match = re.match(r"(\w.+?)\s+\((\w+)\)\s*$", line.strip())
            if match:
                if skill:
                    self.data["skills"].append(skill)
                skill = {
                    "name": match.group(1),
                    "level": match.group(2),
                    "description": [],
                }
            elif (
                skill
                and line.strip()
                and not re.match(r"^[\w].+\s+\(\w+\)", line.strip())
            ):
                skill["description"].append(line.strip())

        if skill:
            self.data["skills"].append(skill)

    def _parse_attacks(self):
        """Parse the Attacks section."""
        content = self._get_section_content("Attacks")
        attack = None

        for line in content:
            # Attack names are short lines without leading whitespace
            if line and not line.startswith("\t") and line.strip():
                match = re.match(r"^([A-Za-z\s]+)$", line.strip())
                if match and len(line.strip()) < 50:
                    if attack:
                        self.data["attacks"].append(attack)
                    attack = {"name": line.strip(), "description": []}
                elif attack:
                    attack["description"].append(line.strip())
            elif attack and line.strip():
                attack["description"].append(line.strip())

        if attack:
            self.data["attacks"].append(attack)

    def _parse_cyphers(self):
        """Parse the Cyphers section."""
        content = self._get_section_content("Cyphers")
        cypher = None

        for line in content:
            # Cypher names: "Name (Level X, Type)"
            match = re.match(
                r"^([A-Za-z\s]+)\s+\(Level\s+(\d+),\s+(.+?)\)\s*$", line.strip()
            )
            if match:
                if cypher:
                    self.data["cyphers"].append(cypher)
                cypher = {
                    "name": match.group(1).strip(),
                    "level": int(match.group(2)),
                    "type": match.group(3),
                    "description": [],
                }
            elif cypher and line.strip():
                cypher["description"].append(line.strip())

        if cypher:
            self.data["cyphers"].append(cypher)

    def _parse_equipment(self):
        """Parse the Equipment section."""
        content = self._get_section_content("Equipment")
        for line in content:
            line = line.strip()
            if line.startswith("-"):
                self.data["equipment"].append(line[1:].strip())
            elif line and not line.startswith("Money:"):
                self.data["equipment"].append(line)

    def _parse_advancements(self):
        """Parse the Advancements section."""
        content = self._get_section_content("Advancements")
        for line in content:
            if "Tier:" in line:
                match = re.search(r"Tier:\s+(\d+)", line)
                if match:
                    self.data["advancements"]["tier"] = int(match.group(1))
            elif line.strip().startswith("["):
                self.data["advancements"].setdefault("choices", []).append(line.strip())

    def _parse_background(self):
        """Parse the Background section."""
        content = self._get_section_content("Background")
        current_subsection = None

        for line in content:
            # Treat as a subsection header only when the heuristic says so.
            if (
                line
                and not line.startswith("\t")
                and self._looks_like_subsection_header(line)
            ):
                current_subsection = line.strip()
                self.data["background"][current_subsection] = []
            elif current_subsection and line.strip():
                # Append wrapped paragraph lines to the current subsection body
                self.data["background"][current_subsection].append(line.strip())

    def _parse_notes(self):
        """Parse the Notes section."""
        content = self._get_section_content("Notes")
        current_subsection = None

        for line in content:
            if (
                line
                and not line.startswith("\t")
                and self._looks_like_subsection_header(line)
            ):
                current_subsection = line.strip()
                self.data["notes"][current_subsection] = []
            elif current_subsection and line.strip():
                self.data["notes"][current_subsection].append(line.strip())
