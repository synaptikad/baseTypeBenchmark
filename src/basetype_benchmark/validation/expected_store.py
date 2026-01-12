"""Expected Answer storage and retrieval.

Loads expected answers generated during dataset creation.

Structure:
    data/generated/{profile}/
    ├── nodes.parquet
    ├── edges.parquet
    ├── timeseries.parquet
    ├── queries_params.yaml
    └── expected_answers/
        ├── metadata.json
        ├── Q1.json
        ├── Q2.json
        └── ...Q23.json
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import ExpectedAnswer, SemanticType


class ExpectedAnswerStore:
    """Store and load Expected Answers.

    Loads from dataset's expected_answers/ directory.
    """

    def __init__(self, store_dir: Path):
        """Initialize store.

        Args:
            store_dir: Dataset directory containing expected_answers/
        """
        self.store_dir = Path(store_dir)

        # Check for expected_answers subdirectory
        expected_answers_dir = self.store_dir / "expected_answers"
        if expected_answers_dir.exists():
            self.answers_dir = expected_answers_dir
        else:
            # Assume store_dir IS the expected_answers directory
            self.answers_dir = self.store_dir

        self._metadata: dict[str, Any] = {}
        self._answers: dict[str, ExpectedAnswer] = {}
        self._params_file: Path | None = None

        # Check for queries_params.yaml in dataset directory
        params_path = self.store_dir / "queries_params.yaml"
        if params_path.exists():
            self._params_file = params_path

    def save(
        self,
        answers: dict[str, ExpectedAnswer],
        parquet_dir: Path,
        params: dict[str, Any],
    ) -> None:
        """Save Expected Answers to store.

        Args:
            answers: Dict mapping query_id to ExpectedAnswer
            parquet_dir: Source Parquet directory
            params: Parameters used for generation
        """
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.answers_dir.mkdir(exist_ok=True)

        # Compute Parquet checksums
        checksums = self._compute_parquet_checksums(parquet_dir)

        # Save metadata
        metadata = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source_dir": str(parquet_dir),
            "parquet_checksums": checksums,
            "parameters": params,
            "query_count": len(answers),
            "queries": list(answers.keys()),
        }

        metadata_path = self.store_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)

        # Save each answer
        for query_id, answer in answers.items():
            answer_path = self.answers_dir / f"{query_id}.json"
            with open(answer_path, "w", encoding="utf-8") as f:
                json.dump(answer.to_dict(), f, indent=2, default=str)

        self._metadata = metadata
        self._answers = answers

    def load(self) -> dict[str, ExpectedAnswer]:
        """Load Expected Answers from store.

        Returns:
            Dict mapping query_id to ExpectedAnswer
        """
        if not self.store_dir.exists():
            raise FileNotFoundError(f"Expected answers store not found: {self.store_dir}")

        # Load metadata
        metadata_path = self.store_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)

        # Load answers
        self._answers = {}
        if self.answers_dir.exists():
            for answer_file in self.answers_dir.glob("Q*.json"):
                with open(answer_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    query_id = data["query_id"]
                    self._answers[query_id] = ExpectedAnswer.from_dict(data)

        return self._answers

    def get(self, query_id: str) -> ExpectedAnswer | None:
        """Get Expected Answer for a query.

        Args:
            query_id: Query ID (Q1, Q2, etc.)

        Returns:
            ExpectedAnswer or None if not found
        """
        if not self._answers:
            self.load()
        return self._answers.get(query_id)

    def get_all(self) -> dict[str, ExpectedAnswer]:
        """Get all Expected Answers.

        Returns:
            Dict mapping query_id to ExpectedAnswer
        """
        if not self._answers:
            self.load()
        return self._answers

    def get_metadata(self) -> dict[str, Any]:
        """Get store metadata.

        Returns:
            Metadata dict with source info and checksums
        """
        if not self._metadata:
            metadata_path = self.store_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
        return self._metadata

    def get_parameters(self) -> dict[str, Any]:
        """Get global parameters used for generation.

        First tries queries_params.yaml (dataset-embedded),
        then falls back to metadata.json parameters.

        Returns:
            Parameters dict
        """
        # Try queries_params.yaml first (more complete)
        if self._params_file and self._params_file.exists():
            import yaml
            with open(self._params_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("parameters", {})

        # Fallback to metadata
        return self.get_metadata().get("parameters", {})

    def get_query_parameters(self, query_id: str) -> dict[str, Any]:
        """Get parameters for a specific query.

        Uses the parameters embedded in the expected answer itself,
        which is the correct approach for validation.

        Args:
            query_id: Query ID (Q1, Q2, etc.)

        Returns:
            Parameters dict for this specific query
        """
        answer = self.get(query_id)
        if answer and answer.parameters:
            return answer.parameters
        # Fallback to global parameters
        return self.get_parameters()

    def verify_source(self, parquet_dir: Path) -> bool:
        """Verify that Parquet source matches stored checksums.

        Args:
            parquet_dir: Parquet directory to verify

        Returns:
            True if checksums match
        """
        stored_checksums = self.get_metadata().get("parquet_checksums", {})
        current_checksums = self._compute_parquet_checksums(parquet_dir)

        for filename, checksum in stored_checksums.items():
            if current_checksums.get(filename) != checksum:
                return False

        return True

    def _compute_parquet_checksums(
        self,
        parquet_dir: Path,
    ) -> dict[str, str]:
        """Compute MD5 checksums of Parquet files.

        Args:
            parquet_dir: Directory containing Parquet files

        Returns:
            Dict mapping filename to MD5 checksum
        """
        checksums = {}
        parquet_dir = Path(parquet_dir)

        for filename in ["nodes.parquet", "edges.parquet", "timeseries.parquet"]:
            filepath = parquet_dir / filename
            if filepath.exists():
                checksums[filename] = self._md5_file(filepath)

        return checksums

    def _md5_file(self, filepath: Path) -> str:
        """Compute MD5 of a file.

        Args:
            filepath: Path to file

        Returns:
            MD5 hex digest
        """
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def exists(self) -> bool:
        """Check if store exists and has answers.

        Returns:
            True if store exists with at least one answer
        """
        if not self.store_dir.exists():
            return False
        if not self.answers_dir.exists():
            return False
        return len(list(self.answers_dir.glob("Q*.json"))) > 0

    def __contains__(self, query_id: str) -> bool:
        """Check if query_id is in store."""
        if not self._answers:
            self.load()
        return query_id in self._answers

    def __len__(self) -> int:
        """Number of Expected Answers in store."""
        if not self._answers:
            self.load()
        return len(self._answers)
