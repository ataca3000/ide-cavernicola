"""
IDC Core - Citable Memory Vault
Selective memory persistence engine:
- Persists 'Recuerdos Lógicos Citables' (Immutable, verifiable empirical facts with SHA256 proof).
- Maintains 'Recuerdos Hipotéticos' (Volatile counterfactuals and sandbox inferences).
Ensures zero memory bloat by only cementing knowledge that survives empirical verification.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from contracts.memory_library import CitableLogicalMemory, HypotheticalMemory


class CitableMemoryVault:
    """
    Coordinates selective retention into citable vs hypothetical libraries.
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = str(Path(__file__).parent.parent / "memory" / "vault")
        self.vault_dir = Path(base_dir)
        self.citable_dir = self.vault_dir / "citable_logical"
        self.hypothetical_dir = self.vault_dir / "hypothetical"

        self.citable_dir.mkdir(parents=True, exist_ok=True)
        self.hypothetical_dir.mkdir(parents=True, exist_ok=True)

        self._citable_cache: Dict[str, CitableLogicalMemory] = {}
        self._hypothetical_cache: Dict[str, HypotheticalMemory] = {}

        self._load_citable_indices()

    def _load_citable_indices(self) -> None:
        """Pre-warms the citable memory index into RAM for O(1) retrieval."""
        for path in self.citable_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    mem = CitableLogicalMemory(**data)
                    self._citable_cache[mem.id] = mem
            except Exception:
                pass

    def record_hypothetical(
        self,
        conjecture: str,
        derived_from_rules: Optional[List[str]] = None,
        mutant_parameters: Optional[Dict] = None,
        plausibility_score: float = 0.5,
    ) -> HypotheticalMemory:
        """Stores a volatile 'What-if' hypothesis in memory for simulation or testing."""
        hypo = HypotheticalMemory(
            conjecture=conjecture,
            derived_from_rules=derived_from_rules or [],
            mutant_parameters=mutant_parameters or {},
            plausibility_score=plausibility_score,
        )
        self._hypothetical_cache[hypo.id] = hypo
        return hypo

    def promote_to_citable(
        self,
        hypothetical_id: str,
        claim: str,
        domain: str,
        citation_source: str,
        empirical_log: str,
        conditions: Optional[List[str]] = None,
        axioms: Optional[List[str]] = None,
    ) -> CitableLogicalMemory:
        """
        Promotes an empirically verified hypothesis into an immutable Citable Logical Memory.
        Computes a cryptographic proof hash from the empirical verification log.
        """
        proof_hash = hashlib.sha256(empirical_log.encode("utf-8")).hexdigest()

        citable = CitableLogicalMemory(
            claim=claim,
            domain=domain,
            citation_source=citation_source,
            proof_hash=proof_hash,
            conditions=conditions or [],
            axioms=axioms or [],
            empirical_confirmations=1,
        )

        # Update cache & persist to disk
        self._citable_cache[citable.id] = citable
        file_path = self.citable_dir / f"{citable.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(citable.model_dump_json(indent=2))

        # Mark hypothetical as promoted if it existed
        if hypothetical_id in self._hypothetical_cache:
            h = self._hypothetical_cache[hypothetical_id]
            h.promoted_to_citable = True
            h.citable_memory_id = citable.id

        return citable

    def save_direct_citable(self, memory: CitableLogicalMemory) -> None:
        """Saves a pre-constructed citable logical memory."""
        self._citable_cache[memory.id] = memory
        file_path = self.citable_dir / f"{memory.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(memory.model_dump_json(indent=2))

    def query_citable_by_domain(self, domain: str) -> List[CitableLogicalMemory]:
        """Returns verified citable memories applicable to a given domain."""
        return [m for m in self._citable_cache.values() if m.domain.lower() == domain.lower()]

    def get_citable(self, memory_id: str) -> Optional[CitableLogicalMemory]:
        """Retrieves a verified citable memory by its unique ID."""
        return self._citable_cache.get(memory_id)

    def get_hypothetical(self, hypo_id: str) -> Optional[HypotheticalMemory]:
        """Retrieves a hypothetical memory by its ID."""
        return self._hypothetical_cache.get(hypo_id)

    def cite_memory(self, memory_id: str) -> Optional[str]:
        """Increments reuse counter and returns formal citation string."""
        mem = self._citable_cache.get(memory_id)
        if mem:
            mem.reusable_count += 1
            return f"[CitableMemory id={mem.id} claim='{mem.claim}' proof={mem.proof_hash[:12]} source='{mem.citation_source}']"
        return None

    @property
    def total_citable_count(self) -> int:
        return len(self._citable_cache)

    @property
    def total_hypothetical_count(self) -> int:
        return len(self._hypothetical_cache)
